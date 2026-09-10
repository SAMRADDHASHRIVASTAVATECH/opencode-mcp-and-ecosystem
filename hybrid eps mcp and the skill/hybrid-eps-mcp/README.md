# Hybrid EPS MCP
Production-oriented headless MCP extracted and expanded from the supplied Tkinter Hybrid EPS Generator. It performs safe image inspection, four edge methods, morphology, quantitative analysis, true OpenCV contour vectorization, hybrid raster/vector EPS/PDF/SVG/PNG export, exact approvals, bounded batch jobs and verification.

## Install
```bash
python -m venv .venv
.venv/bin/pip install -e .
HYBRID_EPS_ROOT=/absolute/image/workspace .venv/bin/hybrid-eps-mcp
```
Windows uses `.venv\Scripts\`. OpenCode example is in `examples/opencode.json`.

Workflow: `eps_inspect_image` → `eps_compare_methods`/`eps_analyze_edges` → `eps_validate_settings` → `eps_plan_export` → show plan and obtain explicit approval → `eps_approve` → `eps_execute` → `eps_get_job`. Every path is confined to `HYBRID_EPS_ROOT`; every write requires a 60-second single-use approval.

Read `docs/CODEBASE_ANALYSIS.md`, `CAPABILITY_MAP.md`, and `RESEARCH.md` for the exhaustive analysis and limitations.
