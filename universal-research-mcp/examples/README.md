# Examples

- `example_client.py` — talk to the MCP stdio server the way a real MCP client
  would (spawn `mcp_server.py`, exchange newline JSON-RPC, call a tool, read a
  resource, get a prompt). Works online or with `UR_OFFLINE=1`.
- `quickstart.py` — direct Python-API tour of the engine (search, fact-check,
  plan, deep research) in offline mode.

## Note on paths

Run these from the repo root and make the package importable, e.g.:

```bash
pip install -e .          # preferred
# or, without installing:
PYTHONPATH=src python examples/quickstart.py
PYTHONPATH=src python examples/example_client.py --offline
```
