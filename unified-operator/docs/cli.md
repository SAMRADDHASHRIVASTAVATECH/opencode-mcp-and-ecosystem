# CLI reference

Two equivalent entry points (both are stdio MCP servers):

```bash
unified-operator-mcp                 # console script from pip install -e .
python -m unified.main               # from repo root, PYTHONPATH=src
```

## Flags

```
--offline       Force deterministic offline/mock mode for every connector.
--list-tools    Print the tool manifest (name + short description) as JSON and exit.
--help          Show this help.
```

`--offline` is equivalent to setting `UNIFIED_OFFLINE=1`.

## Examples

```bash
# Just inspect what tools exist (nice for config validation):
python -m unified.main --list-tools

# Run the MCP server in offline/demo mode:
python -m unified.main --offline

# Run live (uses whatever env credentials are present; unconfigured connectors are mock):
python -m unified.main
```

## Environment

Runtime behaviour is controlled entirely by env (see `.env.example` and docs/setup.md):
`UNIFIED_OFFLINE`, `UNIFIED_STATE_DIR`, `UNIFIED_LOG_DIR`, `UNIFIED_TZ`,
`UNIFIED_PERM_*`, `UNIFIED_CALL_*`, `GOOGLE_*`, `DISCORD_TOKEN`, `VOICE_*`, `OPENCLAW_*`.

State/logs default to `~/.unified-operator/` (`operator.db`, `logs/`). Override with
`UNIFIED_STATE_DIR`/`UNIFIED_LOG_DIR` if you want them inside a project.
