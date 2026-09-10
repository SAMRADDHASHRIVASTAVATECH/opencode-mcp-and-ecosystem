# Windows Acceptance Runbook — RTX 2050 (4 GB VRAM / 16 GB RAM)

This is the **on-device** acceptance procedure. The build/CI sandbox is CPU-only
(no CUDA), so the following must be run on the actual target machine to validate
real GPU generation. Everything before step 5 can also be verified anywhere.

> Honesty contract: never pass a demo image off as AI output. Real AI output
> requires (a) an installed + verified model and (b) a running real backend. The
> `generate_image` family refuses otherwise.

## 0. Prerequisites
- Windows 10/11, NVIDIA RTX 2050 laptop GPU (4 GB VRAM), 16 GB RAM, ~30 GB free disk.
- Python 3.10+ on PATH, `git`.
- NVIDIA driver + CUDA toolkit matching the PyTorch build you install.

## 1. Install the package

```powershell
cd C:\olcap\olcap-image-generator
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e .            # control plane + Pillow
pip install -e ".[inference]"   # torch + diffusers (GPU build)
pip install -e ".[comfy]"       # websocket client
```

Confirm GPU torch sees the card:

```powershell
python -c "import torch; print(torch.__version__, torch.cuda.is_available(), torch.cuda.get_device_name(0))"
# expected: ... True, and a string containing e.g. "RTX 2050"
```

## 2. Config
Copy `configs\config.example.yaml` to your state dir
(`%USERPROFILE%\olcap\image-generator\config.yaml`). Set:

```yaml
runtime:
  backend: auto          # auto prefers ComfyUI when running
  comfyui_port: 8188
generation:
  default_quality: maximum
models:
  auto_install_models: true   # only if you authorize downloads
```

## 3. Offline self-test (optional here)
```powershell
python scripts\selftest.py
```
Expect `RESULT: PASS`. Note it will report `ai_generation_ready: False` because
no real backend/model is loaded yet — that is correct.

## 4. Runtime: ComfyUI (preferred)
Install and start via the server, or manually:
```powershell
olcap-image-generator --transport streamable-http --http-port 8766
# from any MCP client call:
#   install_runtime(backend="comfyui")  -> job -> get_job_progress
#   start_runtime(backend="comfyui")
#   runtime_status()  -> comfyui.health == true
```
(Equivalent manual install: clone comfyanonymous/ComfyUI, create a venv, `pip
install -r requirements.txt`, and add its `models/checkpoints` path as your
`models_dir`.)

## 5. Install a verified model
Use `recommend_model(objective="quality")` to see what is feasible on 4 GB. A
reasonable target is **SDXL @ q8** or **SD1.5 @ fp16/q8** with CPU offload (the
memory planner will size it).

Provide a verified source. Two ways:

**A. Local, hash-verified checkpoint** (safest, no network gate needed):
```text
install_model(
  name="SDXL base",
  family="sdxl",
  source="C:\models\sdxl_base_1.0.safetensors",
  expected_sha256="<real sha256 of that file>",
  quant="q8")
verify_model(model_id="sdxl-q8")
```

**B. Authorized download** (set `auto_install_models: true` + allowed host):
```text
install_model(name="SD1.5", family="sd1.5",
              source="https://huggingface.co/.../v1-5-pruned.safetensors",
              expected_sha256="<real sha256>")
```

Then point the ComfyUI workflow template at the actual file name: edit the
installed checkpoint/upscale names in
`%USERPROFILE%\olcap\image-generator\workflows\sdxl.txt2img.json` (and
`.img2img.json`, `.inpaint.json`, `.upscale.json`) to match your checkpoint /
ESRGAN file names. Restart ComfyUI.

## 6. Real generation acceptance

For **each** of the following, the result must be a real image file at
`job.output.path` plus a `.json` metadata sidecar, and the image must reflect the
prompt (no crash, no all-noise image):

1. `health_check()` → `ai_generation_ready: true`.
2. `generate_image(prompt="a red fox in snow", quality="maximum")`
   → poll to `completed`; verify ~1024×1024 file + metadata.
3. Re-run with a fixed `seed` → identical image (determinism check).
4. `image_to_image(...)` on a generated image, low `strength`.
5. `edit_image(instruction="make it night time", input_image=...)`.
6. `inpaint_image(...)` with a source image + mask (use the `.inpaint.json`
   workflow + an inpainting checkpoint).
7. `upscale_image(input_image=..., factor=2)` (ESRGAN workflow if installed).
8. `optimize_for_memory()` then `recommend_model(objective="memory")` — confirm a
   lower VRAM footprint and that generation still completes.

Record per-case: elapsed seconds, peak VRAM/RAM (`get_job_progress` reports),
steps, and whether output was visually valid.

## 7. Failure-mode acceptance
- Stop ComfyUI, then `generate_image` → job **fails** with a typed error
  (`NO_BACKEND_AVAILABLE` / `RUNTIME_NOT_RUNNING`); no fake image is produced.
- Run `diagnose()` → confirm GPU present, CUDA ok, model ok, comfy running.
- `cancel_job(job_id)` during a long generate → job becomes cancelled/stopped.

## 8. Report
Fill the per-case table above with measured VRAM/RAM/it/s and image checks. If
step 4 GPU line prints `cuda.is_available() == True`, steps 5–7 succeed with real
visual output, and step 7 failure modes behave honestly, the target is accepted.

If the sandbox environment is used for anything, keep the demo backend quarantined
and never report a `demo` image as AI-generated.
