# Hardware detection & the local-first VRAM rule

## Detection
`python scripts/image_to_3d.py --detect` reports:

- **RAM** (psutil): total / available GB.
- **GPU** via `nvidia-smi` when present (name, total & free VRAM); falls back to
  a `torch.cuda` probe. If neither reports a GPU, the skill assumes CPU-only and
  will not try to run a GPU-only model.

## Decision rule used before ANY heavy model
1. Detect GPU/RAM.
2. Look up the model's weights + realistic peak VRAM need (from `registry.py`).
3. Prefer lightweight / quantized variants first.
4. Only if VRAM budget is insufficient do we use CPU (and we warn it is slow);
   if even RAM/CPU is impractical we stop and say so.
5. Clear "cannot realistically run locally" report is produced rather than a fake
   attempt.

Concretely, the skill keeps ~0.6 GB VRAM headroom and treats the realistic GPU
budget as `free VRAM − 0.6 GB`. A model runs on GPU only if
`weights + 0.6 GB ≤ budget`. `--cpu` forces CPU; `--gpu` requests GPU but falls
back to CPU (with a warning) if no GPU is present.

## Target machine (typical) behaviour
RTX 2050 4 GB / 16 GB RAM:

- Single-image **TripoSR** (~1–2 GB) and **StableFast3D low** fit comfortably and
  are preferred.
- **Zero123plus** (~4.5 GB) is marginal → skill steers to the lighter option or
  CPU offload.
- **Trellis / big Flux-style** image-to-3D are reported as too heavy for 4 GB and
  the skill suggests the lightest viable alternative rather than crashing.

## Reporting
If a step can't run locally the stage is marked `skipped`/`needs_mesh` with a
plain-language reason and a suggested lighter alternative. No image is uploaded
to any external service unless `allow_external_service` is true.
