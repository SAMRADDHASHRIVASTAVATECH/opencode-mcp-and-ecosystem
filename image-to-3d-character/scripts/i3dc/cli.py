"""Command-line entry point: image-to-3d-character

Minimises manual work: a single command drives the whole pipeline as far as the
installed tools allow.
"""
from __future__ import annotations

import argparse
import json
import sys

from .config import load_config
from .pipeline import Options, run
from . import toolchain as TC
from . import hardware as H


def _ap() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="image-to-3d-character",
        description="Convert a 2D character image into an animation-ready 3D "
                    "character (as far as the local tools allow).")
    p.add_argument("inputs", nargs="*", help="image(s)/directories/character sheet")
    p.add_argument("--output", "-o", default="", help="project/output name")
    p.add_argument("--quality", default="balanced",
                   choices=["draft", "balanced", "high"])
    p.add_argument("--no-rig", dest="rig", action="store_false")
    p.add_argument("--rig", dest="rig", action="store_true")
    p.set_defaults(rig=True)
    p.add_argument("--no-facial-rig", dest="facial_rig", action="store_false")
    p.add_argument("--facial-rig", dest="facial_rig", action="store_true")
    p.set_defaults(facial_rig=True)
    p.add_argument("--anime", dest="anime", action="store_true", default=True)
    p.add_argument("--no-anime", dest="anime", action="store_false")
    p.add_argument("--low-poly", action="store_true")
    p.add_argument("--format", default="glb",
                   choices=["glb", "gltf", "fbx", "obj", "stl"])
    p.add_argument("--cpu", dest="device", action="store_const", const="cpu")
    p.add_argument("--gpu", dest="device", action="store_const", const="gpu")
    p.set_defaults(device="auto")
    p.add_argument("--mesh", default="", help="skip reconstruction; use this mesh")
    p.add_argument("--texture", default="", help="albedo image to use as texture")
    p.add_argument("--subject-hint", default="",
                   help="short text describing the character identity")
    p.add_argument("--allow-external", action="store_true",
                   help="allow an EXPLICIT external image-to-3D service")
    p.add_argument("--dry-run", action="store_true",
                   help="detect tools/hardware + plan, run nothing heavy")
    p.add_argument("--detect", action="store_true",
                   help="only inspect installed tools + hardware, then exit")
    p.add_argument("--poly-target", type=int, default=0)
    p.add_argument("--config", default="")
    return p


def _print_detect():
    cfg = load_config()
    det = TC.detect_all(cfg)
    hw = H.detect_hardware()

    def _jsonable(x):
        if hasattr(x, "to_dict"):
            return x.to_dict()
        if isinstance(x, dict):
            return {k: _jsonable(v) for k, v in x.items()}
        if isinstance(x, list):
            return [_jsonable(v) for v in x]
        return x

    print(json.dumps({"hardware": hw.to_dict(),
                      "tools": {k: _jsonable(v) for k, v in det.items()}},
                     indent=2, default=str))
    s = TC.summary(det)
    for row in s["apps"]:
        print(f"{row['tool']:<18} {row['status']:<8} {row['path'] or ''}")
    print("GPU:", hw.gpu_name or "none",
          f"({hw.gpu_vram_gb:.0f}GB)" if hw.gpu_present else "")
    print("RAM:", hw.ram_total_gb, "GB")
    return s


def main(argv=None) -> int:
    args = _ap().parse_args(argv)
    if args.detect:
        _print_detect()
        return 0
    if not args.inputs:
        _ap().error("provide at least one input image or directory")
    cfg = load_config(args.config)
    opts = Options(
        inputs=args.inputs, output=args.output, quality=args.quality,
        rig=args.rig, facial_rig=args.facial_rig, low_poly=args.low_poly,
        anime=args.anime, format=args.format, device=args.device,
        mesh=args.mesh, texture=args.texture, subject_hint=args.subject_hint,
        allow_external=args.allow_external, dry_run=args.dry_run,
        poly_target=args.poly_target)
    project = run(cfg, opts)
    # print concise final line for agents
    print("\n[final] report:", project.get("report_md"))
    ok = project.get("validation_ok") is True and bool(project.get("files"))
    print("[final] exported_files:", project.get("files"))
    print("[final] validation_ok:", project.get("validation_ok"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
