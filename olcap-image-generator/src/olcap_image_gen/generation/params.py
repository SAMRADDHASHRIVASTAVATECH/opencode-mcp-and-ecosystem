"""Generation parameter normalization + execution plan."""
from __future__ import annotations

from dataclasses import dataclass, field

QUALITY_PRESETS = {
    "speed": {"steps": 16, "upscale": False, "multi_stage": False,
              "cfg": 6.0},
    "balanced": {"steps": 24, "upscale": False, "multi_stage": False,
                 "cfg": 6.5},
    "high": {"steps": 30, "upscale": True, "multi_stage": False, "cfg": 7.0},
    "maximum": {"steps": 40, "upscale": True, "multi_stage": True,
                "cfg": 7.5, "refine": True},
}


@dataclass
class GenRequest:
    """Normalized user-facing generation request."""
    prompt: str
    negative_prompt: str = ""
    width: int = 1024
    height: int = 1024
    steps: int = 0
    seed: int = -1
    model: str = "auto"
    quant: str = "auto"
    quality: str = "maximum"
    offload: str = "auto"
    upscale: bool | None = None
    cfg: float | None = None
    strength: float = 0.6
    format: str = "png"
    backend: str = "auto"
    input_path: str = ""
    mask_path: str = ""
    metadata: bool = True


@dataclass
class ExecutionPlan:
    job_id: str
    model: str
    family: str
    quant: str
    params: dict = field(default_factory=dict)
    quality: str = "balanced"
    output_dir: str = "."
    filename: str = ""
    out_format: str = "png"
    memory_plan: dict | None = None
    input_path: str = ""
    mask_path: str = ""


def normalize(request: GenRequest, *, model_entry: dict | None = None,
              quality_preset: dict | None = None) -> dict:
    preset = quality_preset or QUALITY_PRESETS.get(request.quality,
                                                   QUALITY_PRESETS["balanced"])
    steps = request.steps or preset.get("steps", 30)
    cfg = request.cfg if request.cfg is not None else preset.get("cfg", 7.0)
    return {
        "prompt": request.prompt,
        "negative_prompt": request.negative_prompt,
        "width": max(64, min(request.width, 2048)),
        "height": max(64, min(request.height, 2048)),
        "steps": steps,
        "seed": request.seed,
        "cfg": cfg,
        "strength": request.strength,
        "upscale": request.upscale if request.upscale is not None
        else bool(preset.get("upscale", False)),
        "multi_stage": bool(preset.get("multi_stage", False)),
        "quality": request.quality,
    }
