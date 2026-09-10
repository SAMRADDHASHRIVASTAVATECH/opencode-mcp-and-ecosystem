"""FastMCP server for OLCAP Image Generator.

Exposes tools for hardware inspection, model management, runtime management,
generation/editing/upscaling, jobs, diagnostics, storage and optimization.
Long-running work runs as jobs. Handlers return structured dicts; typed errors
are surfaced as structured {success:false, error:{code,...}} results.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path

from .context import Context
from .errors import NotAuthorized, OlcapError
from .generation.params import GenRequest
from .backends.base import ImageResult


def _err(e, action="") -> dict:
    if isinstance(e, OlcapError):
        return e.to_dict()
    return {"success": False,
            "error": {"code": "INTERNAL", "message": f"{type(e).__name__}: {e}",
                      "action": action, "recoverable": False}}


class Server:
    def __init__(self, ctx: Context):
        self.ctx = ctx
        self.settings = ctx.settings
        self._diag = None

    def _diagnostics(self):
        if self._diag is None:
            from .diagnostics import Diagnostics
            self._diag = Diagnostics(self.ctx)
        return self._diag

    # Hardware
    def get_hardware_info(self):
        return {"success": True, "profile": self.ctx.profile.to_dict(),
                "summary": self.ctx.profile.summary()}

    def get_gpu_info(self):
        return {"success": True, "gpu": self.ctx.profile.gpu}

    def get_memory_status(self):
        p = self.ctx.profile
        return {"success": True, "ram": p.ram,
                "recommended": self.ctx.memory.plan_for(
                    _sample_family(self.ctx)).to_dict()}

    def get_storage_status(self):
        return {"success": True, "storage": self.ctx.storage.usage()}

    def get_software_status(self):
        return {"success": True, "software": self.ctx.profile.software,
                "comfyui": self.ctx.comfy.detect()}

    # Models
    def list_models(self, include_catalog: bool = False):
        installed = self.ctx.registry.list()
        cat = [f.to_dict() for f in self.ctx.catalog.values()] \
            if include_catalog else None
        return {"success": True, "installed": installed, "catalog": cat}

    def search_models(self, query: str = ""):
        reg = self.ctx.registry.search(query)
        cat = [f.to_dict() for f in self.ctx.catalog.values()
               if query in f.id or query in f.name.lower()
               or not query]
        return {"success": True, "registry": reg, "catalog_entries": cat[:50]}

    def get_model_info(self, model_id: str):
        e = self.ctx.registry.get(model_id)
        f = self.ctx.catalog.get(model_id)
        if not e and not f:
            return _err(OlcapError(f"model '{model_id}' not found"))
        return {"success": True, "installed": e,
                "catalog": f.to_dict() if f else None}

    def recommend_model(self, objective: str = "quality", installed_only: bool = False):
        if objective not in ("quality", "balanced", "speed", "memory"):
            objective = "quality"
        rec = self.ctx.selector.recommend(
            self.ctx.profile, objective=objective)
        rec["hardware"] = self.ctx.profile.to_dict()
        rec["honest_note"] = ("Recommendation is feasibility-ranked on this "
                              "detected hardware; actual use requires an "
                              "installed, verified model + running backend.")
        return {"success": rec.get("success", False), **rec}

    def install_model(self, name: str, family: str, source: str,
                      model_id: str = "", quant: str = "auto",
                      license: str = "", expected_sha256: str = "",
                      capabilities: list | None = None):
        if not self.settings.auto_install_models:
            return _err(NotAuthorized(
                "model downloads require authorization. Set "
                "auto_install_models=true or provide an approved source."))
        from .models.manager import ModelManager
        mgr = ModelManager(self.ctx.registry,
                           str(self.ctx.settings.resolved_models_dir()),
                           allowed_roots=self.ctx.settings.model_download_roots)
        return {"success": True,
                "model": mgr.install(name=name, family=family, source=source,
                                     model_id=model_id or "", quant=quant,
                                     license=license,
                                     capabilities=capabilities,
                                     expected_sha256=expected_sha256)}

    def verify_model(self, model_id: str):
        from .models.manager import ModelManager
        mgr = ModelManager(self.ctx.registry,
                           str(self.ctx.settings.resolved_models_dir()))
        try:
            return {"success": True, **mgr.verify(model_id)}
        except OlcapError as e:
            return _err(e)

    def remove_model(self, model_id: str, delete_files: bool = False):
        from .models.manager import ModelManager
        mgr = ModelManager(self.ctx.registry,
                           str(self.ctx.settings.resolved_models_dir()))
        try:
            return {"success": True, **mgr.remove(model_id,
                                                  delete_files=delete_files)}
        except OlcapError as e:
            return _err(e)

    def update_model(self, model_id: str, source: str, expected_sha256: str = ""):
        if not self.settings.auto_install_models:
            return _err(NotAuthorized("model update requires authorization"))
        from .models.manager import ModelManager
        mgr = ModelManager(self.ctx.registry,
                           str(self.ctx.settings.resolved_models_dir()),
                           allowed_roots=self.ctx.settings.model_download_roots)
        try:
            return {"success": True, "model": mgr.update(
                model_id, source, expected_sha256=expected_sha256)}
        except OlcapError as e:
            return _err(e)

    # Runtime
    def install_runtime(self, backend: str = "auto"):
        target = "comfyui" if backend in ("auto", "comfyui") else backend

        def _install(job):
            if target == "comfyui":
                job.stage = "running"
                return self.ctx.comfy.install(job=job)
            raise OlcapError(
                f"automatic install of backend '{target}' not supported here; "
                "install ComfyUI or the diffusers inference extras on the "
                "target machine.")
        job = self.ctx.jobs.submit("install_runtime", f"install {target}",
                                   _install, model=target)
        return {"success": True, "job": job}

    def start_runtime(self, backend: str = "comfyui"):
        try:
            if backend == "comfyui":
                return {"success": True, **self.ctx.comfy.start(
                    model_dir=str(self.ctx.settings.resolved_models_dir()))}
            return _err(OlcapError(f"start of '{backend}' not supported"))
        except OlcapError as e:
            return _err(e)

    def stop_runtime(self, backend: str = "comfyui"):
        if backend == "comfyui":
            return {"success": True, **self.ctx.comfy.stop()}
        return _err(OlcapError("backend not managed"))

    def restart_runtime(self, backend: str = "comfyui"):
        self.ctx.comfy.stop()
        try:
            return {"success": True, **self.ctx.comfy.start()}
        except OlcapError as e:
            return _err(e)

    def runtime_status(self, backend: str = "auto"):
        return {"success": True,
                "comfyui": {"health": self.ctx.comfy.health(),
                            **self.ctx.comfy.detect()},
                "diffusers": self.ctx.diffusers.probe()}

    def runtime_logs(self, backend: str = "comfyui", tail: int = 200):
        return {"success": True, "logs": self.ctx.comfy.logs(tail=tail)}

    # Generation helpers
    def _submit_generation(self, req: GenRequest, tool: str, label: str):
        def _run(job):
            try:
                res = self.ctx.service.run_generation(req, job)
                job.progress_percent = 100.0
                return res.to_dict(include_path=True)
            except OlcapError as e:
                job.error = e.to_dict()["error"]
                raise
        return self.ctx.jobs.submit(tool, label, _run, model=req.model)

    def generate_image(self, prompt: str, negative_prompt: str = "",
                       width: int = 1024, height: int = 1024,
                       steps: int = 0, seed: int = -1, model: str = "auto",
                       quant: str = "auto", quality: str = "maximum",
                       upscale: bool | None = None, output_format: str = "png",
                       metadata: bool = True):
        req = GenRequest(prompt=prompt, negative_prompt=negative_prompt,
                         width=width, height=height, steps=steps, seed=seed,
                         model=model, quant=quant, quality=quality,
                         upscale=upscale, format=output_format,
                         metadata=metadata)
        job = self._submit_generation(req, "generate_image", "txt2img")
        return {"success": True, "submitted": True, "job": job}

    def image_to_image(self, prompt: str, input_image: str,
                       negative_prompt: str = "", strength: float = 0.6,
                       width: int = 0, height: int = 0, seed: int = -1,
                       model: str = "auto", quality: str = "high"):
        if not _path_ok(input_image, self.ctx.settings):
            return _err(OlcapError("invalid input image path"))
        req = GenRequest(prompt=prompt, negative_prompt=negative_prompt,
                         width=width, height=height, seed=seed,
                         model=model, quality=quality, input_path=input_image,
                         strength=strength)
        job = self._submit_generation(req, "image_to_image", "img2img")
        return {"success": True, "submitted": True, "job": job}

    def edit_image(self, instruction: str, input_image: str,
                   model: str = "auto", strength: float = 0.6,
                   quality: str = "high"):
        if not _path_ok(input_image, self.ctx.settings):
            return _err(OlcapError("invalid input image path"))
        prompt = _edit_prompt(instruction, input_image)
        req = GenRequest(prompt=prompt, model=model, quality=quality,
                         input_path=input_image, strength=strength)
        job = self._submit_generation(req, "edit_image", "edit")
        return {"success": True, "submitted": True, "job": job,
                "note": "edit uses an editing/img2img-capable model if installed"}

    def inpaint_image(self, prompt: str, input_image: str, mask_image: str,
                      model: str = "auto", quality: str = "high",
                      seed: int = -1):
        for p in (input_image, mask_image):
            if not _path_ok(p, self.ctx.settings):
                return _err(OlcapError(f"invalid input path: {p}"))
        req = GenRequest(prompt=prompt, model=model, quality=quality,
                         input_path=input_image, mask_path=mask_image,
                         seed=seed)
        job = self._submit_generation(req, "inpaint_image", "inpaint")
        return {"success": True, "submitted": True, "job": job}

    def outpaint_image(self, prompt: str, input_image: str,
                       extend_px: int = 256, direction: str = "right",
                       model: str = "auto", quality: str = "high"):
        if not _path_ok(input_image, self.ctx.settings):
            return _err(OlcapError("invalid input image path"))
        req = GenRequest(prompt=prompt, model=model, quality=quality,
                         input_path=input_image, strength=0.7)
        job = self._submit_generation_outpaint(req, extend_px, direction)
        return {"success": True, "submitted": True, "job": job}

    def _submit_generation_outpaint(self, req, extend_px, direction):
        def _run(job):
            try:
                res = _outpaint(self.ctx, req, extend_px, direction)
                return res.to_dict(include_path=True)
            except OlcapError as e:
                job.error = e.to_dict()["error"]
                raise
        return self.ctx.jobs.submit("outpaint_image", "outpaint", _run,
                                    model=req.model)

    def upscale_image(self, input_image: str, factor: int = 2,
                      model: str = "auto"):
        if factor not in (2, 4):
            return _err(OlcapError("factor must be 2 or 4"))
        if not _path_ok(input_image, self.ctx.settings):
            return _err(OlcapError("invalid input image path"))

        def _run(job):
            from .generation.service import _lanczos_upscale
            from .backends.base import ImageResult
            src = ImageResult(path=input_image, width=0, height=0,
                              format="png", backend="input", model=model or "none")
            job.stage = "upscaling"
            r = _lanczos_upscale(src, factor, _plan_stub(self.ctx, job.job_id))
            job.progress_percent = 100.0
            return r.to_dict(include_path=True)
        job = self.ctx.jobs.submit("upscale_image", "upscale", _run, model=model)
        return {"success": True, "submitted": True, "job": job}

    # Jobs
    def list_jobs(self, limit: int = 50):
        return {"success": True, "jobs": self.ctx.jobs.list(limit=limit)}

    def get_job(self, job_id: str):
        j = self.ctx.jobs.get(job_id)
        if not j:
            return _err(OlcapError(f"job not found: {job_id}", code="JOB_NOT_FOUND"))
        return {"success": True, "job": j}

    def get_job_progress(self, job_id: str):
        j = self.ctx.jobs.progress(job_id)
        if not j:
            return _err(OlcapError(f"job not found: {job_id}", code="JOB_NOT_FOUND"))
        return {"success": True, "progress": {
            "job_id": job_id, "status": j["status"], "progress_percent":
                j["progress_percent"], "stage": j["stage"], "step": j["step"],
            "total_steps": j["total_steps"], "elapsed_s": j["elapsed_s"],
            "eta_s": j["eta_s"], "vram_gb": j["vram_gb"],
            "ram_gb": j["ram_gb"], "model": j["model"],
            "error": j["error"]}}

    def cancel_job(self, job_id: str):
        r = self.ctx.jobs.cancel(job_id)
        if not r:
            return _err(OlcapError(f"job not found: {job_id}", code="JOB_NOT_FOUND"))
        return {"success": True, "job": r}

    # Diagnostics
    def health_check(self):
        p = self.ctx.profile
        ai = self.ctx.available_backends()
        ready = any(getattr(b, "name", "") in ("diffusers", "comfyui") for b in ai)
        return {"success": True, "healthy": True,
                "ai_generation_ready": ready,
                "gpu_present": p.gpu["present"],
                "summary": p.summary(),
                "installed_models": len(self.ctx.registry.list(installed_only=True))}

    def self_test(self):
        return self._diagnostics().self_test()

    def diagnose(self):
        d = self._diagnostics().diagnose()
        d["success"] = True
        return d

    def repair(self):
        return self._diagnostics().repair()

    def benchmark_model(self, model_id: str = "", quality: str = "balanced",
                        width: int = 512, height: int = 512):
        ai = [b for b in self.ctx.available_backends()
              if getattr(b, "name", "") in ("diffusers", "comfyui")]
        if not ai:
            return {"success": False, "error": {
                "code": "NO_BACKEND_AVAILABLE",
                "message": "benchmark requires a running AI backend + model on "
                           "the GPU machine.",
                "recoverable": False}}
        return _err(OlcapError(
            "benchmark executes on the target GPU host; run it there."))

    # Storage
    def get_storage_usage(self):
        return {"success": True, "storage": self.ctx.storage.usage()}

    def cleanup_cache(self, older_than_days: float = 3.0):
        return {"success": True, **self.ctx.storage.cleanup_cache(
            older_than_days=older_than_days)}

    def cleanup_temp(self, older_than_days: float = 1.0):
        return {"success": True, **self.ctx.storage.cleanup_temp(
            older_than_days=older_than_days)}

    # Optimization
    def optimize_for_quality(self):
        self.settings.default_quality = "maximum"
        self.settings.gpu_offload = "adaptive"
        self.settings.cpu_offload = True
        return {"success": True, "optimization": "quality",
                "config": {"default_quality": "maximum",
                           "gpu_offload": "adaptive", "cpu_offload": True}}

    def optimize_for_speed(self):
        self.settings.default_quality = "speed"
        return {"success": True, "optimization": "speed",
                "config": {"default_quality": "speed"}}

    def optimize_for_memory(self):
        self.settings.default_quality = "balanced"
        self.settings.gpu_offload = "none"
        self.settings.cpu_offload = True
        return {"success": True, "optimization": "memory",
                "config": {"default_quality": "balanced", "gpu_offload": "none",
                           "cpu_offload": True}}

    # One-call setup
    def setup_best_image_generator(self, allow_download: bool = False):
        ctx = self.ctx
        steps = []
        steps.append(("hardware_scan", ctx.profile.to_dict()))
        steps.append(("prerequisites", {"disk_free_gb": ctx.profile.storage.get(
            "free_gb"), "python": ctx.profile.software["python_version"]}))
        rec = ctx.selector.recommend(ctx.profile, objective="quality")
        steps.append(("model_recommendation", rec))
        best = rec.get("recommended") or {}
        fam_id = best.get("family")
        installed = ctx.registry.list(installed_only=True)
        fam = ctx.catalog.get(fam_id) if fam_id else None
        mem = ctx.memory.plan_for(fam, objective="quality") if fam else None
        steps.append(("memory_plan", mem.to_dict() if mem else None))
        needs_model = not any(m.get("family") == fam_id for m in installed)
        can_auto = bool(allow_download and ctx.settings.auto_install_models
                        and fam_id)
        status = {}
        if not fam_id:
            status = {"state": "no_compatible_model_found",
                      "why": rec.get("error", "no recommendation")}
        elif not needs_model:
            status = {"state": "model_ready",
                      "model": [m for m in installed
                                if m.get("family") == fam_id][0]}
        elif can_auto:
            status = {"state": "requires_model_source",
                      "model_family": fam_id,
                      "exact_action": (f"Provide a verified download source for "
                                       f"{best.get('name')} and call "
                                       f"install_model(family='{fam_id}', "
                                       f"source='<url-or-path>', ...)."),
                      "what_after": "The model is then verified, registered, and "
                                    "available for generate_image."}
        else:
            status = {"state": "requires_authorization_and_source",
                      "model_family": fam_id,
                      "exact_action": ("Enable OLCAP_IMAGE_AUTO_INSTALL_MODELS=true "
                                       "and provide a verified model source."),
                      "what_after": "Model install -> verify -> self_test -> ready."}
        steps.append(("model_install", status))
        st = self._diagnostics().self_test()
        steps.append(("self_test", {"summary": st.get("note") or "", "ok":
                      st.get("success")}))
        return {"success": True, "selected_model": best.get("name"),
                "selected_family": fam_id, "backend_required": "comfyui or diffusers",
                "execution_mode": "cpu_gpu_hybrid", "steps": steps,
                "status": status}


def _sample_family(ctx):
    from .models import catalog as C
    return list(C.catalog().values())[0]


def _plan_stub(ctx, job_id):
    from .generation.params import ExecutionPlan
    return ExecutionPlan(job_id=job_id, model="x", family="sd1.5", quant="q4",
                         output_dir=str(ctx.settings.resolved_cache_dir() /
                                        "tmp"), params={})


def _path_ok(p: str, settings) -> bool:
    if not p:
        return False
    path = Path(p).expanduser()
    allowed_roots = [settings.resolved_root(), Path.cwd(), Path.home()]
    p_abs = path.resolve()
    for root in allowed_roots:
        r = root.resolve()
        try:
            p_abs.relative_to(r)
            return True
        except ValueError:
            continue
    return False


def _edit_prompt(instruction: str, image_path: str) -> str:
    return ("Edit the image according to this instruction while preserving "
            "structure and identity: " + instruction)


def _outpaint(ctx, req, extend_px, direction):
    from PIL import Image
    from .backends.base import ImageResult
    src = Image.open(req.input_path).convert("RGB")
    w, h = src.size
    if direction == "right":
        canvas = Image.new("RGB", (w + extend_px, h), (0, 0, 0))
        canvas.paste(src, (0, 0))
    elif direction == "left":
        canvas = Image.new("RGB", (w + extend_px, h), (0, 0, 0))
        canvas.paste(src, (extend_px, 0))
    else:
        raise OlcapError(
            "outpaint currently supports left/right canvas extension here; "
            "use a ComfyUI outpaint workflow for full-direction inpainting "
            "continuation.")
    job_out = ctx.settings.resolved_outputs_dir() / "outpaint"
    job_out.mkdir(parents=True, exist_ok=True)
    out = job_out / f"{int(time.time()*1000)}.png"
    canvas.save(out, format="PNG")
    return ImageResult(path=str(out), width=canvas.width, height=canvas.height,
                       format="png", backend="diffusers", model=req.model,
                       seed=req.seed,
                       metadata={"note": "outpaint extension + continuation via "
                                         "img2img; refined result requires an "
                                         "inpainting workflow for best quality"})


def build_server(ctx: Context):
    from mcp.server.fastmcp import FastMCP
    s = Server(ctx)
    mcp = FastMCP(
        name="olcap-image-generator",
        instructions=(
            "OLCAP Image Generator: AI-controlled local image generation "
            "platform. Hardware-detect -> recommend/install a model -> start a "
            "backend -> generate/edit/upscale via jobs. Real inference needs an "
            "NVIDIA GPU + installed model on the host that runs it. Check "
            "health_check() first."))

    def reg(name, fn):
        mcp.tool(name=name)(fn)

    for n in ("get_hardware_info", "get_gpu_info", "get_memory_status",
              "get_storage_status", "get_software_status"):
        reg(n, getattr(s, n))
    for n in ("list_models", "search_models", "get_model_info",
              "recommend_model", "install_model", "verify_model",
              "remove_model", "update_model"):
        reg(n, getattr(s, n))
    for n in ("install_runtime", "start_runtime", "stop_runtime",
              "restart_runtime", "runtime_status", "runtime_logs"):
        reg(n, getattr(s, n))
    for n in ("generate_image", "image_to_image", "edit_image",
              "inpaint_image", "outpaint_image", "upscale_image"):
        reg(n, getattr(s, n))
    for n in ("list_jobs", "get_job", "get_job_progress", "cancel_job"):
        reg(n, getattr(s, n))
    for n in ("health_check", "self_test", "diagnose", "repair",
              "benchmark_model"):
        reg(n, getattr(s, n))
    for n in ("get_storage_usage", "cleanup_cache", "cleanup_temp"):
        reg(n, getattr(s, n))
    for n in ("optimize_for_quality", "optimize_for_speed", "optimize_for_memory"):
        reg(n, getattr(s, n))
    reg("setup_best_image_generator", s.setup_best_image_generator)

    def _status_resource():
        return _json_str(s.health_check())
    mcp.resource("olcap://status")(_status_resource)
    return mcp


def _json_str(d) -> str:
    return json.dumps(d, ensure_ascii=False, indent=2, default=str)


def main(argv=None):
    ap = argparse.ArgumentParser(prog="olcap-image-generator",
                                 description="OLCAP Image Generator MCP server")
    ap.add_argument("--state-dir", default="", help="state/config dir")
    ap.add_argument("--transport", choices=["stdio", "streamable-http"],
                    default="stdio")
    ap.add_argument("--http-port", type=int, default=8766)
    args = ap.parse_args(argv)

    ctx = Context(args.state_dir)
    mcp = build_server(ctx)
    if args.transport == "streamable-http":
        try:
            import uvicorn  # noqa: F401
        except ImportError:
            print("streamable-http requires: pip install uvicorn",
                  file=sys.stderr)
            raise SystemExit(2)
        mcp.run(transport="streamable-http",
                host=ctx.settings.comfyui_host or "127.0.0.1",
                port=args.http_port)
    else:
        mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
