# Architecture

This document describes how the Universal Web Research system is layered and
how a research task flows through it. It reflects what is implemented.

```
                    ┌──────────────────────────────────────────────┐
                    │                MCP boundary (stdio)          │
                    │   mcp_interface.py  <->  MCP client          │
                    │   tools / resources / prompts                │
                    └───────────────────┬──────────────────────────┘
                                        │ (functions.py = 1:1 API)
                                        ▼
                    ┌──────────────────────────────────────────────┐
                    │                 functions.py                 │
                    │  ~48 thin wrappers over the runtime engines  │
                    └───────────────────┬──────────────────────────┘
                                        ▼
                    ┌──────────────────────────────────────────────┐
                    │             Runtime (composition root)       │
                    │  providers · router · search · query · web   │
                    │  documents · verify · research orchestration │
                    └───┬──────────┬──────────┬─────────┬──────────┘
                        ▼          ▼          ▼         ▼
               ┌──────────┐  ┌──────────┐ ┌────────┐ ┌──────────────┐
               │ Provider │  │ Web      │ │Verify  │ │Research      │
               │ Registry │  │ Reader/  │ │Evidence│ │Orchestrator  │
               │ + Router │  │ Crawler  │ │+FactChk│ │ + State/Graph│
               └──────────┘  └──────────┘ └────────┘ └──────────────┘
```

## Modules

### Config & cross-cutting
- **`config.py`** — `Settings` + `ResearchBudget` dataclasses assembled from
  `UR_`-prefixed environment variables; `.env` auto-loading; a canonical
  `save_env_example()` emitter.
- **`security.py`** — URL validation (SSRF/private-IP/loopback rejection,
  scheme allow-list, credential-in-URL rejection), content-type/extension
  classification, injection heuristics, size caps, secret redaction.
- **`network.py`** — single pooled `httpx` client; `fetch` and `fetch_capped`
  (streams up to the size cap). All providers and the reader go through here.
- **`cache.py`** — small disk/session cache for search + fetches (disabled in
  offline mode).
- **`models.py`** — dataclasses: `SearchResult`, `Source`, `Claim`, `Evidence`,
  `Finding`, `Node`, `Edge`, `ResearchStates`, relation vocabulary.
- **`errors.py`** — typed exceptions (`ProviderError`, `SecurityRejectionError`,
  `UnsafeContentError`, …).

### Providers & routing
- **`providers/`** — one adapter per provider, all returning normalized
  `SearchResult`s. Providers: `arxiv`, `bing`, `brave`, `crossref`,
  `duckduckgo`, `github`, `googlenews`, `hackernews`, `searxng`, and a
  deterministic `mock`.
- **`router.py`** (`ToolRouter`) — decides which provider(s) to ask for a query
  family (discovery/code/academic/news/government/community/…), in which order,
  with fallbacks. In offline mode it is forced to `mock` only.
- **`registry/`** — `base.py` (`ProviderRegistry`), `skills_catalog.py` (the
  29-skill source of truth), `skills.py` (builders), `tools.py` (the 48-tool
  declarative registry with JSON schemas and skill/category/provider metadata).

### Search
- **`search/operators.py`** — parse/emit operator queries (`-word`,
  `"phrase"`, `site:`, `intitle:`, `inurl:`, `filetype:`, `before/after:`).
- **`search/query.py`** (`QueryEngine`) — builds query families per topic and
  target; validates/expands/refines.
- **`search/ranking.py`** — dedupe and rank by relevance/authority/freshness.
- **`search/client.py`** (`SearchClient`) — orchestrate one/multi-provider
  queries, dedupe, per-provider error isolation.

### Web reading & crawling
- **`web/reader.py`** (`WebReader`) — SSRF-safe fetch → HTML readability
  extraction (main content, headings, canonical link, links) or delegates to
  the documents engine by content type. **Offline-aware**: returns
  deterministic mock content when `UR_OFFLINE=1` (no network).
- **`web/crawler.py`** (`Crawler`) — bounded breadth/depth crawl seeded from a
  URL + topic keywords.
- **`documents/`** — `engine.py` (ingest + index content to a content_id) and
  parsers for PDF/docx/xlsx/pptx.

### Verification
- **`verify/engine.py`** (`EvidenceEngine`, `VerificationEngine`) — source
  analysis (authority/primary-secondary/independence), evidence extraction,
  and claim verification that weighs supporting vs. contradicting evidence.
  A **negative-signal filter** ensures topic-overlap matches are not counted as
  contradictions unless the source actually negates the claim.
- **`verify/factcheck.py`** (`FactChecker`) — returns a plain-language
  verdict (`verified` / `contradicted` / `unsupported` / `inconclusive`) with
  confidence and evidence.

### Research orchestration
- **`research/state.py`** (`ResearchManager`) — task registry + state machine
  (e.g. `PLANNING → RUNNING → … → COMPLETED/FAILED/CANCELLED`), progress
  records, per-task budgets, cancellation.
- **`research/graph.py`** (`KnowledgeGraph`) — accumulates nodes (sources,
  claims) and edges (`supports`, `contradicts`, `references`, …).
- **`research/planner.py`** (`ResearchPlanner`) — builds a plan (question →
  sub-questions → source families → operators). Uses the optional local LLM
  when `UR_USE_LLM=1`, else deterministic heuristics.
- **`research/orchestrator.py`** (`ResearchOrchestrator`) — the iterative
  driver:
  - reduces the natural-language objective to a **concise keyword query**
    (`_concise`, stop-word/stem reduced, default n) so search engines keep
    relevance on long queries;
  - per-task `_seen_queries` dedupe;
  - a **relevance gate** drops results from noisy HTML providers when their
    title shares no distinctive keyword of the reduced query (other providers
    are trusted);
  - verify objective + gather contradictions (with the same negative-signal
    gate);
  - respect the budget and stopping intelligence.
- **`research/compare.py`** (`ComparisonEngine`) — structured entity/source
  comparison across dimensions.
- **`research/errorskill.py`** (`ErrorInvestigator`) — investigate an error
  string against docs/community/GitHub.

### Interface
- **`mcp_interface.py`** — thin, SDK-free MCP server over newline JSON-RPC:
  `initialize`, `ping`, `tools/list`, `tools/call`, `resources/list`,
  `resources/read`, `prompts/list`, `prompts/get`. Every request is dispatched
  through `_safe_handle` so a single bad request returns a JSON-RPC error
  instead of killing the stdio loop.

---

## How a research task flows

1. **Plan** (`research_plan`) → produce a research plan from the objective.
2. **Deep research** (`deep_research`) starts an async task, immediately
   returns `task_id`/`status`.
3. The orchestrator plans sub-questions, then iterates:
   for each question it **routes to providers** for the family → **concise
   query** → **relevance gate** → dedupe/rank → optionally **fetch** the best
   sources and **crawl** seed pages.
4. Extracted content is chunked/indexed (external `content_id`); the model only
   sees compact fields + excerpts.
5. **Verification** passes gather supporting/contradicting evidence and update
   the graph edges.
6. Budget accounting decides when to **stop** (`COMPLETED`) vs. escalate
   (`FAILED`) vs. allow cancellation.
7. Clients poll `research_status(task_id)` and read `research_result(task_id)`
   or the graph `research_graph(task_id)`.

---

## Reproducibility & honesty

- Offline mode pins providers to `mock` and the reader to offline content, so
  the engine is **fully deterministic and testable with no network**.
- Live mode is **best-effort**: routing notes failures, marks `degraded`, and
  keeps a `notes` list — results never claim providers that did not respond.
