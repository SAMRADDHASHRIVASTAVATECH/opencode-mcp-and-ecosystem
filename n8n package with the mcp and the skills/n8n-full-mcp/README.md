# n8n-full-mcp

Hybrid, approval-gated n8n MCP control layer: official instance MCP first, REST API second, local/offline artifacts last.

## Install/build

```bash
npm ci
npm run check
npm test
npm run build
```

## Run (stdio)

```bash
N8N_MODE=offline N8N_OFFLINE_DIR=./n8n-artifacts node lib/index.js
```

For online use, configure `N8N_OFFICIAL_MCP_URL` and token and/or `N8N_BASE_URL` plus API key. Do not put credentials in committed files. See `.env.example`.

## OpenCode
Use `examples/opencode-v1.jsonc` for stable V1 syntax or `examples/opencode-v2.jsonc` for OpenCode V2. Copy the separate `n8n/` package to `.opencode/skills/n8n/` (include `SKILL.md` and references).

## Architecture
OpenCode skill → local stdio MCP → capability/mode router → official n8n MCP (Streamable HTTP) → REST → offline JSON artifacts. Write/execute operations pass through the exact-plan approval engine and audit layer.

## Modes
- `online`: remote Cloud/self-hosted endpoint; requires configured remote backend.
- `local`: localhost/private local n8n; HTTP allowed only with explicit localhost exception.
- `offline`: no n8n calls; workflow artifact analysis/create/replace/delete only.

Mode never silently changes. Fallback occurs only among configured adapters consistent with that mode. Offline mode does not contact n8n.

## Documentation
See `docs/research.md`, `capability-matrix.md`, `tool-inventory.md`, and `security.md`.
