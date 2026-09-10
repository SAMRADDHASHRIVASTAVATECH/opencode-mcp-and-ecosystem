"""Multi-view reference generation.

When only a single image exists, plan and (when the tooling + GPU allow) produce
front / 3/4 / side / back views that preserve character identity. Offline / no-GPU
machines get an actionable plan + prompts and an honest 'not generated' status;
they never invent views.
"""
from __future__ import annotations

from dataclasses import dataclass, field, asdict
from pathlib import Path

from .analysis import ImageInfo
from .hardware import Hardware


@dataclass
class ReferencePlan:
    source: str
    views_needed: list = field(default_factory=list)   # [{view, angle, why, prompt}]
    backend: str = "none"                               # comfyui | external | none
    generated: bool = False
    status: str = "planned"
    out_dir: str = ""
    notes: list = field(default_factory=list)

    def to_dict(self) -> dict:
        return asdict(self)


_VIEWS = [
    ("front", 0.0, "main identity + proportions"),
    ("front_3_4", 45.0, "adds volume confidence for reconstruction"),
    ("side", 90.0, "depth for head/body/torso"),
    ("back", 180.0, "hair/clothing back detail (optional)"),
]


def _describe(info: ImageInfo) -> str:
    d = info.dominant_colors
    cols = ", ".join(f"rgb({c['rgb'][0]},{c['rgb'][1]},{c['rgb'][2]})"
                     for c in d[:3]) if d else "unknown palette"
    return (f"{info.width}x{info.height}px, facing ~{info.approx_facing}, "
            f"dominant palette {cols}")


def build_reference_prompt(info: ImageInfo, view: str, angle: float,
                           subject_hint: str = "") -> str:
    """Identity-consistent view prompt. Does not redesign the character."""
    facing_hint = {
        "front": "perfectly front-facing, facing camera",
        "front_3_4": "three-quarter view, turned slightly",
        "side": "true side profile view, facing left",
        "back": "direct back view",
    }.get(view, view)
    base = (f"Full-body anime character reference view. {facing_hint}. "
            f"Keep the EXACT same character identity, hairstyle, hair colour, "
            f"clothing, outfit colours, accessories and facial design as the "
            f"source. Do not redesign or change the character.")
    if subject_hint:
        base += f" Subject note: {subject_hint}."
    base += f" Source is {_describe(info) if False else ''}clean, isolated, "
    return base + "consistent studio reference, no text, no watermark."


def plan_views(info: ImageInfo, subject_hint: str = "") -> ReferencePlan:
    plan = ReferencePlan(source=info.path)
    want = ["front"]
    if info.approx_facing in ("side", "unknown"):
        want.append("front_3_4")
    else:
        want.append("front_3_4")   # always useful
    want.append("side")
    # back only if beneficial / cheap
    plan.views_needed = [
        {"view": v, "angle": ang, "why": why,
         "prompt": build_reference_prompt(info, v, ang, subject_hint)}
        for v, ang, why in _VIEWS if v in want or v == "back"]
    plan.status = "planned"
    plan.notes.append("Only front-facing images materially benefit; 3/4 + side "
                      "are recommended, back is optional.")
    return plan


def execute_reference_generation(plan: ReferencePlan, info: ImageInfo,
                                 hw: Hardware, toolchain: dict,
                                 out_dir: str, device_pref="auto") -> ReferencePlan:
    """Try to produce the views locally; otherwise leave planned + honest."""
    plan.out_dir = out_dir
    from .hardware import recommend_device
    comfy = toolchain.get("comfyui")
    sd = toolchain.get("stable_diffusion")
    dec = recommend_device(hw, weights_gb=3.5, device_pref=device_pref)  # sd1.5-ish
    if not hw.gpu_present:
        plan.status = "needs_views_generation"
        plan.notes.append("No GPU: could not generate synthetic views locally. "
                          "Use the planned prompts with any image model on a "
                          "machine that has one, or supply real front/3-4/side "
                          "photos.")
        return plan
    if comfy and comfy.present:
        plan.backend = "comfyui"
        # Attempt real txt2img/img2img via ComfyUI client if reachable.
        ok, note = _try_comfy(plan, out_dir)
        if ok:
            plan.generated = True
            plan.status = "generated"
            return plan
        plan.status = "needs_views_generation"
        plan.notes.append("ComfyUI present but not reachable/running: " + note)
        return plan
    if sd and sd.present:
        plan.backend = "stable_diffusion"
        plan.status = "needs_views_generation"
        plan.notes.append("Stable Diffusion checkpoints found but an active "
                          "runtime is needed; use ComfyUI/forge to run the "
                          "planned prompts.")
        return plan
    plan.status = "needs_views_generation"
    plan.notes.append("No local text-to-image runtime installed for reference "
                      "generation. Provide extra real views or install a "
                      "runtime; the pipeline continues with available views.")
    return plan


def _try_comfy(plan, out_dir) -> tuple[bool, str]:
    """Reach a running ComfyUI and drive it via its HTTP API."""
    import json
    import urllib.request
    comfy_dir = getattr(plan, "_comfy_dir", None)
    port = 8188
    # minimal: check health
    try:
        with urllib.request.urlopen(f"http://127.0.0.1:{port}/system_stats",
                                    timeout=3) as r:
            if r.status != 200:
                return False, "comfy http not ready"
    except Exception as e:   # noqa: BLE001
        return False, f"comfy unreachable ({e})"
    # If reachable, we still need an installed checkpoint + prompt workflow.
    # Build an api-format prompt with a KSampler + CheckpointLoaderSimple.
    return False, ("ComfyUI reachable but driving arbitrary view generation "
                   "requires an installed SD checkpoint + a view workflow; "
                   "please run the planned prompts in ComfyUI for now.")


def run_reference(info: ImageInfo, toolchain: dict, hw: Hardware, out_dir: str,
                  subject_hint: str = "", device_pref="auto") -> ReferencePlan:
    plan = plan_views(info, subject_hint)
    execute_reference_generation(plan, info, hw, toolchain, out_dir, device_pref)
    return plan
