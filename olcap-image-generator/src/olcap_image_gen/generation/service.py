"""Image generation service.

Orchestrates: model selection -> memory plan -> backend selection -> execution
-> OOM recovery -> optional upscale/refine -> validated output + metadata.

Executes inside a Job so progress/stages are tracked and cancel works. Honest:
raises when no real backend+model is available; never fabricates an AI image.
"""
from __future__ import annotations

import json
from pathlib import Path

from ..errors import (CUDAOutOfMemory, ModelNotFound, NoBackendAvailable,
                      OlcapError)
from ..backends.base import ImageResult
from .params import ExecutionPlan, GenRequest, QUALITY_PRESETS, normalize


class ImageService:
    def __init__(self, ctx):
        self.ctx = ctx

    def resolve_model(self, request: GenRequest) -> dict:
        profile = self.ctx.profile
        if request.model and request.model not in ("auto", ""):
            entry = self.ctx.registry.get(request.model)
            if entry:
                return entry
            fam = self.ctx.catalog.get(request.model)
            if fam:
                return {"id": fam.id, "family": fam.id, "name": fam.name,
                        "params_b": fam.params_b}
            raise ModelNotFound(f"model '{request.model}' is not installed or "
                                "known. Use search_models / recommend_model.")
        rec = self.ctx.selector.recommend(
            profile, objective="quality" if request.quality != "speed" else "speed")
        if not rec.get("success"):
            raise NoBackendAvailable(rec.get("error", "no model available"))
        best = rec["recommended"]
        return {"id": best["model_id"], "family": best["model_id"],
                "name": best["name"], "quant": best["quant"],
                "recommended": True}

    def choose_backend(self, family_id: str, include_demo: bool = False):
        for b in self.ctx.available_backends(include_demo=include_demo):
            try:
                if b.supports_family(family_id):
                    return b
            except Exception:   # noqa: BLE001
                continue
        return None

    def build_plan(self, request: GenRequest, job_id: str) -> ExecutionPlan:
        entry = self.resolve_model(request)
        fam = self.ctx.catalog.get(entry.get("family", entry.get("id")))
        if fam is None:
            fam = self.ctx.catalog.get(entry.get("id")) or \
                  self.ctx.catalog.get(entry.get("family"))
        if fam is None:
            raise ModelNotFound("family not in catalog: " + str(entry))
        preset = QUALITY_PRESETS.get(request.quality, QUALITY_PRESETS["balanced"])
        params = normalize(request, quality_preset=preset)
        quant = request.quant
        if not quant or quant == "auto":
            quant = self.ctx.memory.choose_quant(
                fam, objective="quality" if request.quality != "speed" else "speed")
        if entry.get("quant") and request.quant in ("auto", ""):
            quant = entry["quant"]
        mplan = self.ctx.memory.plan_for(fam, objective=request.quality,
                                         quant=quant,
                                         resolution=(params["width"],
                                                     params["height"]))
        outdir = self.ctx.settings.resolved_outputs_dir() / fam.id
        return ExecutionPlan(
            job_id=job_id, model=entry.get("id", fam.id),
            family=fam.id, quant=quant, params=params,
            quality=request.quality, output_dir=str(outdir),
            out_format=request.format, memory_plan=mplan.to_dict(),
            input_path=request.input_path, mask_path=request.mask_path)

    def run_generation(self, request: GenRequest, job) -> ImageResult:
        plan = self.build_plan(request, job.job_id)
        job.model = plan.model
        job.total_steps = plan.params.get("steps")
        backend = self.choose_backend(plan.family)
        if backend is None:
            raise NoBackendAvailable(
                "No real backend available for model family "
                f"'{plan.family}' on this machine (needs GPU + diffusers, or a "
                "running ComfyUI with a compatible workflow). Install the "
                "runtime/model on the target machine or start ComfyUI.")

        job.stage = "loading_model"
        result = self._execute_with_recovery(backend, plan, job)
        if plan.params.get("upscale"):
            job.stage = "upscaling"
            result = self._maybe_upscale(result, plan, job)
        job.stage = "refining"
        self._write_metadata(result, plan)
        return result

    def _execute_with_recovery(self, backend, plan, job) -> ImageResult:
        attempts = 0
        current = plan
        while True:
            try:
                job.progress_percent = 10.0
                return backend.generate(current)
            except CUDAOutOfMemory as e:
                if attempts >= 2:
                    raise
                attempts += 1
                job.append_log(f"OOM -> increasing CPU offload (attempt {attempts})")
                self._increase_offload(current)
            except OlcapError as e:
                if e.code == "CUDA_OUT_OF_MEMORY" and attempts < 2:
                    attempts += 1
                    job.append_log("CUDA OOM -> increase offload + retry")
                    self._increase_offload(current)
                    continue
                raise
            except Exception as e:   # noqa: BLE001
                if _is_oom(str(e)) and attempts < 2:
                    attempts += 1
                    job.append_log("OOM detected -> offload retry")
                    self._increase_offload(current)
                    continue
                raise CUDAOutOfMemory(
                    f"generation failed (out-of-memory or runtime): {e}",
                    recoverable=True, recovery_attempted=False)

    def _increase_offload(self, plan: ExecutionPlan):
        mp = dict(plan.memory_plan or {})
        mp["gpu_residency"] = "partial"
        mp["cpu_offload"] = True
        plan.memory_plan = mp

    def _maybe_upscale(self, result: ImageResult, plan, job) -> ImageResult:
        up_backend = self.choose_backend(plan.family)
        try:
            if up_backend and getattr(up_backend, "name", "") == "comfyui":
                r2 = up_backend.upscale(plan)
                r2.metadata["upscale"] = {"method": "comfyui-workflow",
                                          "from": result.path}
                return r2
        except Exception:   # noqa: BLE001
            pass
        job.append_log("using high-quality Lanczos upscale fallback")
        return _lanczos_upscale(result, 2, plan)

    def _write_metadata(self, result: ImageResult, plan: ExecutionPlan):
        outdir = Path(result.path).parent
        side = outdir / (Path(result.path).stem + ".json")
        meta = {
            "prompt": plan.params.get("prompt"),
            "negative_prompt": plan.params.get("negative_prompt"),
            "model": plan.model, "family": plan.family, "quant": plan.quant,
            "seed": result.seed, "resolution": [result.width, result.height],
            "steps": plan.params.get("steps"),
            "sampler": None, "scheduler": None,
            "backend": result.backend, "software": "olcap-image-generator",
            "generation_s": result.generation_s,
            "quality": plan.quality,
        }
        side.write_text(json.dumps(meta, ensure_ascii=False, indent=2),
                        encoding="utf-8")


def _is_oom(msg: str) -> bool:
    m = (msg or "").lower()
    return "out of memory" in m or "cuda oom" in m or "torch.cuda.outofmemory" in m


def _lanczos_upscale(result: ImageResult, factor: int, plan) -> ImageResult:
    from PIL import Image
    img = Image.open(result.path)
    nw, nh = img.width * factor, img.height * factor
    img2 = img.resize((nw, nh), Image.LANCZOS)
    outdir = Path(plan.output_dir)
    outdir.mkdir(parents=True, exist_ok=True)
    out = outdir / f"{Path(result.path).stem}_2x.png"
    img2.save(out, format="PNG")
    return ImageResult(path=str(out), width=nw, height=nh, format="png",
                       backend=result.backend, model=result.model,
                       quant=result.quant, seed=result.seed,
                       generation_s=result.generation_s,
                       metadata={"upscale": {"method": "lanczos",
                                             "factor": factor,
                                             "from": result.path}})
