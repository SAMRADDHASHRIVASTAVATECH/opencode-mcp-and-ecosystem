#!/usr/bin/env python3
"""Offline self-check for the skill (no GPU, no Blender required).

Verifies that the package imports, tool/hardware detection runs, image analysis
works on a real (generated) sample, reconstruction + backend selection planning
returns a sane decision, and a dry-run pipeline produces a valid report.

Usage:
    python scripts/selfcheck.py
"""
from __future__ import annotations

import sys
import tempfile
from pathlib import Path

_HERE = Path(__file__).resolve().parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

results = []


def check(name, fn):
    try:
        fn()
        results.append((name, True, ""))
    except Exception as e:   # noqa: BLE001
        results.append((name, False, f"{type(e).__name__}: {e}"))


def _make_sample_image(path: Path):
    from PIL import Image, ImageDraw
    img = Image.new("RGBA", (512, 1024), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    # a simple upright character-ish blob on a magenta solid bg in a padded frame
    d.rectangle([0, 0, 511, 1023], fill=(255, 0, 255, 255))   # solid bg
    d.ellipse([156, 80, 356, 280], fill=(255, 220, 180, 255))  # head
    d.rectangle([180, 280, 332, 720], fill=(70, 70, 200, 255))  # body
    d.ellipse([140, 300, 220, 460], fill=(200, 120, 40, 255))   # arm L
    d.ellipse([292, 300, 372, 460], fill=(200, 120, 40, 255))   # arm R
    img.save(str(path), format="PNG")


def t_import():
    import i3dc
    assert i3dc.__version__


def t_detect():
    import i3dc.toolchain as TC
    from i3dc.config import Config
    det = TC.detect_all(Config())
    assert "python" in det and det["python"].present
    assert "blender" in det


def t_hardware():
    import i3dc.hardware as H
    hw = H.detect_hardware()
    assert hw.ram_total_gb >= 0


def t_analysis(tmp):
    import i3dc.analysis as A
    info = A.analyze(str(tmp / "char.png"))
    assert info.width == 512 and info.height == 1024
    assert info.background_type in ("solid", "transparent")
    assert info.silhouette_fill > 0.1
    assert info.suitable_for_reconstruction in (True, False)


def t_registry_planning(tmp):
    import i3dc.registry as R
    from i3dc.hardware import Hardware
    hw = Hardware(gpu_present=False, ram_available_gb=16)
    bid, dec = R.best_local_backend(hw)
    assert bid  # should pick a CPU-viable lightweight local model


def t_recon_choose(tmp):
    import i3dc.recon as RC
    import i3dc.analysis as A
    from i3dc.hardware import Hardware
    from i3dc.config import Config
    info = A.analyze(str(tmp / "char.png"))
    hw = Hardware(gpu_present=False, ram_available_gb=16)
    toolchain = {"image_to_3d_local": {}, "blender": _Tool(False)}
    ch = RC.choose_recon(info, hw, toolchain, allow_external=False)
    # Honest: recommend an installable lightweight model (needs install) OR
    # report infeasible; never claim a produced mesh.
    if ch["feasible"]:
        oc = RC.run_recon(ch, info, hw, str(tmp / "recon"),
                          str(tmp / "char.png"), Config())
        assert oc.status in ("needs_mesh", "skipped", "failed")
        assert not oc.mesh_path   # nothing installed -> no mesh path produced
    else:
        assert ("install" in ch["reason"].lower()
                or "blender" in ch["reason"].lower())


class _Tool:
    def __init__(self, present, path=None):
        self.present = present
        self.path = path
        self.name = "x"
    def to_dict(self):
        return {"present": self.present, "path": self.path}


def t_dry_run_pipeline(tmp):
    from i3dc.config import Config
    from i3dc.pipeline import Options, run
    # isolate state root into tmp
    cfg = Config()
    cfg.state_root = str(tmp / "state")
    opts = Options(inputs=[str(tmp / "char.png")], output="selftest",
                   dry_run=True, format="glb")
    proj = run(cfg, opts)
    # report md must exist
    assert Path(proj["report_md"]).exists()
    # the pipeline must honestly NOT claim success (no blender/no mesh/no gpu)
    assert proj.get("validation_ok") is False


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="i3dc_selftest_") as td:
        tmp = Path(td)
        _make_sample_image(tmp / "char.png")
        check("import", t_import)
        check("toolchain detect", t_detect)
        check("hardware detect", t_hardware)
        check("image analysis", lambda: t_analysis(tmp))
        check("recon registry plan", lambda: t_registry_planning(tmp))
        check("recon choose (honest no-backend)", lambda: t_recon_choose(tmp))
        check("dry-run pipeline + report", lambda: t_dry_run_pipeline(tmp))

    ok = True
    for name, passed, err in results:
        print(("PASS " if passed else "FAIL ") + name +
              (("  -- " + err) if err else ""))
        ok = ok and passed
    print("SELFCHECK:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
