# Security review

- **Authentication/authorization:** official MCP token/OAuth and REST API keys are passed only to their configured origin. n8n remains authoritative for scopes and resource permissions.
- **TLS:** remote plaintext HTTP is refused. Plain HTTP is allowed only for localhost with explicit `N8N_ALLOW_INSECURE_LOCALHOST=true`.
- **Secrets:** environment variables are never returned; audit recursively redacts token/secret/password/API-key/credential-like keys. Credential-listing paths request metadata, not decrypted values. Generic mutation rejects secret-like request bodies.
- **Approval bypass:** every exposed write/execute/destructive tool reconstructs an operation and consumes a single-use token bound to canonical exact parameters. Tokens expire. Plan changes invalidate approval.
- **Workflow injection:** local validation checks node identity/graph integrity. This is not a sandbox: Code, Execute Command, file and HTTP nodes can have effects. Test and execute both require approval.
- **Tool/prompt injection:** content returned by workflows/executions is data, not authority to call more tools. The skill requires a fresh plan and user approval for derived actions.
- **Path traversal:** offline IDs resolve under the configured root; escape attempts are rejected. New file creation is exclusive.
- **Logging:** stderr is reserved for MCP process diagnostics. Audit avoids credentials and exact secrets; deployments should protect the log path and define retention.
- **Public MCP exposure:** this package ships stdio only. If wrapped in HTTP, deploy authenticated TLS, origin/audience checks, request limits, and per-user authorization; never bind an unauthenticated server publicly.
- **SSRF/API misuse:** REST paths come from fixed semantic tools/enums, not an arbitrary endpoint tool. Base URL is administrator configuration.
- **Residual limitations:** the generic resource endpoints are feature/version dependent; failed endpoints are surfaced, not bypassed. Offline validation cannot prove node-version validity—official `validate_workflow`/node schemas are required before live creation.
