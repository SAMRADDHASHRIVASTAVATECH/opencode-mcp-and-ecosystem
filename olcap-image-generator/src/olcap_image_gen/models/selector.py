"""Model selection / ranking engine.

Ranks candidate model+quantization combinations against the *detected* hardware.
Scores are transparent and field-based (quality, text/photo capability, memory
fit, runtime compatibility). Real measured benchmark results, when present, are
folded in from the selection benchmark cache. A family counts as installed when
any verified model of that family exists.
"""
from __future__ import annotations

import json
import threading
from pathlib import Path

from . import catalog as C
from .registry import ModelRegistry


class Selector:
    def __init__(self, registry: ModelRegistry,
                 bench_path: str | Path | None = None):
        self.registry = registry
        self._bench = {}
        self._bench_path = Path(bench_path) if bench_path else None
        self._lock = threading.Lock()
        self._load_bench()

    def _load_bench(self):
        if self._bench_path and self._bench_path.exists():
            try:
                self._bench = json.loads(self._bench_path.read_text())
            except Exception:   # noqa: BLE001
                self._bench = {}

    def record_benchmark(self, model_id: str, quant: str, *, gen_s, vram_gb,
                         ram_gb, resolution, success: bool) -> None:
        with self._lock:
            key = f"{model_id}@{quant}"
            entry = {"model_id": model_id, "quant": quant, "gen_s": gen_s,
                     "vram_gb": vram_gb, "ram_gb": ram_gb,
                     "resolution": resolution, "success": success}
            self._bench[key] = entry
            if self._bench_path:
                self._bench_path.write_text(json.dumps(self._bench, indent=2))
        self._bench = dict(self._bench)

    def candidate_combos(self, profile, *, backends=None,
                         families: list[str] | None = None) -> list[dict]:
        fams = C.catalog()
        backends = backends or ["comfyui", "diffusers"]
        combos = []
        gpu_ram_gb = (profile.gpu.get("vram_gb") or 0)
        sys_ram_gb = profile.ram.get("total_gb") or 0
        gpu_present = bool(profile.gpu.get("present"))
        for f in fams.values():
            if families and f.id not in families:
                continue
            sup = [b for b in backends if b in f.backends]
            if not sup:
                continue
            for quant in C.QUANT_QUALITY_ORDER:
                if quant not in f.quant_sizes():
                    continue
                size = f.quant_sizes()[quant]
                combos.append(self._feasible(
                    f, quant, size, gpu_present, gpu_ram_gb, sys_ram_gb,
                    supported_backends=sup))
        return combos

    def _feasible(self, fam, quant, size_gb, gpu_present, vram, ram,
                  supported_backends):
        runtime_overhead_gb = 1.5
        fits_ram = (size_gb + runtime_overhead_gb) <= (ram * 0.85)
        if gpu_present and vram >= size_gb * 1.15:
            residency = "full"
        elif gpu_present:
            residency = "partial"
        else:
            residency = "none"
        bench = self._bench.get(f"{fam.id}@{quant}")
        return {
            "model_id": fam.id, "name": fam.name, "family": fam.id,
            "params_b": fam.params_b, "quant": quant,
            "approx_weights_gb": round(size_gb, 2),
            "quality": fam.quality, "photorealism": fam.photorealism,
            "prompt_adherence": fam.prompt_adherence,
            "text_rendering": fam.text_rendering,
            "license": fam.license,
            "capabilities": fam.capabilities,
            "supported_backends": supported_backends,
            "gpu_residency": residency,
            "fits_ram": fits_ram,
            "gpu_required": False,
            "benchmark": bench,
            "notes": fam.notes,
        }

    def rank(self, profile, *, objective: str = "quality",
             installed_only: bool = False, backends=None,
             families: list[str] | None = None,
             max_results: int = 8) -> list[dict]:
        combos = self.candidate_combos(profile, backends=backends,
                                       families=families)
        installed_fams = set()
        if self.registry:
            installed_fams = {m.get("family")
                              for m in self.registry.list(installed_only=True)}
        scored = []
        for c in combos:
            c = dict(c)
            c["installed"] = c["family"] in installed_fams
            if installed_only and not c["installed"]:
                continue
            c["score"] = self._score(c, profile, objective)
            scored.append(c)
        scored.sort(key=lambda x: -x["score"])
        return scored[:max_results]

    def recommend(self, profile, *, objective: str = "quality",
                  allow_uninstalled: bool = True) -> dict:
        candidates = self.rank(profile, objective=objective,
                               backends=["comfyui", "diffusers"])
        if not candidates:
            return {"success": False, "error": "no compatible model found",
                    "recommended": None}
        best = candidates[0]
        return {"success": True, "recommended": best,
                "reason": self._explain(best, objective),
                "runners_up": [c["model_id"] + "@" + c["quant"]
                               for c in candidates[1:4]]}

    def _score(self, c: dict, profile, objective: str) -> float:
        s = 0.0
        qw = 3.0 if objective == "quality" else \
            (2.0 if objective == "balanced" else 1.0)
        s += qw * (c["quality"] / 10.0)
        s += (c["photorealism"] / 10.0) * (qw * 0.6)
        s += (c["prompt_adherence"] / 10.0) * (qw * 0.5)
        if objective in ("quality", "maximum"):
            s += (c["text_rendering"] / 10.0) * 1.0
        if not c["fits_ram"]:
            s -= 100.0
        if objective == "speed":
            s -= (c["params_b"] or 0) * 0.4
            s += (c["quant"] in ("q4", "q5")) * 1.0
        if objective == "memory":
            s -= (c["approx_weights_gb"] or 0) * 0.3
            order = C.QUANT_QUALITY_ORDER
            s += (order.index(c["quant"]) / len(order))
        res = c["gpu_residency"]
        if objective in ("speed", "balanced"):
            s += 1.0 if res == "full" else (0.4 if res == "partial" else -0.3)
        b = c.get("benchmark")
        if b and b.get("success"):
            s += 2.0
            if objective == "speed":
                s -= min((b.get("gen_s") or 60) / 120.0, 1.5)
        return round(s, 3)

    def _explain(self, c: dict, objective: str) -> str:
        return (f"Selected {c['name']} @ {c['quant'].upper()} "
                f"(~{c['approx_weights_gb']}GB weights) for objective "
                f"'{objective}': quality={c['quality']}/10, "
                f"photorealism={c['photorealism']}/10, "
                f"text={c['text_rendering']}/10, GPU residency="
                f"{c['gpu_residency']}, fits RAM={c['fits_ram']}. "
                f"Feasibility must still be confirmed by install+verify.")
