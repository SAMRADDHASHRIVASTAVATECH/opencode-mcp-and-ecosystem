"""Image-to-3D reconstruction backends registry.

A single declarative source of truth about available reconstruction methods so
the skill is not hard-coded to one model. Each entry lists approximate VRAM
need, whether it runs locally, quantized/lightweight options, install notes and
output behaviour. Actual feasibility is decided per-run by hardware.py.
"""
from __future__ import annotations

from dataclasses import dataclass, asdict


@dataclass
class ReconBackend:
    id: str
    name: str
    kind: str                  # local-model | blender | external | cli
    vram_weights_gb: float     # primary weights only
    vram_total_need_gb: float  # realistic peak incl activations
    cpu_viable: bool
    quantized_variant: str | None = None
    quantized_vram_gb: float | None = None
    needs_blender: bool = False
    needs_gpu_model: bool = False
    external: bool = False
    license_note: str = ""
    output: str = "mesh"       # mesh | views | latent
    install: str = ""
    notes: str = ""

    def to_dict(self) -> dict:
        return asdict(self)


def registry() -> dict[str, ReconBackend]:
    return {
        "trellis": ReconBackend(
            id="trellis", name="Trellis (MS) image-to-3D",
            kind="local-model", vram_weights_gb=4.0, vram_total_need_gb=6.0,
            cpu_viable=True, quantized_variant="q4",
            quantized_vram_gb=2.5, needs_gpu_model=True,
            output="mesh",
            install=("pip install trellis (VapourSynth deps) + download weights. "
                     "Heavy: needs ~6GB; on 4GB use q4 + CPU offload."),
            notes="High quality dense mesh from single image."),
        "triposr": ReconBackend(
            id="triposr", name="TripoSR image-to-3D",
            kind="local-model", vram_weights_gb=1.0, vram_total_need_gb=2.0,
            cpu_viable=True, needs_gpu_model=True,
            output="mesh",
            install="pip install " \
                    "git+https://github.com/VAST-AI-Research/TripoSR.git",
            notes="Fast, single-image, lightweight (~1GB). Good fit for 4GB."),
        "zero123plus": ReconBackend(
            id="zero123plus", name="Zero123plus",
            kind="local-model", vram_weights_gb=3.0, vram_total_need_gb=4.5,
            cpu_viable=False, needs_gpu_model=True,
            output="mesh",
            install="pip install zero123plus",
            notes="Generates multi-view then mesh. Moderate VRAM."),
        "stablefast3d": ReconBackend(
            id="stablefast3d", name="Stable Fast 3D",
            kind="local-model", vram_weights_gb=2.0, vram_total_need_gb=3.5,
            cpu_viable=True, needs_gpu_model=True,
            output="mesh",
            install="pip install " \
                    "git+https://github.com/Stability-AI/StableFast3D.git",
            notes="Good UV/material bake; several configs by memory."),
        "blender_reconstruct": ReconBackend(
            id="blender_reconstruct", name="Blender manual/assisted reconstruction",
            kind="blender", vram_weights_gb=0.0, vram_total_need_gb=0.0,
            cpu_viable=True, needs_blender=True,
            output="mesh",
            install="Install Blender 4.x.",
            notes="Sculpt/box-model / camera-track from references. No GPU AI."),
        "external_api": ReconBackend(
            id="external_api", name="External image-to-3D API/service",
            kind="external", vram_weights_gb=0.0, vram_total_need_gb=0.0,
            cpu_viable=True, external=True,
            output="mesh",
            install="Configured service + key.",
            notes="ONLY used when explicitly configured/allowed. Never silent."),
    }


def best_local_backend(hw, device_pref="auto") -> tuple[str | None, dict]:
    """Pick the best *locally runnable* backend for the detected hardware."""
    from .hardware import recommend_device
    reg = registry()
    # order by VRAM asc, prefer lightest that runs
    ordered = sorted(reg.values(), key=lambda b: b.vram_total_need_gb)
    for b in ordered:
        if b.external:
            continue
        dec = recommend_device(hw, b.vram_weights_gb, device_pref)
        # for local GPU models require GPU or CPU-viability accepted
        if b.needs_gpu_model and not (hw.gpu_present or b.cpu_viable):
            continue
        if b.kind == "blender":
            # only viable if blender detected (checked elsewhere)
            continue
        if b.vram_total_need_gb <= max(hw.realistic_gpu_budget_gb,
                                       hw.ram_available_gb * 0.6) \
                or b.cpu_viable:
            return b.id, dec
    return None, {"device": "cpu",
                  "reason": "no lightweight local image-to-3D backend fits; "
                            "consider Blender reconstruction or a lighter model"}
