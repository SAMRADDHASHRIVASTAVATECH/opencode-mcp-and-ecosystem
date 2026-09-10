# Workflow for the OpenCode agent

## 1. Confirm what the user wants
A `/image-to-3d-character` invocation provides an image (or directory / character
sheet) plus options. Default to the safest, most useful behaviour for anime
characters: `--rig --facial-rig --anime --format glb`.

## 2. Inspect the machine first
Run `python scripts/image_to_3d.py --detect`. This tells you whether Blender,
Python, an image-to-3D model, ComfyUI/SD, Inkscape and FFmpeg are present and
what the GPU/RAM look like. Do not assume. Act on the result:
- If a step's required tool is missing, tell the user exactly what is missing and
  the install command (see `references/tools.md`), and continue with whatever can
  still run. Do not pretend.
- Respect the VRAM rule (see `references/hardware.md`). On a 4 GB RTX 2050,
  prefer TripoSR / StableFast3D low; do not auto-run a ~6 GB model.

## 3. Plan (optional but recommended)
`python scripts/image_to_3d.py <image> --dry-run [options]` runs analysis +
planning and writes a report without executing heavy stages. Read it to show the
user what will happen.

## 4. Run the pipeline
```
python scripts/image_to_3d.py character.png --rig --facial-rig --anime --format glb
```
The script does the whole thing as far as the installed tools allow and prints
the report path + final status. If reconstruction is not possible locally, it
will tell you to install the lightest model or pass `--mesh <existing.glb>`.

## 5. Read the report
Open `<project>/report.md` (path printed on stdout). Review `warnings`,
`armature_status`, `facial_rig_status`, `validation_ok`. Give the user a clear,
honest summary: what succeeded, what was skipped, and what they should do next.

## 6. Failure handling
- Never claim a mesh or a "successful" rig that was not actually produced.
- If a stage failed, intermediate files remain in `<project>/` for debugging; say
  so and offer the exact fix/install command.
- If the model is not animation-ready (e.g. no separate eye/mouth geometry),
  state it and offer the manual fallback from `references/rigging.md`.

## Note on Blender
`scripts/blender/run.py` only runs inside Blender. The launcher invokes Blender
headlessly when it is installed. The rig/cleanup/export code cannot be executed
in a CPU-only, no-Blender CI environment — validate the Blender leg on the
user's machine (see `references/index.md`).
