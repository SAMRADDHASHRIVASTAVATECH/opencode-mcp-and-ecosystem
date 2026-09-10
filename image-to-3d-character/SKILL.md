---
name: image-to-3d-character
description: Convert a 2D AI-generated anime character image (PNG/JPG/WebP, EPS/SVG, or a character-sheet directory) into a usable, animation-ready 3D character/object through a complete local 2D->3D pipeline: analysis, background cleanup, multi-view references, image-to-3D reconstruction, mesh repair, retopology, UVs, textures, anime materials, humanoid + basic facial rigging, validation and export (GLB/GLTF/FBX/OBJ).
---

# image-to-3d-character

Turn a 2D character image into a usable 3D character/object suitable for
animation, preferring tools that run **locally** on the user's computer. The
skill performs the full pipeline for the user where the installed tools allow it
and honestly reports anything that cannot run.

## When to invoke
Invoke this skill when the user wants to:
- convert a character drawing / AI image into a 3D model or character,
- prepare a character for animation, rigging or a game engine,
- generate a 3D character from a single view or a character sheet,
- and they are working on a local machine (target: Windows, NVIDIA RTX 2050
  4 GB VRAM, 16 GB RAM, Python 3.12).

## Invocation
Run it as a slash command, e.g.:

```
/image-to-3d-character character.png
/image-to-3d-character character.png --rig --facial-rig --anime --format glb
/image-to-3d-character refs/ --output hero --format fbx
/image-to-3d-character character.png --cpu
/image-to-3d-character character.png --mesh existing.glb   # skip reconstruction
```

### Options
- `--output <name>` / `-o` — project/output directory name.
- `--quality {draft|balanced|high}` — reconstruction/processing fidelity.
- `--rig` / `--no-rig` — build a humanoid armature (default: rig).
- `--facial-rig` / `--no-facial-rig` — attempt basic eye/mouth/expression
  controls (default: on, reported honestly).
- `--anime` / `--no-anime` — apply anime/cel-shaded materials.
- `--low-poly` — decimate/optimise the mesh.
- `--format {glb|gltf|fbx|obj|stl}` — export format (default glb; STL only when
  explicitly requested).
- `--cpu` / `--gpu` — force device; default `auto` detects hardware.
- `--mesh <file>` — skip image-to-3D and process an existing mesh.
- `--dry-run` — analysis/planning + report only, no heavy execution.
- `--allow-external` — allow an explicitly configured external image-to-3D
  service (off by default; images are never uploaded without it).

## Required inputs
A PNG/JPG/WebP anime character image, an EPS/SVG version (used as a vector
reference when present), or a **directory** of character references. Optional
front/side/back character sheets are handled: the skill splits wide multi-panel
sheets and picks the best front view. When multiple images exist it picks the
most suitable reconstruction source automatically.

## How to run the tooling
All automation lives in `scripts/` and needs no install:

```
# inspect machine (tools + hardware) — always do this first
python scripts/image_to_3d.py --detect

# dry-run plan + report (no heavy steps)
python scripts/image_to_3d.py <input> --dry-run

# full pipeline
python scripts/image_to_3d.py <input> [options]

# offline self-test of the skill
python scripts/selfcheck.py
```

Output goes to a dedicated project dir (`<state_root>/projects/<name>/`); the
**original image is never modified**. The final report is
`<project>/report.md` / `report.json` (the launcher prints the path).

## Tool detection — do this before running anything heavy
Run `--detect` and read the result. The skill looks for (PATH first, then common
Windows locations, then `config.json` overrides): Blender, Python, Inkscape,
FFmpeg, ComfyUI, Stable Diffusion checkpoints, python modules (PIL, numpy,
opencv, rembg/onnxruntime, torch, trimesh) and any local image-to-3D model
(TripoSR / Zero123plus / Trellis / StableFast3D).

Guidance:
- **Blender present** → the full clean/rig/material/export leg runs headlessly
  (`scripts/blender/run.py`).
- **Blender missing** but a reconstruction mesh exists → mesh cleanup/rig/export
  can't run; tell the user the exact install step and stop that leg honestly.
- **Image-to-3D model missing** → the skill says the lightest option for 4 GB
  and its install command (see `references/models.md`), and the mesh stage is
  reported `needs_mesh`. Offer `--mesh <file>`.
- If a required tool is missing, explain exactly what is missing and provide the
  installation command/instructions (see `references/tools.md`). Never assume a
  tool exists or fabricate results.

## VRAM / local-first rule
Before running any model: detect GPU/RAM, check the model's VRAM requirement,
prefer lightweight/quantized models, use CPU only when practical, and clearly
report when a step can't realistically run locally. On the 4 GB RTX 2050 prefer
TripoSR (~2 GB) or StableFast3D low; do not auto-run ~6 GB models. See
`references/hardware.md`.

## Pipeline execution (what the skill does)
The orchestrator runs stages and **continues past failures** (records them,
keeps intermediates, reports): detect tools → hardware → analyse image →
background removal → multi-view reference generation (if single view) →
image-to-3D reconstruction → Blender mesh repair/optimise/UV → anime materials →
humanoid rig (+ facial controls where possible) → validation → export → report.
Full stage detail: `references/pipeline.md`.

### Image analysis
The skill inspects silhouette, body orientation/facing, pose, resolution,
background type, colourfulness/dominant colours, and suitability; removes or
isolates backgrounds; and recommends/generates extra views when only one view
exists and more would materially improve reconstruction.

### Reference generation
When only a single image exists, it plans front / 3/4 / side / back views and —
if a local ComfyUI + Stable Diffusion runtime is present and running — attempts
to generate them. Identity is preserved (no redesign): the templates in
`templates/view_prompt.txt` are used. If no local runtime exists, the skill
reports the views are still needed and provides the prompts instead of inventing
output.

### Reconstruction
The skill supports multiple backends (not hard-coded): local installed model →
best lightweight local model for the hardware → Blender-assisted → external
service **only when explicitly allowed**. It never silently uploads images.

### Blender processing
Automated via `scripts/blender/run.py`: import, scale normalisation, orientation,
cleanup, removal of disconnected junk, hole repair where practical, normal
correction, decimation, smoothing, UV generation, material/texture assignment,
basic anime/cel setup, and logical naming/collections (`Character`, `Head`,
`Face`, `Hair`, `Body`, `Clothes`, `Eyes`, `Mouth`, `Accessories`, `Armature`).

### Rigging
Humanoid armature + automatic weights + basic IK (arms/legs/spine/neck/head).
For anime characters it also attempts basic facial controls (eye movement,
blinking, mouth opening, expressions). If automatic rigging fails it preserves
the clean mesh and gives a clear manual-rig fallback (`references/rigging.md`).
A model is never called animation-ready unless validated.

### Validation
Real checks (mesh present/non-empty, normals, materials, texture when expected,
armature/weights when rigging requested, exported file exists, reasonable
polygon count) are merged from the file validator + the Blender result. The final
report includes source image, reconstruction method, generated files, polygon
count, texture resolution, object count, armature status, facial rig status,
export formats, warnings/errors, and recommended next steps
(`references/validation.md`).

## Failure handling
- A failed stage never destroys the project; intermediate files are kept in the
  project dir and logged for debugging.
- Never fabricate a successful mesh/rig/result. Report hardware/install limits
  and the lightest viable alternative.
- Never overwrite the original image.

## Output structure
```
<state_root>/projects/<name>/
  logs/pipeline.log
  cleaned/            background-removed / panel-cropped images
  references/         generated multi-view images or prompts
  recon/              raw reconstructed mesh
  blender/            processed mesh + blender_result.json
  report.json         machine-readable final report
  report.md           human-readable final report
```
