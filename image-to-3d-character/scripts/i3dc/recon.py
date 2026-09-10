"""3D reconstruction driver.

Decides which image-to-3D backend to run (from registry + installed detection +
hardware feasibility) and executes it as a subprocess on the user's machine.
It never fabricates a mesh and never uploads to an external service unless that
service is explicitly configured and allowed.
"""
from __future__ import annotations

import os
import subprocess
import sys
import textwrap
from dataclasses import dataclass, field, asdict
from pathlib import Path

from .registry import registry, best_local_backend
from .hardware import Hardware, recommend_device, explain_limitation
from .analysis import ImageInfo


@dataclass
class ReconOutcome:
    method: str = ""
    method_kind: str = ""
    mesh_path: str = ""
    source: str = ""
    status: str = "planned"        # planned | running | done | skipped | failed | needs_mesh
    runnable: bool = False
    device: str = ""
    reason: str = ""
    command: str = ""
    notes: list = field(default_factory=list)
    mesh_placeholder: bool = False

    def to_dict(self) -> dict:
        return asdict(self)


_MODEL_RUNNER = None   # template text emitted per supported engine


def _runner_for(backend_id: str) -> str:
    """Return a python runner template for a known library interface, or ''."""
    if backend_id in ("triposr",):
        return textwrap.dedent("""
            import torch, sys
            from PIL import Image
            from tripoSR import TripoSR  # provided by repo
            sys.path.insert(0, ".")
            img = Image.open(sys.argv[1]).convert("RGB")
            model = TripoSR.from_pretrained("stabilityai/TripoSR")
            if torch.cuda.is_available():
                model = model.to("cuda")
            else:
                model = model.to("cpu")
            mesh = model(img, num_samples=1)[0]
            mesh.export(sys.argv[2])
        """)
    if backend_id == "stablefast3d":
        return textwrap.dedent("""
            import sys, torch
            from PIL import Image
            from stable_fast_3d import StableFast3D
            img = Image.open(sys.argv[1]).convert("RGB")
            model = StableFast3D.from_pretrained("stabilityai/stable-fast-3d")
            if torch.cuda.is_available():
                model = model.to("cuda")
            out = model(img)
            mesh = out["mesh"] if isinstance(out, dict) else out
            # save .glb / obj
            import trimesh
            trimesh.exchange.export.export_mesh(mesh, sys.argv[2])
        """)
    if backend_id == "trellis":
        return textwrap.dedent("""
            import sys, torch
            from PIL import Image
            import trellis  # package provides high-level API
            from trellis.utils import postprocessing_utils as pp
            img = Image.open(sys.argv[1]).convert("RGB")
            assets = trellis.from_image(img, spec={
                "text_encoder": "dense",
                "decode": {"sample_res": 256, "quantize": True},
            })
            mesh = pp.postprocess_mesh(assets["gaussian_to_mesh"])
            mesh.export(sys.argv[2])
        """)
    if backend_id == "zero123plus":
        return textwrap.dedent("""
            import sys, torch
            from PIL import Image
            from zero123plus import Zero123PlusPipeline  # per repo
            img = Image.open(sys.argv[1]).convert("RGB")
            pipe = Zero123PlusPipeline.from_pretrained(
                "sudo-ai/zero123plus-v1.2")
            if torch.cuda.is_available():
                pipe = pipe.to("cuda")
            images = pipe(img, num_inference_steps=28)[0]
            # zero123plus yields views; reconstruct via provided scripts/colmap
            print("zero123plus produced views; run provided reconstruction to mesh.")
            for i, im in enumerate(images):
                im.save(sys.argv[2] + f"/view_{i}.png")
        """)
    return ""


def choose_recon(info: ImageInfo, hw: Hardware, toolchain: dict,
                 device_pref: str = "auto", allow_external: bool = False) -> dict:
    """Pick a reconstruction method and return feasibility + plan."""
    installed = toolchain.get("image_to_3d_local", {})
    present_ids = {k for k, v in installed.items() if v.present}
    reg = registry()

    # 1) local installed model
    if present_ids:
        for pid in present_ids:
            b = reg[pid]
            dec = recommend_device(hw, b.vram_total_need_gb, device_pref)
            if b.cpu_viable or hw.gpu_present:
                return {"backend_id": pid, "feasible": True,
                        "device": dec["device"], "reason": "installed local model",
                        "kind": "local-model"}
    # 2) best lightweight local that could be run (but needs install)
    if hw.gpu_present or hw.ram_available_gb >= 8:
        bid, dec = best_local_backend(hw, device_pref)
        if bid:
            return {"backend_id": bid, "feasible": True,
                    "device": dec["device"], "kind": "local-model",
                    "reason": "recommended lightweight local model (needs "
                              "install): " + dec["reason"]}
    # 3) blender reconstruction available
    if toolchain.get("blender") and toolchain["blender"].present:
        return {"backend_id": "blender_reconstruct", "feasible": True,
                "kind": "blender",
                "reason": "falling back to Blender-assisted reconstruction"}
    # 4) external only when allowed
    if allow_external:
        return {"backend_id": "external_api", "feasible": True,
                "kind": "external",
                "reason": "EXPLICIT external service use (allowed by config)."}
    return {"backend_id": None, "feasible": False,
            "reason": ("No locally runnable image-to-3D backend. Options: "
                       "install a lightweight model (see references/models.md), "
                       "install/run Blender for manual reconstruction, or "
                       "provide an existing mesh.")}


def run_recon(recon_choice: dict, info: ImageInfo, hw: Hardware,
              out_dir: str, source_image: str, cfg) -> ReconOutcome:
    """Execute the chosen reconstruction. Returns honest outcome."""
    oc = ReconOutcome(method=recon_choice.get("backend_id", ""),
                      method_kind=recon_choice.get("kind", ""),
                      source=source_image, device=recon_choice.get("device", ""))
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    bid = oc.method
    if not bid:
        oc.status = "needs_mesh"
        oc.reason = recon_choice.get("reason", "no method")
        oc.notes.append("No mesh was generated. Provide an existing mesh or "
                        "install a reconstruction backend; no image was "
                        "uploaded anywhere.")
        return oc

    if recon_choice.get("kind") == "external":
        oc.status = "needs_mesh"
        oc.reason = ("External service would be used, but only when the source "
                     "image is explicitly cleared for upload and a service+key "
                     "are configured. Not run now.")
        oc.notes.append("Never silent upload: confirm before enabling.")
        return oc

    if recon_choice.get("kind") == "blender":
        oc.status = "needs_mesh"
        oc.reason = ("Blender-assisted reconstruction selected. This is "
                     "interactive/assisted (import references, model the "
                     "character). Producing geometry automatically from a "
                     "single image requires an image-to-3D model; install one "
                     "for full automation, or build in Blender manually.")
        oc.notes.append("A manual/assisted mesh in Blender is the fallback; "
                        "continue processing it once saved.")
        return oc

    # local-model backend
    runner = _runner_for(bid)
    if not runner:
        oc.status = "failed"
        oc.reason = f"no executable runner defined for backend '{bid}'"
        return oc
    # feasibility for real run
    need = registry()[bid].vram_total_need_gb
    lim = explain_limitation(hw, f"{bid}", need, need)
    if not lim["runnable_local"]:
        oc.status = "skipped"
        oc.reason = lim["reason"]
        oc.notes.append(lim.get("note", ""))
        return oc
    oc.runnable = True
    mesh_target = str(out_dir / "raw_mesh.glb")
    py = sys.executable or "python"
    runner_file = out_dir / "_runner_recon.py"
    runner_file.write_text(runner, encoding="utf-8")
    cmd = [py, str(runner_file), str(source_image), mesh_target]
    oc.command = " ".join(cmd)
    oc.status = "running"
    try:
        res = subprocess.run(cmd, capture_output=True, text=True,
                             timeout=3600, cwd=str(out_dir))
    except Exception as e:   # noqa: BLE001
        oc.status = "failed"
        oc.reason = f"failed to launch recon: {e}"
        return oc
    if Path(mesh_target).exists():
        oc.mesh_path = mesh_target
        oc.status = "done"
    else:
        oc.status = "failed"
        tail = (res.stdout or res.stderr or "")[-1500:]
        oc.reason = (f"reconstruction backend did not produce a mesh.\n"
                     f"exit={res.returncode}\n{tail}")
    return oc


def import_existing_mesh(mesh_path: str, out_dir: str) -> ReconOutcome:
    """Use a mesh the user already has (skip reconstruction)."""
    p = Path(mesh_path)
    oc = ReconOutcome(method="provided_mesh", method_kind="provided",
                      mesh_path=str(p), source="", status="done" if p.exists()
                      else "needs_mesh", runnable=True,
                      reason="using user-provided mesh; reconstruction skipped" if
                      p.exists() else "mesh not found")
    return oc
