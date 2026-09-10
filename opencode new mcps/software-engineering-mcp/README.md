# Universal Software Engineering MCP

The **software-development capability layer** for this ecosystem. It discovers, routes, scaffolds, builds, tests, diagnoses, and audits **general software** — and **refuses to duplicate** the Office, Database, Windows, and Android specialists.

Companion **skills** live in `../skills/` (how to decide). This package is the operational MCP (what to execute).

## Install / run

```bash
pip install -e ./software-engineering-mcp
python -m se_mcp
```

Listed in workspace `mcp.json` as `software-engineering`.

## Tools

`se_detect_environment` `se_ecosystem` `se_route` `se_plan` `se_discover_project` `se_create_project` `se_build` `se_test` `se_run` `se_deps` `se_analyze` `se_diagnose` `se_security_audit` `se_document` `se_package` `se_git` `se_quality` `se_ascii_tree` `se_sdlc` `se_launch_gui`

ASCII Tree Creator and Universal SDLC Generator: headless tools above, plus tkinter GUIs in `apps/` (`python apps/ascii_tree_creator.py`, `python apps/sdlc_generator.py`).

Templates (not MERN-only): `python-cli`, `python-lib`, `python-fastapi`, `python-flask`, `python-desktop`, `node-cli`, `node-express`, `node-library`, `static-web`, `java-cli`, `c-cli`, `go-cli`, `rust-cli`.

Android / Office / SQL / Windows admin → other MCPs (`se_route` tells you).
