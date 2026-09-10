# Windows System MCP — Security Model

- No user-supplied script execution
- CIM classes allowlisted
- Event log names allowlisted (System, Application, Setup, PrintService/Admin if present)
- Timeouts (default 30s)
- confirm=true for mutations
- WIN_MCP_ALLOW_DESTRUCTIVE for spool purge / remove printer
- WIN_MCP_READ_ONLY blocks mutations
- Redact passwords if they ever appear in CIM properties
- ComputerName remoting optional and disabled unless WIN_MCP_ALLOW_REMOTE=1
