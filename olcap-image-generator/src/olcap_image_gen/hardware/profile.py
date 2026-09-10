"""Structured hardware profile data model."""
from __future__ import annotations


class Profile:
    def __init__(self):
        self.system = {"os": None, "architecture": None, "platform": None}
        self.cpu = {"model": None, "cores": None, "threads": None,
                    "physical_cores": None}
        self.ram = {"total_gb": None, "available_gb": None, "used_gb": None}
        self.gpu = {"present": False, "vendor": None, "model": None,
                    "vram_gb": None, "vram_free_gb": None,
                    "cuda_available": None, "cuda_version": None,
                    "driver_version": None, "compute_capability": None,
                    "utilization_percent": None, "temperature_c": None}
        self.storage = {"system_drive": None, "free_gb": None, "total_gb": None,
                        "fs": None}
        self.software = {"python_version": None, "git": None, "node": None,
                         "npm": None, "comfyui": None, "torch": None,
                         "cuda_toolkit": None}
        self.recommended_execution = {
            "mode": "cpu", "cpu_offload": True,
            "gpu_offload": "none",
            "notes": []}
        self._sources = {}

    def to_dict(self) -> dict:
        return {"system": self.system, "cpu": self.cpu, "ram": self.ram,
                "gpu": self.gpu, "storage": self.storage,
                "software": self.software,
                "recommended_execution": self.recommended_execution}

    def summary(self) -> str:
        g = self.gpu
        gpu = (f"{g['model']} ({g['vram_gb']}GB VRAM, CUDA="
               f"{bool(g['cuda_available'])}))") if g["present"] else "none"
        return (f"OS={self.system['os']} | CPU={self.cpu['model']} "
                f"{self.cpu['cores']}c | RAM={self.ram['total_gb']}GB | "
                f"GPU={gpu}")
