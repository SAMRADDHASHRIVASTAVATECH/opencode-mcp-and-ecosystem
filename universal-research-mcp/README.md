# Universal Web Research — MCP & Skill System

A dependency-light **Model Context Protocol (MCP) server** plus an **autonomous
deep-research engine** and a **portable skill catalog**. It researches topics
across the general web, code/GitHub, academic sources (arXiv/Crossref), news,
and documents — gathering evidence, verifying claims, finding contradictions,
comparing options, and producing a knowledge graph with budgets and stopping
intelligence.

The package is **SDK-independent**: the MCP server speaks newline-delimited
JSON-RPC 2.0 over stdio by itself, so it runs in any MCP client (Claude
Desktop, Cursor, OpenCode, `npx mcp` style tooling, custom clients) without
depending on a particular MCP SDK version.

> **Honesty note on availability.** All network providers are best-effort and
> some require credentials or are blocked by the target (see
> [Availability](README.md#provider-availability)). The engine degrades
> gracefully, routes around failures, and tracks them. Offline mock mode is
> deterministic and network-free. Do not assume every provider "just works" —
> check the table below.

---

## Features

- **Two modes**
  - **Tool/skill mode** — ~48 declarative tools (search, fetch, crawl,
    documents, verification, comparison, GitHub, academic, news, research
    lifecycle) and 29 built-in, individually-callable skills.
  - **Autonomous deep-research mode** — `deep_research` plans, runs in
    iterative rounds across source families, crawls seeds, extracts/verifies
    evidence, detects contradictions, and stops on budget/stopping criteria.
- **Evidence & verification engine** — source scoring, authority/primary-source
  analysis, claim verification with contradiction detection (with a
  negative-signal filter so topic-overlap isn't mislabelled as contradiction).
- **State machine** with per-task budgets (`max_iterations`, `max_runtime`,
  `max_searches`, `max_pages`…), run-time accounting, cancellation, and a
  research knowledge graph.
- **Search query engine** — operators (`site:`, `-word`, `"phrase"`,
  `filetype:`, `intitle:`, dates), families (discovery/code/academic/news/…),
  query building/validation/refinement/expansion.
- **Web reader + crawler** — SSRF-safe HTTP, HTML → readable text with
  headings/links, PDF/doc/xlsx/pptx extraction via the documents engine,
  bounded crawling.
- **Security built in** — SSRF/private-IP rejection, scheme allow-listing,
  credential-in-URL rejection, injection heuristics, size caps, robots
  awareness, secret redaction.
- **Skills directory** — rendered to `skills/<name>/SKILL.md` so skills travel
  as human/agent-readable markdown alongside the code.

---

## Layout

```
universal-research-mcp/
├── pyproject.toml            # packaging + console script
├── mcp_server.py             # stdio MCP entry point (SDK-free)
├── .env.example              # all optional knobs, UR_-prefixed
├── README.md / ARCHITECTURE.md / SECURITY.md / MCP.md
├── skills/                   # rendered skill catalog (SKILL.md + INDEX.md)
├── src/universal_research/
│   ├── __main__.py           # python -m universal_research
│   ├── config.py models.py errors.py security.py network.py cache.py
│   ├── sources.py functions.py runtime.py router.py llm.py
│   ├── mcp_interface.py      # MCP server (tools/resources/prompts)
│   ├── registry/             # provider, skills, tools catalogs
│   ├── providers/            # arxiv bing brave crossref duckduckgo github
│   │                         # googlenews hackernews mock searxng
│   ├── search/               # operators, query, ranking, client
│   ├── web/                  # reader, crawler
│   ├── documents/            # pdf/doc/xlsx/pptx parsers + engine
│   ├── verify/               # evidence, verification, factcheck
│   └── research/             # state, graph, planner, compare, orchestrator
└── tests/                    # offline, deterministic, mock-only (no network)
```

---

## Install

Python 3.10+.

```bash
cd universal-research-mcp
python -m venv .venv && source .venv/bin/activate
pip install -e .          # installs package + `universal-research-mcp` script
```

Runtime deps are deliberately light: `httpx`, `beautifulsoup4`, `lxml`,
`pypdf`, `python-docx`, `openpyxl`, `python-pptx`. No MCP SDK is required.

### Run the MCP server

```bash
# online (best-effort live providers)
universal-research-mcp
# or
python mcp_server.py
# or
python -m universal_research

# deterministic offline/mock mode (great for tests & demos)
python mcp_server.py --offline

# inspect the surface without starting the server
python -m universal_research --list-tools
python -m universal_research --list-skills
```

Add the invocation to your MCP client as a **stdio** server command. Example
(OpenCode / Claude-style config, JSON):

```jsonc
{
  "mcpServers": {
    "universal-research": {
      "command": "python",
      "args": ["/absolute/path/to/mcp_server.py"],
      "env": { "UR_OFFLINE": "1" }   // optional; drop for live
    }
  }
}
```

---

## Configuration

All settings are optional and read from environment variables prefixed with
`UR_`. Copy `.env.example` to `.env` (auto-loaded from the working dir or
package root) or export the vars. Real process environment wins over `.env`.

| Var | Meaning | Default |
|-----|---------|---------|
| `UR_OFFLINE` | force offline deterministic mock mode | off |
| `UR_BRAVE_API_KEY` | Brave Search API key (needed for Brave results) | — |
| `UR_SEARXNG_BASE_URL` | self-hosted SearXNG JSON endpoint | — |
| `UR_BING_ENABLED` / `UR_DUCKDUCKGO_ENABLED` | best-effort HTML engines | true |
| `UR_RESEARCH_MODEL_BASE_URL`/`_NAME`/`_API_KEY` + `UR_USE_LLM` | optional OpenAI-compatible local LLM for planner/synthesis; deterministic fallbacks when absent | off |
| `UR_ALLOW_PRIVATE_IPS` | **never** enable in production; SSRF guard | false |
| `UR_MAX_SEARCHES`, `UR_MAX_PAGES`, `UR_MAX_ITERATIONS`, `UR_MAX_RUNTIME` | research budgets | 40/25/12/300 |
| `UR_MAX_DOCUMENT_SIZE` | per-fetch size cap (bytes) | 4000000 |
| `UR_TIMEOUT`, `UR_USER_AGENT` | HTTP | 20 / UA |

---

## Provider availability

Adapters exist for: **arXiv**, **Bing** (HTML), **Brave** (key), **Crossref**,
**DuckDuckGo** (HTML), **GitHub** (REST), **Google News** (RSS), **Hacker
News** (Algolia), **SearXNG** (URL), plus a deterministic **mock** used
offline.

| Provider | Needs credential? | Status in this sandbox |
|----------|-------------------|------------------------|
| mock | no | ✅ deterministic, used offline |
| github (repos/issues/releases) | no | ✅ works unauthenticated (code search needs a token) |
| googlenews (RSS), crossref, arxiv, hackernews | no | ✅ reachable |
| bing | no | reachable but relevance can be noisy; engine gates/dedupes |
| brave | **Brave API key** | only if keyed |
| searxng | base URL | only if self-hosted |
| duckduckgo | no | can be bot-blocked (HTTP 202); engine treats as degraded |

The engine never circumvents anti-bot blocks. When a provider is unavailable,
routing notes it (`degraded: true`, `notes: [...]`) and continues with the
others — it does **not** claim success it did not have.

---

## The skill system

`registry/skills_catalog.py` is the single source of truth for 29 built-in
skills (deep-research, fact-checking, github-research, pdf-research,
web-crawler, comparison, contradiction-search, literature-review, …). Each
skill declares its tools, dependencies, providers, input/output schemas, and
security notes. They are:

1. **registered** as data (countable, queryable via `list_skills`), and
2. **rendered** to `skills/<name>/SKILL.md` by `scripts/render_skills.py`.

Each skill is callable individually through its bound tools and is composable
by the deep-research orchestrator.

---

## Quick start (Python API)

```python
import os
os.environ["UR_OFFLINE"] = "1"          # deterministic mode, no network
from universal_research import functions as F

print(len(F.list_tools()["tools"]), "tools")
print(len(F.list_skills()["skills"]), "skills")

res = F.search_web("python pdf parsing", limit=4)
for r in res["results"]:
    print("-", r["title"], "|", r["url"])

fc = F.fact_check("PyMuPDF is a PDF library for Python")
print(fc["verdict"], fc["confidence"])

plan = F.research_plan("best open source pdf parsing library")
dr = F.deep_research("open source python pdf parsing")     # async task
# poll: F.research_status(dr["task_id"]), then F.research_result(task_id)
```

See [ARCHITECTURE.md](ARCHITECTURE.md), [SECURITY.md](SECURITY.md), and
[MCP.md](MCP.md).
