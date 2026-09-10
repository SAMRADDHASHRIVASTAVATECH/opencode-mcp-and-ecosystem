# Troubleshooting
- MCP absent: run the launcher manually; use absolute paths in OpenCode.
- Avatar unavailable: check port 8765 and call `start_person` first.
- Dialogue fallback text: no provider is configured; this is intentional.
- Memory locked: stop duplicate server processes; SQLite supports one local runtime design.
- GUI delegation fails: diagnose the separate computer-use MCP and platform permissions.
- Wrong memory: use `correct_memory`; use `forget_memory` for deletion.
- Immediate stop: call `emergency_stop` and independently stop any active computer-use session.
