"""Adaptive VRAM/RAM management.

Produces a memory plan for a chosen model+quant on the *detected* hardware:
which quantization is the highest-quality that can run reliably, how much GPU
residency is safe, how much CPU offload is needed, and RAM budget reservations.
All values are computed, never fabricated.
"""
from __future__ import annotations

from ..models import catalog as C

_RUNTIME_OVERHEAD_GB = 1.6
_RAM_OS_RESERVE_GB = 1.5
_RAM_MAX_USE_FRACTION = 0.85


class MemoryPlan:
    def __init__(self, **kw):
        self.quant = kw.get("quant")
        self.model_weights_gb = kw.get("model_weights_gb")
        self.gpu_residency = kw.get("gpu_residency", "partial")
        self.cpu_offload = kw.get("cpu_offload", True)
        self.vram_reserve_mb = kw.get("vram_reserve_mb")
        self.ram_budget_gb = kw.get("ram_budget_gb")
        self.ram_free_gb = kw.get("ram_free_gb")
        self.gpu_headroom_gb = kw.get("gpu_headroom_gb")
        self.recommended_resolution = kw.get("recommended_resolution")
        self.notes = kw.get("notes", [])

    def to_dict(self):
        return self.__dict__


class MemoryManager:
    def __init__(self, profile):
        self.profile = profile

    def choose_quant(self, model_family, objective: str = "quality") -> str:
        ram_total = self.profile.ram.get("total_gb") or 4
        ram_budget = max(1.0, (ram_total - _RAM_OS_RESERVE_GB) * _RAM_MAX_USE_FRACTION)
        sizes = model_family.quant_sizes()
        ordered = C.QUANT_QUALITY_ORDER
        if objective == "memory":
            ordered = list(reversed(ordered))
        for q in ordered:
            if q not in sizes:
                continue
            need = sizes[q] + _RUNTIME_OVERHEAD_GB
            if need <= ram_budget:
                return q
        return "q2"

    def plan_for(self, model_family, *, objective="quality",
                 quant: str | None = None,
                 resolution: tuple | None = None) -> MemoryPlan:
        ram_total = self.profile.ram.get("total_gb") or 4
        ram_avail = self.profile.ram.get("available_gb") or ram_total
        vram = self.profile.gpu.get("vram_gb") or 0
        gpu_present = bool(self.profile.gpu.get("present"))

        if quant is None:
            quant = self.choose_quant(model_family, objective)

        sizes = model_family.quant_sizes()
        wsize = sizes.get(quant, model_family.base_quant_size_gb)

        ram_budget = max(1.0, (ram_total - _RAM_OS_RESERVE_GB) * _RAM_MAX_USE_FRACTION)
        ram_free = round(ram_avail - _RAM_OS_RESERVE_GB, 2)

        notes = []
        if not gpu_present:
            residency = "none"
            notes.append("No GPU: full CPU execution.")
        elif vram >= wsize * 1.35:
            residency = "full"
            notes.append("Weights fit in VRAM with headroom.")
        elif vram >= wsize * 1.0:
            residency = "mostly"
            notes.append("Weights ~fit VRAM; keep headroom for activations.")
        elif vram > 0:
            residency = "partial"
            notes.append(f"Offload to CPU RAM (hybrid): VRAM {vram}GB < weights "
                         f"{round(wsize,2)}GB.")
        else:
            residency = "none"

        rec_res = resolution or self._resolution(vram, model_family, residency)

        vram_reserve = 0
        if gpu_present:
            vram_reserve = int(max(256, vram * 0.10 * 1024))

        return MemoryPlan(
            quant=quant, model_weights_gb=round(wsize, 2),
            gpu_residency=residency,
            cpu_offload=(residency != "full"),
            vram_reserve_mb=vram_reserve,
            ram_budget_gb=round(ram_budget, 2),
            ram_free_gb=ram_free,
            gpu_headroom_gb=round(max(0, vram - wsize), 2) if gpu_present else 0,
            recommended_resolution=rec_res,
            notes=notes)

    def _resolution(self, vram, fam, residency) -> list[int]:
        if not vram or residency == "none":
            return [1024, 1024] if fam.params_b <= 1 else [512, 768]
        if residency == "full":
            return [1024, 1024] if fam.params_b <= 4 else [832, 1216]
        return [768, 768] if fam.params_b <= 1 else [512, 768]

    def validate_before_load(self, wsize_gb: float) -> list[str]:
        warns = []
        ram_total = self.profile.ram.get("total_gb") or 4
        ram_avail = self.profile.ram.get("available_gb") or ram_total
        if wsize_gb > ram_avail * 0.9:
            warns.append("Model weights exceed safe RAM budget for offload; "
                         "stronger quantization recommended.")
        vram = self.profile.gpu.get("vram_gb") or 0
        if vram and wsize_gb > vram:
            warns.append(f"Model larger than VRAM ({vram}GB): requires CPU "
                         "offload (hybrid).")
        return warns
