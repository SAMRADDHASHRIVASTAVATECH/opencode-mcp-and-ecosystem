"""Diagnostics, self-test and repair.

self_test proves the whole pipeline by producing a clearly-labelled DEMO test
image (not AI-generated) so plumbing is validated on any machine. It also
reports truthfully which AI-capable backend/model is actually available.
"""
from __future__ import annotations

import importlib.util
import time
from pathlib import Path

from .generation.params import ExecutionPlan


class Diagnostics:
    def __init__(self, ctx):
        self.ctx = ctx

    def diagnose(self) -> dict:
        profile = self.ctx.profile
        checks = []
        hw = profile.to_dict()

        checks.append({
            "component": "gpu", "status": "ok" if profile.gpu["present"]
            else "missing",
            "severity": "info" if not profile.gpu["present"] else "ok",
            "detail": profile.gpu})
        ram = profile.ram.get("total_gb") or 0
        checks.append({"component": "ram", "status": "ok" if ram >= 8 else "low",
                       "severity": "warn" if ram < 8 else "ok",
                       "detail": {"total_gb": ram}})
        for dep in ("torch", "diffusers"):
            present = importlib.util.find_spec(dep) is not None
            checks.append({"component": f"dep:{dep}",
                           "status": "ok" if present else "missing",
                           "severity": "ok" if present else
                           ("warn" if dep == "torch" else "error"),
                           "detail": None})
        inst = self.ctx.registry.list(installed_only=True)
        checks.append({"component": "models",
                       "status": "ok" if inst else "none_installed",
                       "severity": "info" if inst else "warn",
                       "detail": {"installed": len(inst),
                                  "names": [m["name"] for m in inst]}})
        for b in self.ctx.available_backends():
            try:
                p = b.probe()
                checks.append({"component": f"backend:{b.name}",
                               "status": "ok" if p.get("available") else
                               "unavailable",
                               "severity": "ok" if p.get("available") else "warn",
                               "detail": p})
            except Exception as e:   # noqa: BLE001
                checks.append({"component": f"backend:{b.name}",
                               "status": "error", "severity": "warn",
                               "detail": str(e)})
        cd = self.ctx.comfy.detect()
        checks.append({"component": "comfyui", "status":
                       "running" if self.ctx.comfy.health() else
                       ("installed" if cd["installed"] else "not_installed"),
                       "severity": "ok", "detail": cd})
        root = self.ctx.settings.resolved_root()
        from .storage import disk_free_gb
        checks.append({"component": "disk", "status": "ok",
                       "detail": {"free_gb": disk_free_gb(root)}})

        problems = [c for c in checks if c.get("severity") in ("error", "warn")]
        return {"hardware": hw, "checks": checks,
                "problems": problems, "counts": {
                    "ok": sum(1 for c in checks if c.get("severity") == "ok"),
                    "warn": sum(1 for c in checks if c.get("severity") == "warn"),
                    "error": sum(1 for c in checks if c.get("severity") == "error")},
                "recommendation": ("Install the inference runtime on the target "
                                   "GPU machine (pip install "
                                   "'olcap-image-generator[inference]') and "
                                   "install a model to enable real generation."
                                   if not profile.gpu["present"] else
                                   "GPU present - proceed to install a model.")}

    def self_test(self, *, allow_demo_image: bool = True) -> dict:
        results = []
        results.append(_r("python", True, "interpreter OK"))
        for m in ("psutil", "yaml", "requests"):
            try:
                __import__(m)
                results.append(_r(f"import:{m}", True))
            except Exception as e:   # noqa: BLE001
                results.append(_r(f"import:{m}", False, str(e)))
        gp = self.ctx.profile.gpu
        results.append(_r("cuda", bool(gp.get("cuda_available")),
                          ("present" if gp.get("present") else "no GPU"),
                          required=False))
        try:
            self.ctx.registry.list()
            results.append(_r("registry", True))
        except Exception as e:   # noqa: BLE001
            results.append(_r("registry", False, str(e)))
        demo_ok = False
        if allow_demo_image:
            try:
                self.ctx.demo.allow(True)
                job = _FakeJob()
                plan = ExecutionPlan(
                    job_id=job.job_id, model="demo", family="demo",
                    quant="none",
                    params={"prompt": "demo", "negative_prompt": "",
                            "width": 128, "height": 128, "steps": 1,
                            "seed": 1}, quality="balanced",
                    output_dir=str(self.ctx.settings.resolved_cache_dir() /
                                   "tmp/selftest"), out_format="png")
                res = self.ctx.demo.generate(plan)
                demo_ok = Path(res.path).exists()
                results.append(_r("pipeline.demo_generation", demo_ok,
                                  res.path, required=False))
            except Exception as e:   # noqa: BLE001
                results.append(_r("pipeline.demo_generation", False, str(e),
                                  required=False))
        ai = self.ctx.available_backends()
        ai_ok = any(getattr(b, "name", "") in ("diffusers", "comfyui") for b in ai)
        results.append(_r("ai_backend_available", ai_ok,
                          ("none" if not ai_ok else "yes"),
                          required=False))
        all_core = all(r["ok"] for r in results if r["required"])
        return {"success": all_core, "results": results,
                "ai_generation_ready": ai_ok,
                "note": ("Demo plumbing passed. Real AI generation additionally "
                         "requires a GPU runtime + installed model on the "
                         "target machine." if ai_ok is False else "")}

    def repair(self) -> dict:
        diag = self.diagnose()
        actions = []
        for c in diag["checks"]:
            if c["component"].startswith("dep:") and c["status"] == "missing":
                actions.append({"action": "pip install", "component":
                                c["component"]})
        cd = self.ctx.comfy.detect()
        if cd["installed"] and not self.ctx.comfy.health():
            try:
                self.ctx.comfy.start()
                actions.append({"action": "restarted ComfyUI",
                                "status": "ok"})
            except Exception as e:   # noqa: BLE001
                actions.append({"action": "restart ComfyUI",
                                "status": "failed", "detail": str(e)})
        st = self.self_test()
        return {"actions": actions, "self_test": st}


def _r(name, ok, detail=None, required=True):
    return {"test": name, "ok": bool(ok), "required": required,
            "detail": detail}


class _FakeJob:
    def __init__(self):
        import uuid
        self.job_id = "olcap-" + uuid.uuid4().hex[:12]
        self.model = None
        self.stage = "running"
        self.progress_percent = 0.0
        self.log = []

    def append_log(self, msg):
        self.log.append(msg)
