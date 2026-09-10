"""Tool implementations (the callable bodies behind the MCP tools and skills).

Every function is individually callable; several are also composed by the deep
research orchestrator. They are thin wrappers over the runtime subsystems and
return JSON-safe dicts with compact, structured outputs for small models.
"""
from __future__ import annotations

import json
from typing import Optional

from . import config
from .errors import NotFoundError, ResearchError
from .runtime import get_runtime, reset_runtime

# ======================================================================
# discovery
# ======================================================================

def list_skills():
    from .registry.skills import build_skill_registry
    reg = build_skill_registry()
    return {"count": len(reg), "skills": [
        {"name": s.name, "description": s.description,
         "tools": s.tools, "dependencies": s.dependencies}
        for s in reg.all()]}


def list_tools():
    from .registry.tools import build_tool_registry
    reg = build_tool_registry()
    return {"count": len(reg), "tools": [t.to_dict() for t in reg.all()]}


def get_skill(name: str):
    from .registry.skills import build_skill_registry
    reg = build_skill_registry()
    try:
        return reg.get(name).to_dict()
    except NotFoundError:
        return {"error": f"skill not found: {name}"}


def get_tool(name: str):
    from .registry.tools import build_tool_registry
    reg = build_tool_registry()
    try:
        return reg.get(name).to_dict()
    except NotFoundError:
        return {"error": f"tool not found: {name}"}


def get_capabilities():
    return {"modes": ["direct", "autonomous"],
            "skills": [s.name for s in list_skills()["skills"]],
            "tools": [t["name"] for t in list_tools()["tools"]],
            "resources": ["research://skills", "research://tools",
                          "research://operators", "research://providers",
                          "research://research/{id}", "research://graph/{id}"],
            "providers_configured": [
                {"name": p.name, "configured": p.configured,
                 "capabilities": sorted(p.capabilities)}
                for p in get_runtime().providers.all()]}


def list_providers():
    rt = get_runtime()
    return {"providers": [p.to_dict() for p in rt.providers.all()]}


def list_operators():
    return {"operators": [
        {"op": "exact phrase", "syntax": '"phrase"'},
        {"op": "site", "syntax": "site:domain"},
        {"op": "exclude site/term", "syntax": "-site:domain | -word"},
        {"op": "OR", "syntax": "a OR b"},
        {"op": "intitle/allintitle", "syntax": "intitle:word"},
        {"op": "inurl/allinurl", "syntax": "inurl:word"},
        {"op": "filetype", "syntax": "filetype:pdf"},
        {"op": "before/after", "syntax": "before:YYYY-MM-DD after:YYYY-MM-DD"},
    ]}


# ======================================================================
# search
# ======================================================================

def search_web(query: str, limit: int = 8, providers: Optional[list] = None,
               **ctx):
    """Simplest search. providers auto-selected if omitted."""
    rt = get_runtime()
    out = rt.search.search(query, kind="web", limit=limit, providers=providers,
                           use_mock=_wants_mock())
    return _compact(out)


def search_multi(query: str, limit: int = 6, providers: Optional[list] = None,
                 **ctx):
    """Multi-provider general search."""
    rt = get_runtime()
    out = rt.search.search(query, kind="web", limit=limit, providers=providers,
                           use_mock=_wants_mock())
    return _compact(out)


def search_operator(expression: str, limit: int = 8, kind: str = "web",
                    providers: Optional[list] = None):
    """Operator-aware search. Returns parsed structure + results."""
    rt = get_runtime()
    out = rt.search.search_operator(expression, limit=limit, kind=kind)
    compact = _compact(out)
    compact["parsed"] = out.get("parsed", {})
    return compact


# ---- query engine tools -------------------------------------------------
def build_search_query(topic: str, family: str = "discovery", n: int = 4,
                       target: str = "", site: str = "", filetype: str = ""):
    rt = get_runtime()
    qe = rt.query
    qs = qe.generate(topic, family, n, target=target)
    if site or filetype:
        qs = [qe.refine(q, add_site=site, filetype=filetype) for q in qs]
    return {"topic": topic, "family": family, "queries": qe.deduplicate(qs)}


def validate_search_query(query: str):
    return get_runtime().query.validate(query)


def expand_query(topic: str, terms: Optional[list] = None, n: int = 6):
    return {"topic": topic, "expansions":
            get_runtime().query.expand(topic, terms=terms, n=n)}


def refine_query(query: str, domain: str = "", filetype: str = "",
                 exact: bool = False, remove_terms: Optional[list] = None):
    return {"refined": get_runtime().query.refine(
        query, domain=domain, filetype=filetype, exact=exact,
        remove_terms=remove_terms)}


def get_search_strategy(topic: str, target: str = ""):
    qe = get_runtime().query
    return {"topic": topic, "target": target,
            "families": qe.strategy(topic, {"target": target})}


# ======================================================================
# web reader / crawler
# ======================================================================

def fetch_source(url: str):
    """Fetch + parse one page/document into compact Source (content indexed
    externally)."""
    rt = get_runtime()
    src = rt.reader.fetch(url)
    return src.to_dict(include_heavy=False)


def extract_links(url: str, limit: int = 50):
    rt = get_runtime()
    src = rt.reader.fetch(url)
    return {"url": url, "links": src.links[:limit], "count": len(src.links)}


def crawl_web(seed: str, topic: str = "", depth: int = 1, max_pages: int = 8,
              same_domain: bool = True, domains: Optional[list] = None):
    rt = get_runtime()
    seeds = seed if isinstance(seed, list) else [seed]
    out = rt.crawler.crawl(seeds, topic=topic, depth=depth,
                           max_pages=max_pages, domains=domains,
                           same_domain_only=same_domain)
    return {"sources": out["sources"], "visited_count": len(out["visited"]),
            "frontier_sample": out["visited"][:20],
            "depth_limit": out["depth_limit"], "page_limit": out["page_limit"]}


# ======================================================================
# vertical searches
# ======================================================================

def _github_search(query, scope, limit):
    rt = get_runtime()
    if rt.offline_mode:
        out = rt.search.search(query, kind="code", limit=limit, use_mock=True)
        return _compact(out)
    prov = rt.providers.get("github")
    try:
        res = prov.adapter.search(query, limit=limit,
                                  opts={"scope": scope})
        return {"results": [r.to_dict() for r in res],
                "providers_used": ["github"], "notes": [], "degraded": False,
                "scope": scope}
    except Exception as e:  # noqa: BLE001
        return {"error": f"{type(e).__name__}: {e}", "scope": scope}


def search_github(query: str, scope: str = "repositories", limit: int = 8):
    return _github_search(query, scope, limit)


def github_repository(repo: str):
    return _github_search(repo, "repository", 1)


def github_code_search(query: str, limit: int = 8):
    return _github_search(query, "code", limit)


def github_issues(query: str, limit: int = 8):
    return _github_search(query, "issues", limit)


def github_releases(repo: str, limit: int = 5):
    rt = get_runtime()
    try:
        prov = rt.providers.get("github")
        res = prov.adapter.releases(repo, limit=limit)
        return {"repo": repo, "releases": [r.to_dict() for r in res]}
    except Exception as e:  # noqa: BLE001
        return {"repo": repo, "error": f"{type(e).__name__}: {e}"}


def search_academic(query: str, limit: int = 8):
    rt = get_runtime()
    out = rt.search.search(query, kind="paper", limit=limit, use_mock=_wants_mock())
    return _compact(out)


def paper_research(query: str, limit: int = 8):
    return search_academic(query, limit)


def literature_review(topic: str, limit_per_source: int = 6):
    """Multi-source academic sweep (arXiv + Crossref)."""
    rt = get_runtime()
    families = {"concepts": topic, "methods": f"{topic} method",
                "datasets": f"{topic} dataset", "evaluation": f"{topic} evaluation",
                "surveys": f"{topic} survey"}
    collected = []
    for label, q in families.items():
        try:
            out = rt.search.search(q, kind="paper", limit=limit_per_source,
                                   use_mock=_wants_mock())
            for r in out["results"]:
                collected.append({"label": label, "title": r.title,
                                  "url": r.url, "date": r.date,
                                  "extra": r.extra})
        except Exception:
            continue
    return {"topic": topic, "families": list(families),
            "papers": collected[:60], "count": len(collected)}


def search_government(query: str, region: str = "in", limit: int = 8):
    """Site-restricted official research (#20). region: in/us/uk/etc."""
    rt = get_runtime()
    from .search.operators import domain_for_type
    site = domain_for_type("government", region)
    refined = rt.query.refine(query, domain=site) if site else query
    out = rt.search.search(refined, kind="web", limit=limit, use_mock=_wants_mock())
    return {"region": region, "domain_restriction": site, **_compact(out)}


def search_news(query: str, limit: int = 8, region: str = "US",
                language: str = "en"):
    rt = get_runtime()
    out = rt.search.search(query, kind="news", limit=limit, use_mock=_wants_mock())
    return _compact(out)


def search_community(query: str, limit: int = 8):
    rt = get_runtime()
    out = rt.search.search(query, kind="community", limit=limit,
                           use_mock=_wants_mock())
    return _compact(out)


# ======================================================================
# documents
# ======================================================================

def search_documents(query: str, limit: int = 8, filetype: str = "pdf"):
    """Find documents (PDF/docs) about a topic (#16)."""
    rt = get_runtime()
    q = rt.query.refine(query, filetype=filetype)
    out = rt.search.search(q, kind="web", limit=limit, use_mock=_wants_mock())
    return {"requested_filetype": filetype, **_compact(out)}


def pdf_research(query: str, limit: int = 8):
    return search_documents(query, limit, filetype="pdf")


def spreadsheet_research(query: str, limit: int = 6):
    return search_documents(query, limit, filetype="xlsx")


def presentation_research(query: str, limit: int = 6):
    return search_documents(query, limit, filetype="pptx")


def fetch_document(url: str):
    """Fetch a document (pdf/doc/xlsx/pptx/web) and index its text externally."""
    return fetch_source(url)


# ======================================================================
# evidence / verification / contradiction / factcheck / compare / error
# ======================================================================

def extract_evidence(claim: str, support_terms: Optional[list] = None,
                     limit_per_query: int = 6):
    rt = get_runtime()
    return rt.evidence.extract(claim, support_terms=support_terms,
                               limit_per_query=limit_per_query)


def verify_claim(claim: str, phrases: Optional[list] = None,
                 fetch_depth: int = 0, verification_threshold: float = 0.5):
    rt = get_runtime()
    return rt.verification.verify(claim, phrases=phrases,
                                  fetch_depth=fetch_depth,
                                  verification_threshold=verification_threshold)


def find_contradictions(claim: str, angles: Optional[list] = None,
                        limit_per_query: int = 6):
    rt = get_runtime()
    return rt.evidence.contradictory(claim, angles=angles,
                                     limit_per_query=limit_per_query)


def fact_check(statement: str, phrases: Optional[list] = None):
    rt = get_runtime()
    return rt.factcheck.check(statement, phrases=phrases)


def compare_entities(entities, dimensions: Optional[list] = None,
                     limit: int = 4):
    rt = get_runtime()
    return rt.compare.compare_entities(entities, dimensions=dimensions,
                                       limit=limit)


def compare_sources(urls, **kw):
    rt = get_runtime()
    return rt.compare.compare_sources(urls)


def investigate_error(error: str, tech: str = ""):
    rt = get_runtime()
    return rt.errors.investigate(error, tech=tech)


def source_analysis(url: str, **kw):
    from . import sources as S
    return S.analyze_source(url, **kw)


# ======================================================================
# deep research
# ======================================================================

def deep_research(objective: str, budget: Optional[dict] = None):
    rt = get_runtime()
    task_id = rt.orchestrator.start(objective, budget=budget)
    return {"task_id": task_id, "status": "running",
            "objective": objective,
            "note": "poll research_status(task_id) for progress/results"}


def research_plan(objective: str):
    """Return the intended plan (steps) without executing (#57)."""
    rt = get_runtime()
    return rt.planner.plan(objective)


def research_status(task_id: str):
    rt = get_runtime()
    st = rt.orchestrator.status(task_id)
    if st is None:
        return {"error": f"task not found: {task_id}"}
    return st


def research_result(task_id: str):
    rt = get_runtime()
    res = rt.orchestrator.get_result(task_id)
    return {"task_id": task_id, "result": res}


def cancel_research(task_id: str):
    rt = get_runtime()
    ok = rt.orchestrator.cancel(task_id)
    return {"task_id": task_id, "cancelled": ok}


def research_graph(task_id: str):
    rt = get_runtime()
    return rt.orchestrator.graph(task_id)


# ======================================================================
# helpers
# ======================================================================

def _compact(out) -> dict:
    return {"results": [r.to_dict() for r in out.get("results", [])],
            "providers_used": out.get("provider_used", []),
            "notes": out.get("notes", []),
            "degraded": out.get("degraded", False)}


def _wants_mock() -> bool:
    rt = get_runtime()
    return bool(rt.offline_mode)
