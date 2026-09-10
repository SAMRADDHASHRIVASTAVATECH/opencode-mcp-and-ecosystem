# image-to-3d-character — references

Guides the OpenCode agent and a human through the pipeline on the target
machine (Windows, NVIDIA RTX 2050 4 GB, 16 GB RAM, Python 3.12).

| File | Purpose |
|---|---|
| [tools.md](tools.md) | Tool discovery + install commands when something is missing |
| [hardware.md](hardware.md) | GPU/RAM detection + the local-first VRAM decision rule |
| [models.md](models.md) | Image-to-3D backends that fit 4 GB, and how they are chosen |
| [pipeline.md](pipeline.md) | Stage-by-stage explanation of the automation |
| [rigging.md](rigging.md) | Humanoid + facial rig details and the manual fallback |
| [validation.md](validation.md) | Checks performed and the final report format |
| [workflow.md](workflow.md) | How OpenCode should invoke the skill end-to-end |

All scripts live in `scripts/`:
- `image_to_3d.py` — thin launcher (no install needed)
- `selfcheck.py` — offline self-test
- `i3dc/` — the automation engine
- `blender/run.py` — Blender headless processing/rig/export script
