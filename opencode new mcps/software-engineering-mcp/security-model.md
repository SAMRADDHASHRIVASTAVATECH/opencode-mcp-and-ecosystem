# SE MCP — Security Model

- `SE_MCP_ROOT` sandbox for all file I/O
- `SE_MCP_READ_ONLY` blocks writes/builds
- No arbitrary shell; build/test/run use argv lists from detected project type
- Git: status/diff/log only unless `confirm=true` for commit; never force-push
- Secret redaction in command logs
- Dependency install (`npm install`, `pip install`) requires `confirm=true`
- Do not vendor or print signing passwords
