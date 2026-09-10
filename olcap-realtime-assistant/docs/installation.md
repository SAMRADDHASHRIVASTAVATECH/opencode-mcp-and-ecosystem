# Installation

Primary host: **Windows 10/11** (also runs on Linux/macOS). Components are Python; no
Linux-only utilities are assumed.

## 1. Core (MCP + control plane)

```bash
python -m pip install -e <project-path>            # e.g. olcap-realtime-assistant
python -m olcap_realtime.main --list-tools
```

`-e` is a normal editable install; the console script `olcap-realtime-assistant-mcp` is
registered.

## 2. Optional real-capture/inference extras

```bash
python -m pip install -e ".[audio,stt,screen]"     # sounddevice, faster-whisper, mss
# vision (for screen frame analysis):
python -m pip install opencv-python-headless       # or ".[vision]"
```

Each extra is optional. Without it the corresponding capability reports `UNAVAILABLE`
honestly (e.g. mic tools say "sounddevice not installed").

## 3. Run the MCP server

```bash
olcap-realtime-assistant-mcp                        # stdio MCP server
# or
python -m olcap_realtime.main
# inspect health/diag without hardware assumptions:
python -m olcap_realtime.main --health
python -m olcap_realtime.main --diag
```

## 4. Verify

```bash
python -m unittest discover -s tests                # 25 offline tests
python examples/client_demo.py
```

## 5. Node.js (optional)

OpenCode runs under Node; this project is a stdio MCP server, so OpenCode spawns it via
`command` in the MCP config (no Node runtime needed by the Python package itself).

## Dependency map (pyproject.toml)

* core: `mcp`, `pydantic`, `httpx`, `numpy`
* `[audio]`: `sounddevice`
* `[stt]`: `faster-whisper`
* `[screen]`: `mss`, `pillow`
* `[vision]`: `opencv-python-headless`

Secrets come only from environment variables / secure storage (`.env`), never code.
