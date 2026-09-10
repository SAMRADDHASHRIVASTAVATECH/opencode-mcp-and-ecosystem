# Examples

Run from the repo root so the package is importable:

```bash
# deterministic offline tour of the whole system
PYTHONPATH=src python examples/quickstart_offline.py

# 18-point selfcheck (offline) — exits non-zero on any failure
PYTHONPATH=src python examples/selfcheck.py

# Drive the MCP server as a client (offline)
PYTHONPATH=src python examples/mcp_client.py --offline --goal status
PYTHONPATH=src python examples/mcp_client.py --offline --goal msg

# Remote Touchpad companion (phone -> this PC); uses a stub unless AC_RT_BIN set
PYTHONPATH=src python examples/remote_touchpad_demo.py

# Authorization policy for destructive ops
PYTHONPATH=src python examples/custom_authorizer.py
```

Or install the package (`pip install -e .`) and run without `PYTHONPATH`.

## Running the MCP server
```bash
android-control-mcp --offline            # console script
python mcp_server.py --offline           # direct
python -m android_control --mcp --offline
```
Point any MCP client at one of these as a stdio server. See `docs/MCP.md`.
