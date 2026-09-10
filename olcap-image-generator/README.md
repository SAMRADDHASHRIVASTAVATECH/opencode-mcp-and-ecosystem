# OLCAP Image Generator

An AI-controlled, **local** image-generation infrastructure exposed through an
[MCP](https://modelcontextprotocol.io) server. Another AI (or a human via any MCP
client) can fully automate local image generation on a machine that has an NVIDIA
GPU — detect hardware → choose/install/quantize a model → manage a backend
(ComfyUI preferred) → generate → edit → upscale → track jobs → diagnose.

It is backend-agnostic (ComfyUI and Hugging Face `diffusers`), quality-first by
default, and **honest by design**: it never fabricates a result. If a real model
+ backend is not available on the machine that would run inference, operations
fail with a clear typed error instead of returning a fake image.

> Real inference requires an NVIDIA GPU (target: Windows RTX 2050, 4 GB VRAM,
> 16 GB RAM). The **demo** backend exists only for offline plumbing tests and is
> quarantined behind an explicit `.allow(True)`; its outputs are labelled
> "not AI-generated" and are never returned from the production tools.

## Package layout

```
olcap_image_gen/
  config.py            Settings (env + YAML merge), path discovery, coercion
  errors.py            typed, structured error codes
  context.py           assembly of all subsystems + default-workflow seeding
  hardware/            profile model + profiler (GPU/RAM/disk/software detection)
  models/              catalog, registry (persistent), selector (feasibility),
                       manager + downloader (install/verify/resume)
  memory/              MemoryManager: quantization + GPU residency + resolution
  generation/          params (presets/normalize), service (orchestrates)
  backends/            base interface, diffusers, quarantined demo backend
  runtimes/            ComfyUI runtime + workflow client
  jobs.py              asynchronous JobManager (stages/progress/cancel)
  storage.py           usage reporting + scoped cleanup
  diagnostics.py       diagnose / self_test / repair
  server.py            FastMCP tool surface
  workflows/           packaged ComfyUI workflow JSON templates
```

## Install

```bash
# core (control plane) — runs anywhere, even CPU-only:
pip install -e .

# inference runtime — ONLY on the GPU machine that will actually generate:
pip install -e ".[inference]"   # torch + diffusers + transformers + accelerate
pip install -e ".[comfy]"        # websocket client for the ComfyUI driver
```

Requires Python >= 3.10. See `docs/WINDOWS_ACCEPTANCE.md` for the RTX 2050 run.

## Configure

Copy `configs/config.example.yaml` to your state dir and edit it. The state dir
is `$OLCAP_IMAGE_STATE_DIR`, else `%USERPROFILE%\olcap\image-generator`
(Windows) or `~/.olcap/image-generator`. Environment variables `OLCAP_IMAGE_*`
override YAML (booleans/ints coerced from strings).

**Security:** model *downloads* are disabled unless
`models.auto_install_models: true` **and** the host is in
`models.model_download_roots`. Installing a model from a local, hash-verified
file does not require the download gate.

## Run

```bash
# stdio transport (default; what MCP clients connect to)
olcap-image-generator

# streamable-HTTP server
olcap-image-generator --transport streamable-http --http-port 8766
```

Offline self-test / diagnostics (no GPU needed):

```bash
python scripts/selftest.py
```

## Tool surface

| Area | Tools |
|---|---|
| Hardware | `get_hardware_info`, `get_gpu_info`, `get_memory_status`, `get_storage_status`, `get_software_status` |
| Models | `list_models`, `search_models`, `get_model_info`, `recommend_model`, `install_model`, `verify_model`, `update_model`, `remove_model` |
| Runtime | `install_runtime`, `start_runtime`, `stop_runtime`, `restart_runtime`, `runtime_status`, `runtime_logs` |
| Generation | `generate_image`, `image_to_image`, `edit_image`, `inpaint_image`, `outpaint_image`, `upscale_image` |
| Jobs | `list_jobs`, `get_job`, `get_job_progress`, `cancel_job` |
| Diagnostics | `health_check`, `self_test`, `diagnose`, `repair`, `benchmark_model` |
| Storage | `get_storage_usage`, `cleanup_cache`, `cleanup_temp` |
| Optimization | `optimize_for_quality`, `optimize_for_speed`, `optimize_for_memory` |
| One-call | `setup_best_image_generator` |

Generation/install/runtime tools return a **job** immediately; poll
`get_job_progress` (or `get_job`) and `cancel_job` to stop.

### Recommended flow for an AI agent
1. `health_check()` — is real inference ready?
2. `setup_best_image_generator()` — hardware scan + recommendation + install plan.
3. `install_model(...)` with a **verified source** (URL or local file + sha256).
4. `verify_model(...)` → `start_runtime(backend="comfyui")`.
5. `generate_image(...)` (returns job) → poll `get_job_progress`.
6. `get_job(job_id)` → `output.path` = validated image + `.json` metadata.

## Quality presets

| Preset | Steps | Upscale | Notes |
|---|---|---|---|
| `speed` | 16 | no | fast draft |
| `balanced` | 24 | no | default-ish |
| `high` | 30 | yes | + upscale pass |
| `maximum` (default) | 40 | yes + multi-stage | best quality |

## Testing

All offline, no GPU required:

```bash
python -m pytest -q
```

Coverage: config, profile/profiler, catalog, selector, registry, model manager,
memory planner, jobs, storage, params, and a full simulated generate→file→
metadata pipeline through the quarantined demo backend. Run
`python scripts/selftest.py` for a human-readable report.

See `docs/WINDOWS_ACCEPTANCE.md` for the on-device acceptance run on the RTX 2050.
