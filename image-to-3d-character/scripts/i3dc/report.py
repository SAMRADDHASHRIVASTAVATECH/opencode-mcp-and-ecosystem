"""Final pipeline report generation.

Produces a structured + human-readable report covering source, method, files,
polygon count, texture resolution, object count, armature/facial status, export
formats, warnings and recommended next steps. Written as JSON + Markdown into
the project dir.
"""
from __future__ import annotations

import json
from pathlib import Path


def build_report(project: dict) -> dict:
    stages = project.get("stages", [])
    bl = project.get("blender_result", None)
    files = project.get("files", [])
    warnings = []
    notes = []

    recon = _stage(stages, "reconstruction")
    recon_method = recon.get("method") or "none"
    mesh_path = recon.get("mesh_path") or project.get("input_mesh") or ""
    poly = _poly_count(bl, recon)
    obj_count = _obj_count(bl)
    armature = _armature_status(bl, project)
    facial = _facial_status(bl, project)
    val = project.get("validation", {})

    # gather warnings from anywhere
    for s in stages:
        if s.get("warning"):
            warnings.append(s["warning"])
        if s.get("status") in ("skipped", "failed", "needs_mesh"):
            warnings.append(f"stage '{s['stage']}' -> {s['status']}: "
                            f"{s.get('reason','')}")

    report = {
        "source_image": project.get("source_image"),
        "project_dir": project.get("project_dir"),
        "reconstruction_method": recon_method,
        "reconstruction_kind": recon.get("method_kind", ""),
        "generated_files": files,
        "export_formats": sorted({p.split(".")[-1] for p in files
                                  if "." in Path(p).name}),
        "polygon_count": poly,
        "texture_resolution": project.get("texture_resolution"),
        "number_of_objects": obj_count,
        "armature_status": armature,
        "facial_rig_status": facial,
        "validation_ok": val.get("ok", False),
        "warnings": warnings,
        "notes": notes + [s.get("note") for s in stages if s.get("note")],
        "recommended_next_steps": _next_steps(project, warnings),
    }
    return report


def _stage(stages, name):
    for s in stages:
        if s.get("stage") == name:
            return s
    return {}


def _poly_count(bl, recon):
    if bl and bl.get("details", {}).get("validation"):
        t = bl["details"]["validation"].get("total_tris")
        if t is not None:
            return t
    if recon.get("mesh_path"):
        # rough via validator if possible
        from .validator import validate_mesh_file
        v = validate_mesh_file(recon["mesh_path"])
        if v.summary.get("faces"):
            return v.summary["faces"]
    return None


def _obj_count(bl):
    if bl:
        clean = bl.get("details", {}).get("cleanup")
        if clean and "mesh_objects" in clean:
            return clean["mesh_objects"]
    return None


def _armature_status(bl, project):
    if project.get("rig") is False:
        return "not_requested"
    if bl:
        rg = bl.get("details", {}).get("rig", {})
        if rg.get("armature"):
            return "armature_created" + ("+weights" if rg.get("weights")
                                         else "_no_weights")
        if rg.get("error"):
            return "failed:" + rg["error"]
    return "unknown_no_blender_result"


def _facial_status(bl, project):
    if project.get("facial_rig") is False:
        return "not_requested"
    if bl:
        rg = bl.get("details", {}).get("rig", {})
        return rg.get("facial", "none")
    return "unknown_no_blender_result"


def _next_steps(project, warnings):
    steps = []
    if project.get("validation_ok") is True:
        steps.append("Model validated. Optionally review in Blender and refine "
                     "UVs/materials for production quality.")
        steps.append("Consider retargeting to a game-engine/VRM humanoid skeleton "
                     "for animation pipelines if needed.")
    else:
        if warnings:
            steps.append("Resolve reported warnings, then re-run the "
                         "process_mesh -> rig -> export stages.")
        steps.append("Install the recommended image-to-3D backend to get real "
                     "character geometry (see references/models.md), or provide "
                     "a mesh and re-run processing.")
    return steps


def write(project: dict, project_dir: str):
    rep = build_report(project)
    d = Path(project_dir)
    d.mkdir(parents=True, exist_ok=True)
    (d / "report.json").write_text(json.dumps(rep, indent=2, default=str),
                                   encoding="utf-8")
    (d / "report.md").write_text(markdown(rep), encoding="utf-8")
    return d / "report.md"


def markdown(rep: dict) -> str:
    L = []
    L.append("# image-to-3d-character report\n")
    L.append(f"- **Source image:** {rep['source_image']}")
    L.append(f"- **Project dir:** {rep['project_dir']}")
    L.append(f"- **Reconstruction method:** {rep['reconstruction_method']} "
             f"({rep['reconstruction_kind']})")
    L.append(f"- **Validation OK:** {rep['validation_ok']}")
    L.append(f"- **Polygons:** {rep['polygon_count']}")
    L.append(f"- **Objects:** {rep['number_of_objects']}")
    L.append(f"- **Texture res:** {rep['texture_resolution']}")
    L.append(f"- **Armature:** {rep['armature_status']}")
    L.append(f"- **Facial rig:** {rep['facial_rig_status']}")
    L.append(f"- **Export formats:** {', '.join(rep['export_formats'] or ['none'])}")
    L.append("\n## Generated files")
    for f in rep["generated_files"]:
        L.append(f"- `{f}`")
    if rep["warnings"]:
        L.append("\n## Warnings / errors")
        for w in rep["warnings"]:
            L.append(f"- {w}")
    else:
        L.append("\n## Warnings\nNone.")
    L.append("\n## Recommended next steps")
    for s in rep["recommended_next_steps"]:
        L.append(f"- {s}")
    return "\n".join(L) + "\n"
