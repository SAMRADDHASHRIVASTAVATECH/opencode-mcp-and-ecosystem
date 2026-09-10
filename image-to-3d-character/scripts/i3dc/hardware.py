"""Hardware detection + VRAM/RAM feasibility checks.

Implements the local-first rule: before running any heavy model we detect the
machine's GPU/RAM, look up the model's approximate VRAM requirement, prefer
lightweight/quantized variants, and only then decide GPU vs CPU. Every decision
is reported; steps that cannot realistically run locally are flagged clearly.
"""
from __future__ import annotations

import os
import platform
import shutil
import subprocess
from dataclasses import dataclass, field, asdict

_RUNTIME_OVERHEAD_GB = 1.5   # activations + runtime above weights


@dataclass
class Hardware:
    os: str = os.name
    platform: str = platform.platform()
    ram_total_gb: float = 0.0
    ram_available_gb: float = 0.0
    gpu_present: bool = False
    gpu_vram_gb: float = 0.0
    gpu_vram_free_gb: float = 0.0
    gpu_name: str | None = None
    torch_cuda: bool = False
    notes: list = field(default_factory=list)

    @property
    def realistic_gpu_budget_gb(self) -> float:
        """What we may actually pin to VRAM (account headroom for activations)."""
        if not self.gpu_present:
            return 0.0
        free = self.gpu_vram_free_gb or self.gpu_vram_gb
        return max(0.0, free - 0.6)   # leave ~600MB for the display/runtime

    def can_run_on_gpu(self, weights_gb: float) -> bool:
        return self.gpu_present and (weights_gb + 0.6) <= self.realistic_gpu_budget_gb

    def to_dict(self) -> dict:
        return asdict(self)


def detect_hardware() -> Hardware:
    h = Hardware()
    # RAM
    try:
        import psutil
        vm = psutil.virtual_memory()
        h.ram_total_gb = round(vm.total / (1024 ** 3), 2)
        h.ram_available_gb = round(vm.available / (1024 ** 3), 2)
    except Exception:   # noqa: BLE001
        h.notes.append("psutil unavailable; RAM unknown")

    # GPU via nvidia-smi when present
    smi = shutil.which("nvidia-smi")
    if not smi and os.name == "nt":
        for cand in (r"C:\Windows\System32\nvidia-smi.exe",
                     r"C:\Program Files\NVIDIA Corporation\NVSMI\nvidia-smi.exe"):
            if os.path.exists(cand):
                smi = cand
                break
    if smi:
        try:
            out = subprocess.run([smi, "--query-gpu=name,memory.total,memory.free",
                                  "--format=csv,noheader,nounits"],
                                 capture_output=True, text=True, timeout=15)
            if out.returncode == 0 and out.stdout.strip():
                name, total, free = [x.strip() for x in out.stdout.splitlines()[0].split(",")]
                h.gpu_present = True
                h.gpu_name = name
                h.gpu_vram_gb = float(total) / 1024.0
                h.gpu_vram_free_gb = float(free) / 1024.0
        except Exception:   # noqa: BLE001
            pass

    # torch cuda probe (optional, honest)
    if shutil.which("python") or shutil.which("python3"):
        try:
            import importlib.util
            if importlib.util.find_spec("torch"):
                import torch
                h.torch_cuda = bool(torch.cuda.is_available())
                if h.torch_cuda and not h.gpu_present:
                    h.gpu_present = True
                    try:
                        h.gpu_name = torch.cuda.get_device_name(0)
                    except Exception:   # noqa: BLE001
                        pass
                    try:
                        props = torch.cuda.get_device_properties(0)
                        h.gpu_vram_gb = round(props.total_memory / (1024 ** 3), 2)
                    except Exception:   # noqa: BLE001
                        pass
        except Exception:   # noqa: BLE001
            pass
    return h


def _is_low_vram(h: Hardware) -> bool:
    return h.gpu_present and h.gpu_vram_gb <= 6


def recommend_device(h: Hardware, weights_gb: float | None = None,
                     device_pref: str = "auto") -> dict:
    """Decide gpu vs cpu vs mixed for a step, honouring a preference."""
    gpu_ok = h.can_run_on_gpu(weights_gb) if weights_gb is not None else h.gpu_present
    if device_pref == "cpu":
        return {"device": "cpu", "reason": "cpu forced by user", "gpu": False}
    if device_pref == "gpu":
        if not h.gpu_present:
            return {"device": "cpu", "reason": "no GPU detected",
                    "gpu": False, "warning": "GPU requested but not present"}
        return {"device": "gpu", "reason": "gpu forced by user", "gpu": True}
    # auto
    if not h.gpu_present:
        return {"device": "cpu", "reason": "no GPU detected; using CPU", "gpu": False}
    if weights_gb is not None and not gpu_ok:
        return {"device": "cpu", "reason":
                f"model needs ~{weights_gb:.1f}GB VRAM; only ~"
                f"{h.realistic_gpu_budget_gb:.1f}GB realistic; using CPU or a "
                f"lighter model", "gpu": False,
                "suggest_lighter": True}
    if _is_low_vram(h):
        return {"device": "gpu", "reason": f"low VRAM ({h.gpu_vram_gb:.0f}GB) — "
                "GPU with strong offload; prefer lightweight/quantized",
                "gpu": True, "low_vram": True}
    return {"device": "gpu", "reason": "GPU available and sufficient", "gpu": True}


def explain_limitation(h: Hardware, step: str, weights_gb: float,
                       lightest_gb: float) -> dict:
    """Produce an honest 'cannot realistically run locally' report."""
    if h.can_run_on_gpu(weights_gb):
        return {"runnable_local": True}
    gpu_budget = h.realistic_gpu_budget_gb if h.gpu_present else 0
    msg = (f"{step} needs ~{weights_gb:.1f}GB VRAM.")
    if not h.gpu_present:
        msg += " No GPU detected on this machine."
    else:
        msg += f" Only ~{gpu_budget:.1f}GB VRAM is realistically available."
    if lightest_gb and lightest_gb <= max(gpu_budget, h.ram_available_gb * 0.6):
        msg += (f" The lightest variant (~{lightest_gb:.1f}GB) could still run "
                "on CPU/offload.")
    return {"runnable_local": False, "reason": msg,
            "suggest_lightest": lightest_gb,
            "note": "Consider CPU/quantized or a lighter local model; no image "
                    "was uploaded to any external service."}
