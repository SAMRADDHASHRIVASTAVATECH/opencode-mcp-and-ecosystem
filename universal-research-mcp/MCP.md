# MCP protocol

This server implements the **Model Context Protocol** over stdio using
**newline-delimited JSON-RPC 2.0** — the reference MCP stdio transport. It is
deliberately **SDK-independent**: no `mcp` Python package is imported, so it
does not break when MCP SDKs change their APIs (v1 → v2 renamed
`FastMCP`→`MCPServer`, etc.).

## Invocation

```bash
# online
python mcp_server.py
python -m universal_research
universal-research-mcp

# deterministic offline
python mcp_server.py --offline
```

Wire it to an MCP client as a **stdio server**:

```jsonc
{ "command": "python", "args": ["/abs/path/universal-research-mcp/mcp_server.py"] }
```

## Framing

- Requests and responses are single JSON objects, one per line, UTF-8.
- Each request that has an `id` gets a response with that `id`; notifications
  (no `id`) get none.
- Errors use JSON-RPC 2.0 error frames: `{ "jsonrpc":"2.0","id":N,
  "error":{"code":-32002,"message":"…"} }`.

## Methods

| Method | Notes |
|--------|-------|
| `initialize` | returns `serverInfo` `{name:"universal-research", version:"1.0.0"}`, protocol version `2024-11-05`, capabilities for tools/resources/prompts |
| `notifications/initialized` | accepted, no response |
| `ping` | → `{}` |
| `tools/list` | **48 tools** with JSON input schemas |
| `tools/call` | dispatch by name; coerces args to declared JSON-schema types; returns text content with `isError` |
| `resources/list` | resource templates below |
| `resources/read` | reads a resource by URI |
| `prompts/list` | **11 prompts** |
| `prompts/get` | renders a prompt template; clean `-32002` error if required args are missing |
| anything else | `-32601 method not found` (or `-32603` via `_safe_handle` on an unexpected error) |

## Tools

All 48 tool names map 1:1 to `functions.py`. Major groups:

- **Search**: `search_web`, `search_multi`, `search_operator`,
  `build_search_query`, `expand_query`, `refine_query`, `validate_search_query`,
  `get_search_strategy`, `list_providers`, `list_operators`.
- **Web**: `fetch_source`, `fetch_document`, `extract_links`, `crawl_web`.
- **Domain skills**: `search_github`, `github_repository`,
  `github_code_search`, `github_issues`, `github_releases`,
  `search_academic`, `paper_research`, `literature_review`,
  `search_government`, `search_news`, `search_community`, `search_documents`,
  `pdf_research`, `spreadsheet_research`, `presentation_research`.
- **Verification**: `extract_evidence`, `verify_claim`, `find_contradictions`,
  `fact_check`, `compare_entities`, `compare_sources`, `source_analysis`,
  `investigate_error`.
- **Research lifecycle**: `deep_research`, `research_plan`, `research_status`,
  `research_result`, `research_graph`, `cancel_research`.
- **Introspection**: `list_skills`, `list_tools`, `get_skill`, `get_tool`,
  `get_capabilities`.

## Resources

Static resources under `research://`, plus two per-task templates.

- `research://skills` — built-in skill catalog
- `research://tools` — tool registry
- `research://operators` — supported search operators
- `research://providers` — provider list + availability
- `research://strategies` — query/route strategies per family
- `research://research/{id}` — live status/result of a research task
- `research://graph/{id}` — knowledge graph of a research task

## Prompts

11 packaged prompts (name — description): `deep_research`,
`technical_research`, `web_investigation`, `github_research`,
`academic_research`, `document_research`, `fact_check`,
`error_investigation`, `competitive_research`, `literature_review`,
`source_verification`. Each declares its required arguments (e.g.
`deep_research` requires `objective`); calling `prompts/get` without a required
argument returns a clean `-32002` error, with it returns a rendered user
message plus a recommended tool note.

## Example session (offline)

```json
{"jsonrpc":"2.0","id":1,"method":"initialize",
 "params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"t"}}}
{"jsonrpc":"2.0","method":"notifications/initialized"}
{"jsonrpc":"2.0","id":2,"method":"tools/call",
 "params":{"name":"fact_check","arguments":{"statement":"PyMuPDF is a PDF library"}}}
{"jsonrpc":"2.0","id":3,"method":"resources/read","params":{"uri":"research://skills"}}
{"jsonrpc":"2.0","id":4,"method":"prompts/get",
 "params":{"name":"fact_check","arguments":{"statement":"PyMuPDF is a PDF library"}}}
```

Each produces a single JSON object response on its own line.
