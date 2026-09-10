# Universal Artist MCP

An independently installable professional artistic-reasoning and artwork-orchestration MCP. It maintains editable artwork state, plans workflows, adapts to applications, generates drawing trajectories, critiques outputs, and emits approval-gated control envelopes.

It does **not** implement graphics algorithms or Windows input. It delegates visual computation to Universal Graphics/Vision MCP using `visual.request/1`, and physical actions to an authorized Windows Live Control Agent using `live-control.action/1`.

## Install and run
```bash
python tools/manage.py install
python tools/manage.py init
python tools/manage.py doctor
```
Register the JSON printed by `python tools/manage.py config` with OpenCode. Entry point: `universal-artist-mcp`.
