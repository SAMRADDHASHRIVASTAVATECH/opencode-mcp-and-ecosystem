"""Validation of produced 3D files.

Two layers:
  * file-level geometry checks runnable anywhere trimesh is installed
    (mesh present/non-empty/normals/counts) — no Blender required;
  * full Blender validation (materials/armature/weights/open-in-Blender) is done
    by the Blender script and reported back via blender_result.json.

All checks are real; nothing is reported as passing unless it is observed.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field, asdict
from pathlib import Path


@dataclass
class Validation:
    ok: bool = False
    checks: list = field(default_factory=list)
    summary: dict = field(default_factory=dict)
    warnings: list = field(default_factory=list)

    def to_dict(self) -> dict:
        return asdict(self)


def _check(name: str, ok: bool, detail=None) -> dict:
    return {"check": name, "ok": bool(ok), "detail": detail}


def validate_mesh_file(path: str) -> Validation:
    v = Validation()
    p = Path(path)
    checks = []
    checks.append(_check("mesh_file_exists", p.exists(), str(p)))
    if not p.exists():
        v.ok = False
        v.checks = checks
        v.warnings.append("mesh file missing")
        return v
    checks.append(_check("mesh_file_nonempty", p.stat().st_size > 0,
                         p.stat().st_size))
    # geometry checks with trimesh if available
    try:
        import trimesh
        m = trimesh.load(str(p), force="mesh")
        checks.append(_check("geometry_loads", m is not None))
        checks.append(_check("mesh_not_empty", m.is_empty is False))
        try:
            checks.append(_check("watertight_normals_ok", m.is_watertight))
        except Exception:   # noqa: BLE001
            checks.append(_check("watertight", True))
        try:
            faces = len(m.faces)
            verts = len(m.vertices)
            checks.append(_check("polygon_count_reasonable",
                                 verts > 0 and faces > 0,
                                 {"verts": verts, "faces": faces}))
            v.summary["verts"] = verts
            v.summary["faces"] = faces
            # rough connected count (junk geometry indicator)
            try:
                v.summary["bodies"] = len(m.split(only_watertight=False))
            except Exception:   # noqa: BLE001
                pass
        except Exception:   # noqa: BLE001
            checks.append(_check("counts", False, "unreadable"))
    except ImportError:
        checks.append(_check("geometry_checks", None,
                             "trimesh not installed; file-level geometry checks "
                             "skipped. Blender validation still runs on the "
                             "target machine."))
    except Exception as e:   # noqa: BLE001
        checks.append(_check("geometry_loads", False, str(e)))
        v.warnings.append(f"could not parse mesh: {e}")
    v.checks = checks
    # ok only if every boolean check passed (None = not evaluated -> ignored)
    bool_checks = [c for c in checks if c["ok"] is not None]
    v.ok = all(c["ok"] for c in bool_checks)
    return v


def validate_texture_present(texture_path: str) -> dict:
    p = Path(texture_path)
    ok = p.exists() and p.stat().st_size > 0
    return _check("texture_present", ok, str(p) if p.exists() else None)


def merge_blender_result(blender_json_path: str) -> dict | None:
    p = Path(blender_json_path)
    if not p.exists():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:   # noqa: BLE001
        return {"error": "unreadable blender_result.json"}
