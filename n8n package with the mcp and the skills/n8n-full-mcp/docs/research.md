# Research audit — 2026-09-10

## Current platform
n8n 2.38.x is current in the environment research window. The platform spans visual workflows, core/integration/community/custom nodes, expressions, triggers/webhooks, executions, credentials, variables, tags, folders, projects/RBAC, data tables, source-control environments, package import/export, queue mode/workers, task runners, binary storage, APIs/CLI, Cloud and self-hosted deployment. AI functionality includes LangChain-based agent/model/tool/memory/vector-store/retrieval nodes, MCP client/server nodes, evaluation and agent management. Edition, license, rollout flags and permission scopes alter availability.

Queue mode separates the main/webhook processes from workers. All processes must share the credential encryption key. Filesystem binary storage is unsuitable for queue mode unless shared/external storage is configured. MCP Server Trigger persistent transports need routing to a single dedicated webhook replica in multi-replica queue deployments.

## Official instance-level MCP
Instance-level MCP is a remote Streamable HTTP endpoint at `/mcp-server/http`, enabled by an owner/admin. OAuth is preferred; personal access token is supported and rotatable. Visibility is user/scopes-based. `search_workflows` can preview accessible workflows, but full access/modification/execution generally requires MCP exposure. Project/folder exposure arrived in 2.24; auto-expose is a later opt-in rollout.

Current official tool families include workflow search/details/execution/test/publish/archive, project/folder/tag search, executions, credential metadata, SDK/node discovery and validation, atomic targeted workflow updates, data tables, and (on 2.34+) preview agent management. Important version gates: workflow builder 2.12/2.13, test/pin data 2.15, execution search 2.20, credentials 2.21, node validation 2.25.1, tags/resource exploration 2.27, agents 2.34 and agent call 2.35. `call_agent` and workflow tests can cause real side effects.

This differs from:
- **MCP Server Trigger**: one workflow exposes its connected tools as a custom MCP server; Streamable HTTP/SSE, not stdio.
- **MCP Client / MCP Client Tool**: n8n calls external MCP tools, as a normal workflow step or an AI-agent tool.
- **Instance-level MCP**: centralized n8n control/build surface across explicitly exposed workflows/agents.

## Public API and CLI
The public `/api/v1` API uses `X-N8N-API-KEY` and scoped authorization. Current endpoint groups include workflows, executions, credentials, users, audit, tags, source control, variables, data tables, projects, community packages, discovery, evaluations, folders, insights, log streaming, packages, models and enterprise settings (availability varies). The current API CLI covers workflow, execution, credential, project/member, tag, variable, data-table/user/config/source-control/audit operations.

REST often covers lifecycle/admin gaps beyond instance MCP (delete/deactivate, variables, users, community packages, etc.), but the exact OpenAPI document for the connected instance is authoritative. This implementation therefore probes/fails explicitly rather than pretending every endpoint exists on every edition.

## MCP protocol and OpenCode
The TypeScript MCP SDK supports stdio for local process-spawned servers and Streamable HTTP for remote servers. HTTP+SSE is legacy. This package exposes a local stdio server and itself connects to n8n's remote instance MCP through Streamable HTTP.

OpenCode V1 uses `mcp.<name>` with `type`, command array, environment, enabled and timeout. OpenCode V2 groups servers at `mcp.servers`, uses `disabled`, and splits catalog/execution timeouts. V2 still auto-discovers `.opencode/skills/<name>/SKILL.md`.

## Primary sources
- n8n MCP setup: https://docs.n8n.io/connect/connect-to-n8n-mcp-server
- Official tool reference: https://docs.n8n.io/connect/connect-to-n8n-mcp-server/mcp-server-tools-reference
- API reference/OpenAPI: https://docs.n8n.io/connect/n8n-api/api-reference
- n8n CLI: https://docs.n8n.io/api/n8n-cli/
- Package format: https://docs.n8n.io/build/manage-workflows/n8n-packages/package-format
- Queue mode: https://docs.n8n.io/deploy/host-n8n/configure-n8n/scaling/enable-queue-mode
- MCP Server Trigger: https://docs.n8n.io/integrations/builtin/core-nodes/n8n-nodes-langchain.mcptrigger
- MCP Client: https://docs.n8n.io/integrations/builtin/core-nodes/n8n-nodes-langchain.mcpclient
- Official n8n skills: https://github.com/n8n-io/skills
- MCP TypeScript SDK: https://ts.sdk.modelcontextprotocol.io/
- OpenCode MCP: https://opencode.ai/docs/mcp-servers/
- OpenCode V2 migration: https://opencode.ai/v2/docs/migrate-v1/
