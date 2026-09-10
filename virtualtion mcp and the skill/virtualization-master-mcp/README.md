# Virtualization Master MCP

A local stdio MCP server for truthful VM discovery, exact planning, approval-gated execution, guest readiness, bounded jobs and diagnostics. Supports dynamically detected VirtualBox, Hyper-V, VMware `vmrun`, libvirt and WSL. Node.js 20+.

## Install and run
```bash
npm install
npm run build
node lib/index.js
```
OpenCode local MCP configuration:
```json
{"mcp":{"virtualization-master":{"type":"local","command":["node","/absolute/path/virtualization-master-mcp/lib/index.js"]}}}
```

## Safety model
All mutation and guest execution follows `plan_operation` → human inspection/approval → `approve_operation` → `execute_operation`. Approval is bound to the exact plan digest, expires after 60 seconds, and is single-use. Commands use argv spawning (`shell:false`). There is no arbitrary HOST shell tool. `HOST` and `GUEST` contexts are mandatory. A powered-on VM is not considered guest-ready until the configured control mechanism is verified.

Never put passwords or private-key contents into MCP arguments. SSH uses an existing key path and strict host-key checking; VirtualBox guestcontrol accepts a password-file path. Output is bounded to 200 KB per stream. Current-process jobs are not durable across server restarts.

See `docs/ARCHITECTURE.md`, `docs/CAPABILITIES.md`, `docs/SECURITY.md`, and `docs/RESEARCH.md`.
