# Universal Decompiler MCP
A local, authorized, **static-first** reverse-engineering orchestration server. It identifies unknown files, maps formats/runtimes/architectures to capabilities, discovers local tools, plans curated on-demand installs, routes multiple analyzers, preserves artifacts, labels uncertainty and never executes the target.

## Directories
- Source: this project
- User targets: `DECOMPILER_TARGET_ROOT` (default `/home/user/decompiler-targets`)
- Analysis artifacts: `DECOMPILER_ANALYSIS_ROOT` (default `/home/user/decompiler-analysis`)
- External tools/cache/registry: `DECOMPILER_TOOL_ROOT` (default `/home/user/decompiler-tools`)

## Install and configure
```bash
python -m venv .venv
.venv/bin/pip install -e .
.venv/bin/universal-decompiler-mcp
```
See `examples/opencode.json`. Place authorized samples under the target root. Start with `identify_file`, then `route_analysis`. `universal_decompile` returns a plan; show it to the user, call `approve_operation`, then `execute_operation`, and poll `get_job`.

Tool installation is never silent. `plan_install_tool` only produces an auditable plan. Automatic installation is limited to curated pinned PyPI or .NET recipes into the external tool root. Large/manual tools require the operator to verify official releases/checksums. No unknown target is ever launched.
