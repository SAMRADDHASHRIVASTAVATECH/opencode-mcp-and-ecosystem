"""Local diffusers backend (real inference).

Runs in-process with Hugging Face `diffusers` + PyTorch on the host that has an
NVIDIA GPU (e.g. RTX 2050). Implements low-VRAM techniques chosen by the memory
manager: fp16 weights, model/sequential CPU offload, VAE slicing/tiling and
attention slicing, so SD1.5/SDXL-family models run within a small VRAM budget.

Heavy imports (torch/diffusers) are lazy and only loaded when this backend is
actually used on a machine that has them; elsewhere availability is reported
honestly as False. This file is intended to run on the target GPU machine, not
in a CPU-only build sandbox.
"""
from __future__ import annotations

import time
from pathlib import Path

from .base import Backend, ImageResult
from ..errors import (ModelNotFound, NoBackendAvailable, RuntimeNotRunning)


def _available() -> dict:
    import importlib.util
    have = {m: bool(importlib.util.find_spec(m))
            for m in ("torch", "diffusers", "PIL")}
    cuda = False
    if have["torch"]:
        try:
            import torch
            cuda = bool(torch.cuda.is_available())
        except Exception:   # noqa: BLE001
            cuda = False
    return {"available": have["torch"] and have["diffusers"] and cuda,
            "torch": have["torch"], "diffusers": have["diffusers"],
            "PIL": have["PIL"], "cuda": cuda}


class DiffusersBackend(Backend):
    name = "diffusers"
    display = "Hugging Face diffusers (local)"

    SUPPORTED = {"sd1.5", "sdxl"}

    def __init__(self, models_dir: str, memory_plan=None):
        self.models_dir = Path(models_dir)
        self.plan = memory_plan
        self._pipe = None
        self._pipe_id = None
        self._cancel = False

    def probe(self) -> dict:
        return _available()

    def supports_family(self, family_id: str) -> bool:
        return family_id in self.SUPPORTED

    def _require_runtime(self):
        st = _available()
        if not st["available"]:
            raise NoBackendAvailable(
                "diffusers backend needs torch + diffusers + a CUDA GPU. "
                "Install: pip install 'olcap-image-generator[inference]'. "
                "Reported: " + str(st))

    def _load(self, model):
        self._require_runtime()
        if self._pipe is not None and self._pipe_id == model:
            return self._pipe
        import torch
        from diffusers import DiffusionPipeline
        if (self.models_dir / model).exists():
            model_path = str(self.models_dir / model)
        else:
            model_path = model
        if not _is_local_dir(model_path) and not _is_valid_repo(model_path):
            raise ModelNotFound(f"model not found locally or as known repo: {model}")
        try:
            pipe = DiffusionPipeline.from_pretrained(
                model_path, torch_dtype=torch.float16,
                variant="fp16" if _is_local_dir(model_path) else None,
                safety_checker=None)
        except Exception as e:     # noqa: BLE001
            raise ModelNotFound(f"could not load pipeline for {model}: {e}")
        pipe = self._apply_low_vram(pipe)
        pipe.to("cuda")
        self._pipe = pipe
        self._pipe_id = model
        return pipe

    def _apply_low_vram(self, pipe):
        plan = self.plan
        if plan:
            try:
                if plan.gpu_residency in ("partial", "none"):
                    pipe.enable_model_cpu_offload()
                else:
                    pipe.enable_sequential_cpu_offload()
            except Exception:   # noqa: BLE001
                try:
                    pipe.enable_model_cpu_offload()
                except Exception:   # noqa: BLE001
                    pass
        else:
            try:
                pipe.enable_model_cpu_offload()
            except Exception:   # noqa: BLE001
                pass
        for meth in ("enable_vae_slicing", "enable_vae_tiling",
                     "enable_attention_slicing"):
            try:
                getattr(pipe, meth)()
            except Exception:   # noqa: BLE001
                pass
        return pipe

    def _do(self, pipe, *, prompt, negative, steps, width, height, seed,
            strength=None, image=None, mask=None):
        import torch
        gen = torch.Generator(device="cuda").manual_seed(seed if seed and seed >= 0
                                                         else int(time.time() * 1000) % (2**31))
        kwargs = dict(prompt=prompt, negative_prompt=negative or None,
                      num_inference_steps=steps, width=width, height=height,
                      generator=gen)
        if strength is not None:
            kwargs["strength"] = strength
        if image is not None:
            kwargs["image"] = image
        if mask is not None:
            kwargs["mask_image"] = mask
        out = pipe(**kwargs)
        return out.images[0]

    def generate(self, plan) -> ImageResult:
        self._cancel = False
        t0 = time.time()
        p = plan.params
        pipe = self._load(plan.model)
        img = self._do(pipe, prompt=p["prompt"], negative=p["negative_prompt"],
                       steps=p["steps"], width=p["width"], height=p["height"],
                       seed=p["seed"])
        path = self._save(img, plan)
        return ImageResult(path=str(path), width=p["width"], height=p["height"],
                           format=plan.out_format, backend=self.name,
                           model=plan.model, quant=plan.quant,
                           seed=p["seed"], generation_s=time.time() - t0,
                           metadata=self._meta(plan))

    def image_to_image(self, plan) -> ImageResult:
        p = plan.params
        from PIL import Image as PILImage
        pipe = self._load(plan.model)
        src = PILImage.open(plan.input_path).convert("RGB")
        img = self._do(pipe, prompt=p["prompt"], negative=p["negative_prompt"],
                       steps=p["steps"], width=p["width"], height=p["height"],
                       seed=p["seed"], strength=p.get("strength", 0.6),
                       image=src)
        path = self._save(img, plan)
        return ImageResult(path=str(path), width=p["width"], height=p["height"],
                           format=plan.out_format, backend=self.name,
                           model=plan.model, quant=plan.quant,
                           seed=p["seed"], generation_s=0.0,
                           metadata=self._meta(plan))

    def inpaint(self, plan) -> ImageResult:
        raise RuntimeNotRunning(
            "diffusers inpaint requires an inpainting model checkpoint; "
            "install one, or use the ComfyUI backend with an inpaint workflow.")

    def upscale(self, plan):
        raise RuntimeNotRunning(
            "use upscale via the ComfyUI upscale workflow or 'image' service.")

    def cancel(self) -> None:
        self._cancel = True

    def _save(self, img, plan) -> Path:
        outdir = Path(plan.output_dir)
        outdir.mkdir(parents=True, exist_ok=True)
        name = plan.filename or f"{plan.job_id}.{plan.out_format}"
        path = outdir / name
        fmt = plan.out_format.lower()
        pil_fmt = {"png": "PNG", "jpeg": "JPEG", "webp": "WEBP"}.get(fmt, "PNG")
        if pil_fmt != "PNG":
            img = img.convert("RGB")
        img.save(path, format=pil_fmt)
        (outdir / (path.stem + ".json")).write_text(
            _json(self._meta(plan) | {"path": str(path)}), encoding="utf-8")
        return path

    def _meta(self, plan) -> dict:
        return {"prompt": plan.params.get("prompt"), "model": plan.model,
                "quant": plan.quant, "seed": plan.params.get("seed"),
                "resolution": [plan.params.get("width"), plan.params.get("height")],
                "steps": plan.params.get("steps"), "backend": self.name,
                "software": "olcap-image-generator"}


def _is_local_dir(path: str) -> bool:
    return Path(path).is_dir()


def _is_valid_repo(repo: str) -> bool:
    import re
    return bool(re.match(r"^[A-Za-z0-9_.\-]+/[A-Za-z0-9_.\-]+$", repo))


def _json(d) -> str:
    import json
    return json.dumps(d, ensure_ascii=False, indent=2, default=str)
