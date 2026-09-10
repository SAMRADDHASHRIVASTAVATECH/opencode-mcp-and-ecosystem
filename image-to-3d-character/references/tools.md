# Tool discovery & installation

The skill discovers tools automatically (never assumes a path). Run:

```
python scripts/image_to_3d.py --detect
```

It prints JSON plus a short table of what is found vs missing for: Blender,
Inkscape, FFmpeg, ComfyUI, Stable Diffusion checkpoints, Python, and python
modules (PIL, numpy, opencv, rembg, onnxruntime, torch, trimesh), plus any
locally installed image-to-3D models (TripoSR / Zero123plus / Trellis /
StableFast3D).

The skill checks PATH first, then common Windows install locations, then the
`override_*` keys in `config.json`. Only *verified* (file-present) results are
reported as found.

## If something is missing

Give the user the exact command for their machine.

- **Blender** — needed for mesh cleanup, rigging, materials, export.
  Install Blender 4.x. On Windows: download the installer from blender.org, or
  `winget install BlenderFoundation.Blender`. Note the exe path if not on PATH
  (the skill searches `C:\Program Files\Blender Foundation\...` automatically;
  otherwise set `override_blender` in config.json).
- **Python** — the skill runs on the user's installed Python 3.12. Not found →
  install from python.org or `winget install Python.Python.3.12`.
- **Inkscape** — used only if EPS/SVG vector reference needs rasterizing.
  `winget install Inkscape.Inkscape`, or inkscape.org.
- **FFmpeg** — optional, used to build reference-sheet previews/GIFs if useful.
  `winget install Gyan.FFmpeg`.
- **rembg + onnxruntime** — optional high-quality AI background removal.
  `pip install rembg onnxruntime` (downloads a ~170 MB U²-Net on first use).
  If absent, the skill falls back to a simple colour-key removal only when it
  can, and otherwise tells you background removal was skipped.
- **trimesh** — optional file-level mesh validation.
  `pip install trimesh`.
- **Image-to-3D model** — see `models.md`. If none is installed and no Blender
  manual mesh exists, the skill honestly reports that reconstruction cannot run
  and gives install instructions for the lightest viable option for 4 GB.

Important: the skill **never fabricates** a missing tool or a produced mesh. If a
required tool is absent it says exactly what is missing and how to install it.
