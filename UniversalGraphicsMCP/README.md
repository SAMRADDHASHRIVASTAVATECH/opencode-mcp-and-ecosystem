# Universal Graphics/Vision MCP

An independently installable computer-graphics and visual-computing expert MCP. It provides typed artifacts, capability discovery, safe DAG execution, raster/vector/procedural operations, optional OpenCV CV/tracking, optional OCR/video adapters, and hardware/model-provider diagnostics.

It does **not** plan artwork or control Windows. Universal Artist calls it through `visual.request/1`; approved platform capture providers supply screen frames.

## Install and run
```bash
python tools/manage.py install
python tools/manage.py init
python tools/manage.py doctor
```
Register the JSON printed by `python tools/manage.py config` with OpenCode. Entry point: `universal-visual-mcp`.

Base installation is CPU-only. OpenCV, FFmpeg, Tesseract, Blender, Inkscape, VTracer and model runtimes are optional and discovered lazily.
