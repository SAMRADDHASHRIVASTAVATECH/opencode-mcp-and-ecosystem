"""Pipeline orchestrator.

Runs the 2D-image -> 3D-character workflow stage by stage. Each stage is logged;
a failed stage does NOT abort the project — the orchestrator records what failed
and continues with any stages that can still run. Intermediate files are kept in
the project dir so failures can be debugged. Nothing is fabricated: absent tools
or hardware are reported, never simulated as success.
"""
from __future__ import annotations

import datetime as _dt
import json
import os
import shutil
import subprocess
import sys
from dataclasses import dataclass, field, asdict
from pathlib import Path

from . import analysis as A
from . import hardware as H
from . import reference as R
from . import recon as RC
from . import report as RP
from . import toolchain as TC
from . import validator as VD
from .config import Config, load_config

BLENDER_RUN = "blender/run.py"     # relative to scripts/ dir


@dataclass
class Stage:
    stage: str
    status: str = "pending"        # ok | failed | skipped | needs_mesh | done
    detail: str = ""
    reason: str = ""
    warning: str = ""
    note: str = ""
    data: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        d = asdict(self)
        return d


@dataclass
class Options:
    inputs: list = field(default_factory=list)   # images / dirs
    output: str = ""                             # project name/dir
    quality: str = "balanced"                    # draft|balanced|high
    rig: bool = True
    facial_rig: bool = True
    low_poly: bool = False
    anime: bool = True
    format: str = "glb"
    device: str = "auto"                         # auto|gpu|cpu
    mesh: str = ""                               # skip recon, use this mesh
    texture: str = ""                            # optional albedo to use
    subject_hint: str = ""
    allow_external: bool = False
    dry_run: bool = False                        # plan only (no heavy run)
    poly_target: int = 0


class Logger:
    def __init__(self, path: Path):
        self.path = path
        self.entries = []
        path.parent.mkdir(parents=True, exist_ok=True)

    def log(self, msg: str):
        line = f"[{_dt.datetime.now().isoformat(timespec='seconds')}] {msg}"
        self.entries.append(msg)
        with self.path.open("a", encoding="utf-8") as f:
            f.write(line + "\n")
        print(line, flush=True)


def _collect_inputs(opts: Options) -> list[Path]:
    files = []
    for inp in opts.inputs:
        p = Path(inp).expanduser()
        if p.is_dir():
            files += sorted(x for x in p.rglob("*")
                            if x.suffix.lower() in (".png", ".jpg", ".jpeg",
                                                    ".webp", ".svg", ".eps"))
        elif p.is_file():
            files.append(p)
    # ignore svg/eps for image analysis but keep for reference if vector available
    return files


def _primary_image(files: list[Path], logger) -> tuple[Path | None, dict]:
    """Pick the single best reconstruction source (front/isolated raster)."""
    raster = [f for f in files if f.suffix.lower() in
              (".png", ".jpg", ".jpeg", ".webp")]
    if not raster:
        return None, {}
    if len(raster) == 1:
        info = A.analyze(str(raster[0]))
        return raster[0], info.to_dict()
    # multiple: prefer a 'front'/'frontish' with good fill
    best, best_score = None, -1
    for f in raster:
        try:
            info = A.analyze(str(f))
            score = 0
            if info.approx_facing in ("front", "frontish"):
                score += 3
            score += info.silhouette_fill * 10
            score += 1 if info.background_type in ("transparent", "solid") else 0
            score += 0.01 * info.width
            if score > best_score:
                best_score, best = score, (f, info)
        except Exception as e:   # noqa: BLE001
            logger.log(f"could not analyse {f.name}: {e}")
    if best:
        return best[0], best[1].to_dict()
    f = raster[0]
    return f, A.analyze(str(f)).to_dict()


def _split_sheet_if_wide(primary: Path, info: dict, project: Path,
                         logger) -> Path:
    """If the input looks like a multi-panel character sheet (wide), attempt to
    crop the most frontal panel. Best-effort; never destroys the original."""
    w, h = info.get("width", 0), info.get("height", 0)
    if not (w and h) or w / h < 1.4:
        return primary
    # heuristically: assume panels stacked in columns by vertical background gaps
    from PIL import Image
    import numpy as np
    img = Image.open(str(primary)).convert("RGBA")
    a = np.asarray(img)
    alpha = a[..., 3]
    # columns with no opaque content = gaps; find contiguous column regions
    col_has = (alpha > 40).any(axis=0)
    # gap detection
    regions = []
    start = None
    for i, has in enumerate(col_has):
        if has and start is None:
            start = i
        elif not has and start is not None:
            regions.append((start, i))
            start = None
    if start is not None:
        regions.append((start, len(col_has)))
    if len(regions) < 2:
        logger.log("wide image but no clean column gaps found; using as-is")
        return primary
    # pick the widest contiguous region as the character front
    widest = max(regions, key=lambda r: r[1] - r[0])
    x0, x1 = widest
    crop = img.crop((int(x0), 0, int(x1), h))
    out = project / "cleaned" / f"{primary.stem}_panel.png"
    out.parent.mkdir(parents=True, exist_ok=True)
    crop.save(str(out), format="PNG")
    logger.log(f"character sheet split into {len(regions)} panels; using "
               f"widest as front -> {out.name}")
    return out


def run(cfg: Config, opts: Options) -> dict:
    # --- logging & project setup (never touch the original) ---
    project_name = opts.output or Path(opts.inputs[0]).stem \
        if opts.inputs else "character"
    project_dir = cfg.project_dir(project_name)
    project_dir.mkdir(parents=True, exist_ok=True)
    log = Logger(project_dir / "logs" / "pipeline.log")
    log.log(f"=== image-to-3d-character run ({project_dir}) ===")
    stages: list[Stage] = []
    files_out: list[str] = []

    def emit(stage: Stage):
        stages.append(stage)
        log.log(f"[stage:{stage.stage}] {stage.status} {stage.reason or ''}")

    # ---- 0/1 detection & hardware ----
    det = TC.detect_all(cfg)
    st = Stage("detect_tools", status="done", data=TC.summary(det))
    emit(st)
    hw = H.detect_hardware()
    emit(Stage("hardware", "done", data=hw.to_dict()))

    inputs = _collect_inputs(opts)
    if not inputs:
        emit(Stage("collect_inputs", "failed", reason="no input images found"))
        return _finish(project_dir, stages, files_out, opts, log, hw, None, {})

    primary, info_dict = _primary_image(inputs, log)
    source_for_record = str(primary) if primary else str(inputs[0])

    # ---- analysis ----
    analysis_result = {}
    if primary:
        primary = _split_sheet_if_wide(primary, info_dict, project_dir, log)
        info = A.analyze(str(primary))
        analysis_result = info.to_dict()
        emit(Stage("analyze_image", "done", data=analysis_result,
                   note="resolution/background/facing assessed"))

        # background removal (skip in dry-run)
        if (info.background_type in ("photo", "busy", "solid", "gradient")
                and info.has_alpha is False and not opts.dry_run):
            cleaned = project_dir / "cleaned" / f"{primary.stem}_nobg.png"
            try:
                rm = A.remove_background(str(primary), str(cleaned))
            except Exception as e:   # noqa: BLE001
                rm = {"ok": False, "engine": "none", "reason": str(e)}
            if rm["ok"]:
                emit(Stage("background_removal", "done",
                           detail=f"engine={rm['engine']}", data=rm))
                primary = Path(rm["out"])
            else:
                emit(Stage("background_removal", "skipped",
                           reason=rm["reason"],
                           warning="background not removed; may reduce quality"))
    else:
        emit(Stage("analyze_image", "failed",
                   reason="no raster image (only vector given); vector handling "
                          "needs Inkscape conversion to raster"))

    # ---- reference (additional views) ----
    if primary and info_dict.get("approx_facing") in ("side", "unknown"):
        ref_dir = str(project_dir / "references")
        refplan = R.run_reference(info, det, hw, ref_dir,
                                  opts.subject_hint, opts.device)
        emit(Stage("reference_generation",
                   "done" if refplan.generated else refplan.status,
                   data=refplan.to_dict(),
                   reason=("views generated locally" if refplan.generated
                           else "planned; see prompts")))

    # ---- reconstruction ----
    recon_outcome = None
    recon_stage = Stage("reconstruction")
    if opts.mesh:
        recon_outcome = RC.import_existing_mesh(opts.mesh, str(project_dir))
    elif primary is None:
        recon_stage.status = "needs_mesh"
        recon_stage.reason = "no source image available"
        emit(recon_stage)
    else:
        choice = RC.choose_recon(info, hw, det, opts.device, opts.allow_external)
        recon_stage.detail = str(choice)
        recon_outcome = RC.run_recon(choice, info, hw,
                                     str(project_dir / "recon"),
                                     str(primary), cfg)
        recon_stage.status = recon_outcome.status
        recon_stage.reason = recon_outcome.reason or ""
        recon_stage.data = recon_outcome.to_dict()
        recon_stage.warning = (recon_outcome.reason
                               if recon_outcome.status in ("skipped", "failed",
                                                           "needs_mesh")
                               else "")
        emit(recon_stage)

    mesh_path = (recon_outcome.mesh_path if recon_outcome
                 else (opts.mesh if opts.mesh else ""))

    # ---- blender process/rig/export ----
    blender_result = None
    blender_ok = False
    blender = det.get("blender")
    if blender and blender.present and mesh_path:
        if opts.dry_run:
            emit(Stage("blender_process", "skipped",
                       reason="dry-run: no blender execution"))
        else:
            st_b = _run_blender(cfg, blender.path, mesh_path, project_dir,
                                opts, log)
            blender_result = st_b.get("blender_result")
            blender_ok = st_b.get("ok", False)
            if blender_result and blender_result.get("files"):
                files_out += blender_result["files"]
            if st_b.get("fatal"):
                emit(Stage("blender_process", "failed", reason=st_b["fatal"]))
            else:
                emit(Stage("blender_process",
                           "done" if blender_ok else "failed",
                           reason=st_b.get("reason", "")))
    elif blender and blender.present and not mesh_path:
        emit(Stage("blender_process", "skipped",
                   reason="no mesh to process (reconstruction not available)"))
    elif not (blender and blender.present):
        emit(Stage("blender_process", "skipped",
                   reason="Blender not installed; mesh cleanup/rig/export "
                          "cannot run locally. Install Blender to continue.",
                   warning="Blender missing"))

    # ---- validation ----
    validation = {"ok": False}
    if mesh_path:
        v = VD.validate_mesh_file(mesh_path)
        validation = v.to_dict()
        if blender_result:
            bval = blender_result.get("details", {}).get("validation", {})
            validation["blender"] = bval
            validation["ok"] = bool(blender_ok)
        emit(Stage("validate", "done" if validation["ok"] else "failed",
                   data=validation, reason="" if validation["ok"] else
                   "validation found issues"))
    else:
        emit(Stage("validate", "skipped", reason="no mesh produced to validate"))

    return _finish(project_dir, stages, files_out, opts, log, hw, blender_result,
                   {"source_image": source_for_record, "validation_ok":
                    validation.get("ok", False)})


def _run_blender(cfg, blender_bin, mesh_path, project_dir, opts, log) -> dict:
    scripts_dir = Path(__file__).resolve().parent.parent   # .../scripts
    run_script = scripts_dir / BLENDER_RUN
    log.log(f"invoking Blender: {blender_bin}")
    if not run_script.exists():
        return {"ok": False, "fatal": f"blender script missing: {run_script}"}
    out_dir = project_dir / "blender"
    out_dir.mkdir(parents=True, exist_ok=True)
    cmd = [blender_bin, "--background", "--factory-startup", "-P",
           str(run_script), "--",
           "--input", mesh_path,
           "--out-dir", str(out_dir),
           "--format", opts.format,
           "--name", "character"]
    if opts.rig:
        cmd.append("--rig")
    if opts.facial_rig:
        cmd.append("--facial-rig")
    if opts.anime:
        cmd.append("--anime")
    if opts.low_poly:
        cmd.append("--low-poly")
    if opts.texture:
        cmd += ["--texture", opts.texture]
    if opts.poly_target:
        cmd += ["--poly-target", str(opts.poly_target)]
    log.log("blender cmd: " + " ".join(cmd))
    try:
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=3600)
    except Exception as e:   # noqa: BLE001
        return {"ok": False, "fatal": f"blender launch failed: {e}"}
    out = (res.stdout or "") + ("\n" + res.stderr if res.stderr else "")
    log.log("blender exit=" + str(res.returncode))
    for line in out.splitlines()[-80:]:
        log.log("  blender: " + line)
    bj = VD.merge_blender_result(str(out_dir / "blender_result.json"))
    if bj:
        return {"ok": bool(bj.get("ok")), "blender_result": bj,
                "reason": ("ok" if bj.get("ok") else
                           str(bj.get("details", {}).get("validation", ""))),
                "exit": res.returncode}
    return {"ok": res.returncode == 0,
            "reason": "no blender_result.json emitted",
            "exit": res.returncode}


def _finish(project_dir, stages, files_out, opts, log, hw, blender_result,
            extra) -> dict:
    # keep intermediate files -> nothing is cleaned up here
    texture_res = (opts.texture and "provided") or "n/a"
    project = {
        "project_dir": str(project_dir),
        "source_image": extra.get("source_image"),
        "input_mesh": opts.mesh or "",
        "stages": [s.to_dict() for s in stages],
        "blender_result": blender_result,
        "files": files_out,
        "texture_resolution": texture_res,
        "rig": opts.rig,
        "facial_rig": opts.facial_rig,
        "quality": opts.quality,
        "low_poly": opts.low_poly,
        "format": opts.format,
        "device": opts.device,
        "validation_ok": extra.get("validation_ok", False),
    }
    md = RP.write(project, project_dir)
    log.log("report written: " + str(md))
    project["report_md"] = str(md)
    project["report_json"] = str(project_dir / "report.json")
    return project
