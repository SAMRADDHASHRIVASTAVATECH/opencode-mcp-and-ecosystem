# Test report — 2026-09-10

## Executed
- TypeScript strict type check: passed.
- Unit/mock tests: 9/9 passed (approval explicitness, exact-plan binding and one-use consumption; workflow draft/validation/diff; offline CRUD/path traversal; mode/TLS configuration).
- Production build: passed.
- MCP stdio smoke integration: initialized a real SDK client against the built server, discovered 26 tools, and called `n8n_status`: passed.
- Package structure validation: passed.
- `npm pack`: passed.

## Mocked/offline
Workflow and REST behavior tests use offline artifacts and unit-level objects. No live n8n endpoint, API key, OAuth session, queue worker, Cloud account, credential, data table, agent or external service was available.

## Not claimed as tested
Real n8n MCP authentication, live REST CRUD, Cloud/self-hosted permission scopes, workflow execution/test side effects, queue mode, community package installation, agent calls, and real data-table row operations require an authorized n8n instance. The adapters return explicit backend/version/auth errors rather than simulating success.
