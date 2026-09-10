# Pipeline (stage-by-stage)

Driven by `scripts/i3dc/pipeline.py`. Every stage is logged to
`<project>/logs/pipeline.log` and recorded in the report. A failed stage does not
destroy the project — later stages that can still run are attempted, and
intermediate files are kept for debugging.

Project/output lives under a dedicated directory:
`<state_root>/projects/<name>/` (state root from `config.json`/`state_root`,
default under the OS app-data dir). The **original image is never modified** — all
derivatives are written into the project `cleaned/`, `references/`, `recon/`,
`blender/` folders.

1. **detect_tools** — discover Blender/Python/Inkscape/FFmpeg/ComfyUI/SD +
   python modules + local image-to-3D models.
2. **hardware** — GPU/RAM detection and VRAM feasibility summary.
3. **collect_inputs** — gather the image(s)/directory/character sheet(s). If a
   directory is given, the most suitable (front, isolated, high-res) raster is
   chosen as the reconstruction source; SVG/EPS noted as vector references.
4. **analyze_image** — resolution, background type, silhouette, colourfulness,
   dominant colours, approx facing (front/frontish/side), suitability verdict,
   warnings. Splits a wide multi-panel character sheet into panels if detected.
5. **background_removal** — removes an opaque/photo background when a removal
   engine is present (rembg preferred, opencv colour-key fallback). Honest if
   skipped. (Skipped on `--dry-run`.)
6. **reference_generation** — if only one view exists (esp. front-only or
   side), plans front / 3/4 / side / back views. When a local image runtime
   (ComfyUI + an SD checkpoint) is present and running it tries to generate
   them; otherwise it outputs identity-preserving prompts (see
   `templates/view_prompt.txt`) and reports views are still needed.
7. **reconstruction** — run the chosen image-to-3D backend (see models.md) or use
   `--mesh`. Outputs a raw mesh (e.g. `raw_mesh.glb`). Never fabricates.
8. **blender_process** — if Blender is present and a mesh exists, run
   `scripts/blender/run.py` headlessly to:
   - import + merge meshes, name the object `Character`
   - scale-normalise (~1.8 units), correct orientation
   - remove disconnected junk geometry, weld doubles, fix normals
   - cap boundary holes where practical
   - auto-smooth; decimate if `--low-poly`/`--poly-target`
   - generate UVs (smart-project)
   - anime/cel material + optional texture assignment
   - organise objects into logical collections (`Character`, `Head`, `Body`,
     `Clothes`, `Eyes`, `Armature`, ...)
   - rig a humanoid armature + automatic weights + basic IK (see rigging.md)
   - basic facial/blend-shape controls where geometry allows (never overclaims)
   - validate and export (GLB/GLTF/FBX/OBJ; STL only on explicit request)
   Writes `<project>/blender/blender_result.json` with details.
   If Blender is missing it reports the exact install need and does not proceed.
9. **validate** — real checks (mesh file exists & non-empty; geometry parses;
   normals valid; reasonable polygon count; materials assigned; texture present
   when expected; armature + weights present when rigging requested) merged from
   the file validator + the Blender validation result.
10. **report** — writes `report.json` + `report.md` (see validation.md) and
   recommended next steps.

`--dry-run` performs detection/hardware/analysis/planning and writes a report but
runs no heavy stage (no background removal, no Blender, no model). `--detect`
only inspects the machine and exits.
