"""ToolRegistry + declarative tool specs (#4, #57).

Each Tool carries an input_schema (JSON Schema) used to expose MCP tools, plus
metadata (skill, providers, security) used by the router and docs.
"""
from __future__ import annotations

from .. import functions as F
from .base import Tool, ToolRegistry

_TMAP = {"str": "string", "int": "integer", "float": "number",
         "bool": "boolean", "array": "array", "object": "object"}


def _s(props, required=None):
    schema = {"type": "object", "properties": {}, "required": required or []}
    for k, v in props.items():
        t = v.pop("type", "string")
        schema["properties"][k] = {"type": _TMAP.get(t, t), **v}
    return schema


def _p(t, desc, **kw):
    return {"type": t, "description": desc, **kw}


def _specs():
    L = []
    A = lambda spec: L.append(spec)

    # ---------------- search ----------------
    A(("search_web", F.search_web, "Universal web search (auto providers).",
       _s({"query": _p("str", "search text"), "limit": _p("int", "max results", default=8),
           "providers": _p("array", "optional provider names", items={"type": "string"})},
          ["query"]), "web-search", ["search"], ["auto"]))
    A(("search_multi", F.search_multi, "Multi-provider general web search.",
       _s({"query": _p("str", "search text"), "limit": _p("int", "max results", default=6),
           "providers": _p("array", "optional providers", items={"type": "string"})},
          ["query"]), "web-search", ["search"], ["auto"]))
    A(("search_operator", F.search_operator, "Operator-aware search.",
       _s({"expression": _p("str", "query with operators"),
           "kind": _p("str", "source kind", enum=["web", "code", "paper", "news", "community", "gov"]),
           "limit": _p("int", "max results", default=8)}, ["expression"]),
       "search-operators", ["search"], ["auto"]))
    # ------------- query engine -------------
    A(("build_search_query", F.build_search_query, "Build a family of queries.",
       _s({"topic": _p("str", "topic"), "family": _p("str", "query family",
           enum=["discovery", "exact", "technical", "implementation", "source_specific",
                 "verification", "contradiction", "historical", "current", "alternative"]),
           "n": _p("int", "count", default=4), "target": _p("str", "target type"),
           "site": _p("str", "site"), "filetype": _p("str", "filetype")}, ["topic"]),
       "query-builder", ["query"], ["internal"]))
    A(("validate_search_query", F.validate_search_query, "Validate a query.",
       _s({"query": _p("str", "query")}, ["query"]), "query-builder", ["query"], ["internal"]))
    A(("expand_query", F.expand_query, "Expand a topic into variants.",
       _s({"topic": _p("str", "topic"), "terms": _p("array", "extra terms", items={"type": "string"}),
           "n": _p("int", "count", default=6)}, ["topic"]), "query-expansion",
       ["query"], ["internal"]))
    A(("refine_query", F.refine_query, "Refine a query.",
       _s({"query": _p("str", "query"), "domain": _p("str", "domain"),
           "filetype": _p("str", "filetype"), "exact": _p("bool", "wrap in quotes"),
           "remove_terms": _p("array", "terms to drop", items={"type": "string"})},
          ["query"]), "query-refinement", ["query"], ["internal"]))
    A(("get_search_strategy", F.get_search_strategy, "Multi-family strategy.",
       _s({"topic": _p("str", "topic"), "target": _p("str", "target type")}, ["topic"]),
       "query-engine", ["query"], ["internal"]))
    # ------------- reader / crawler -------------
    A(("fetch_source", F.fetch_source, "Fetch & extract a page/document.",
       _s({"url": _p("str", "url")}, ["url"]), "web-reader", ["fetch"], ["auto"]))
    A(("extract_links", F.extract_links, "Outbound links of a page.",
       _s({"url": _p("str", "url"), "limit": _p("int", "max links", default=50)},
          ["url"]), "link-discovery", ["fetch"], ["auto"]))
    A(("crawl_web", F.crawl_web, "Bounded crawl from seed URLs.",
       _s({"seed": _p("str", "seed URL (or comma list)"), "topic": _p("str", "relevance topic"),
           "depth": _p("int", "depth", default=1), "max_pages": _p("int", "max pages", default=8),
           "same_domain": _p("bool", "stay on seed domain", default=True),
           "domains": _p("array", "allow domains", items={"type": "string"})}, ["seed"]),
       "web-crawler", ["crawl"], ["auto"]))
    # ------------- verticals -------------
    A(("search_github", F.search_github, "Search GitHub repositories/issues/code.",
       _s({"query": _p("str", "query"), "scope": _p("str",
           "what to search", enum=["repositories", "code", "issues", "repository"]),
           "limit": _p("int", "max results", default=8)}, ["query"]),
       "github-research", ["code"], ["github"]))
    A(("github_repository", F.github_repository, "Profile of one repository.",
       _s({"repo": _p("str", "owner/name")}, ["repo"]), "github-research", ["code"], ["github"]))
    A(("github_code_search", F.github_code_search, "Search source code on GitHub.",
       _s({"query": _p("str", "query"), "limit": _p("int", "max", default=8)}, ["query"]),
       "github-research", ["code"], ["github"]))
    A(("github_issues", F.github_issues, "Search issues/PRs/discussions.",
       _s({"query": _p("str", "query"), "limit": _p("int", "max", default=8)}, ["query"]),
       "github-research", ["community"], ["github"]))
    A(("github_releases", F.github_releases, "Releases of a repository.",
       _s({"repo": _p("str", "owner/name"), "limit": _p("int", "max", default=5)},
          ["repo"]), "github-research", ["community"], ["github"]))
    A(("search_academic", F.search_academic, "Search academic papers (arXiv/Crossref).",
       _s({"query": _p("str", "query"), "limit": _p("int", "max", default=8)}, ["query"]),
       "academic-research", ["paper"], ["arxiv", "crossref"]))
    A(("paper_research", F.paper_research, "Paper research on a topic.",
       _s({"query": _p("str", "query"), "limit": _p("int", "max", default=8)}, ["query"]),
       "academic-research", ["paper"], ["arxiv", "crossref"]))
    A(("literature_review", F.literature_review, "Structured literature sweep.",
       _s({"topic": _p("str", "topic"), "limit_per_source": _p("int", "max per query", default=6)},
          ["topic"]), "literature-review", ["paper"], ["arxiv", "crossref"]))
    A(("search_government", F.search_government, "Official/government search.",
       _s({"query": _p("str", "query"), "region": _p("str", "country code", default="in"),
           "limit": _p("int", "max", default=8)}, ["query"]), "government-research",
       ["gov"], ["web"]))
    A(("search_news", F.search_news, "News search.",
       _s({"query": _p("str", "query"), "limit": _p("int", "max", default=8),
           "region": _p("str", "region code", default="US")}, ["query"]),
       "news-research", ["news"], ["googlenews"]))
    A(("search_community", F.search_community, "Community search.",
       _s({"query": _p("str", "query"), "limit": _p("int", "max", default=8)}, ["query"]),
       "community-research", ["community"], ["hackernews", "github"]))
    # ------------- documents -------------
    A(("search_documents", F.search_documents, "Find documents (default PDF).",
       _s({"query": _p("str", "query"), "limit": _p("int", "max", default=8),
           "filetype": _p("str", "filetype", default="pdf")}, ["query"]),
       "document-research", ["search"], ["auto"]))
    A(("pdf_research", F.pdf_research, "Find PDF documents.",
       _s({"query": _p("str", "query"), "limit": _p("int", "max", default=8)}, ["query"]),
       "pdf-research", ["search"], ["auto"]))
    A(("spreadsheet_research", F.spreadsheet_research, "Find spreadsheets.",
       _s({"query": _p("str", "query"), "limit": _p("int", "max", default=6)}, ["query"]),
       "spreadsheet-research", ["search"], ["auto"]))
    A(("presentation_research", F.presentation_research, "Find presentations.",
       _s({"query": _p("str", "query"), "limit": _p("int", "max", default=6)}, ["query"]),
       "presentation-research", ["search"], ["auto"]))
    A(("fetch_document", F.fetch_document, "Fetch a document and index its text.",
       _s({"url": _p("str", "url")}, ["url"]), "document-research", ["fetch"], ["auto"]))
    # ------------- evidence / verification -------------
    A(("extract_evidence", F.extract_evidence, "Evidence for a claim.",
       _s({"claim": _p("str", "claim"),
           "support_terms": _p("array", "supporting phrases", items={"type": "string"}),
           "limit_per_query": _p("int", "max per query", default=6)}, ["claim"]),
       "evidence-extraction", ["evidence"], ["auto"]))
    A(("verify_claim", F.verify_claim, "Verify a claim with confidence.",
       _s({"claim": _p("str", "claim"), "phrases": _p("array", "phrases", items={"type": "string"}),
           "verification_threshold": _p("float", "threshold", default=0.5)}, ["claim"]),
       "claim-verification", ["evidence"], ["auto"]))
    A(("find_contradictions", F.find_contradictions, "Hunt criticisms/limitations.",
       _s({"claim": _p("str", "claim"), "angles": _p("array", "angles", items={"type": "string"}),
           "limit_per_query": _p("int", "max per query", default=6)}, ["claim"]),
       "contradiction-search", ["evidence"], ["auto"]))
    A(("fact_check", F.fact_check, "Fact-check verdict + evidence.",
       _s({"statement": _p("str", "statement"), "phrases": _p("array", "phrases", items={"type": "string"})},
          ["statement"]), "fact-checking", ["evidence"], ["auto"]))
    A(("compare_entities", F.compare_entities, "Compare entities across dimensions.",
       _s({"entities": _p("array", "entity names", items={"type": "string"}),
           "dimensions": _p("array", "dimensions", items={"type": "string"}),
           "limit": _p("int", "results per entity", default=4)}, ["entities"]),
       "comparison", ["compare"], ["auto"]))
    A(("compare_sources", F.compare_sources, "Analyze/compare source URLs.",
       _s({"urls": _p("array", "source urls", items={"type": "string"})}, ["urls"]),
       "comparison", ["compare"], ["internal"]))
    A(("investigate_error", F.investigate_error, "Deep error investigation.",
       _s({"error": _p("str", "error message"), "tech": _p("str", "technology context")},
          ["error"]), "error-investigation", ["research"], ["auto"]))
    A(("source_analysis", F.source_analysis, "Analyze a source's authority/type.",
       _s({"url": _p("str", "url")}, ["url"]), "source-analysis", ["analysis"], ["internal"]))
    # ------------- research -------------
    A(("deep_research", F.deep_research, "Autonomous deep research.",
       _s({"objective": _p("str", "research objective"),
           "budget": _p("object", "budget overrides")}, ["objective"]),
       "deep-research", ["research"], ["auto"]))
    A(("research_plan", F.research_plan, "Preview a research plan (no execute).",
       _s({"objective": _p("str", "objective")}, ["objective"]),
       "deep-research", ["research"], ["internal"]))
    A(("research_status", F.research_status, "Status of a research task.",
       _s({"task_id": _p("str", "task id")}, ["task_id"]),
       "deep-research", ["research"], ["internal"]))
    A(("research_result", F.research_result, "Result of a research task.",
       _s({"task_id": _p("str", "task id")}, ["task_id"]),
       "deep-research", ["research"], ["internal"]))
    A(("cancel_research", F.cancel_research, "Cancel a research task.",
       _s({"task_id": _p("str", "task id")}, ["task_id"]),
       "deep-research", ["research"], ["internal"]))
    A(("research_graph", F.research_graph, "Knowledge graph of a task.",
       _s({"task_id": _p("str", "task id")}, ["task_id"]),
       "knowledge-graph", ["research"], ["internal"]))
    # ------------- discovery -------------
    A(("list_skills", F.list_skills, "List available skills.", _s({}), "system", ["discovery"], ["internal"]))
    A(("list_tools", F.list_tools, "List available tools.", _s({}), "system", ["discovery"], ["internal"]))
    A(("get_skill", F.get_skill, "One skill definition.",
       _s({"name": _p("str", "skill name")}, ["name"]), "system", ["discovery"], ["internal"]))
    A(("get_tool", F.get_tool, "One tool definition.",
       _s({"name": _p("str", "tool name")}, ["name"]), "system", ["discovery"], ["internal"]))
    A(("get_capabilities", F.get_capabilities, "Capability summary.", _s({}), "system", ["discovery"], ["internal"]))
    A(("list_providers", F.list_providers, "List providers.", _s({}), "system", ["discovery"], ["internal"]))
    A(("list_operators", F.list_operators, "List search operators.", _s({}), "system", ["discovery"], ["internal"]))
    return L


def build_tool_registry() -> ToolRegistry:
    reg = ToolRegistry()
    for name, func, desc, schema, skill, cats, providers in _specs():
        reg.register(Tool(name, description=desc, func=func, input_schema=schema,
                          skill=skill, categories=cats, providers=providers))
    return reg


TOOL_SPECS = [t[0] for t in _specs()]
