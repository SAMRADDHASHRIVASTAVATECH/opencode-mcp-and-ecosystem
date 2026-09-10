"""Tool discovery.

Determines which relevant tools are actually installed on the current machine by
checking (in order):
  1. PATH (shutil.which)
  2. common Windows install locations
  3. user-provided overrides
Never assumes a path exists. Everything returned is verified (file present) or
clearly marked as not found.
"""
from __future__ import annotations

import os
import shutil
import sys
import importlib.util
from dataclasses import dataclass, field, asdict
from pathlib import Path

from .config import Config

WINDOWS_COMMON = [
    r"C:\Program Files\Blender Foundation",
    r"C:\Program Files\Inkscape",
    r"C:\Program Files\ffmpeg",
    r"%LOCALAPPDATA%\Programs\Blender Foundation",
    r"%LOCALAPPDATA%\Programs\Python",
]
_WIN_EXE = {".exe", ".bat", ".cmd", ".ps1"}


@dataclass
class Tool:
    name: str
    present: bool = False
    version: str | None = None
    path: str | None = None
    kind: str = "cli"                 # cli | module | model | app
    note: str = ""

    def to_dict(self) -> dict:
        return asdict(self)


def _expand(p: str) -> Path:
    return Path(os.path.expandvars(os.path.expanduser(p)))


def _find_win(name: str) -> str | None:
    """Search common Windows locations recursively (bounded)."""
    # Windows already found via which() for exe's; here we help GUI apps.
    roots = []
    for pat in WINDOWS_COMMON:
        roots.append(_expand(pat))
    targets = name.lower()
    for root in roots:
        if not root.exists():
            continue
        try:
            if root.is_dir():
                for f in root.rglob(name):
                    try:
                        if f.is_file() and f.suffix.lower() in _WIN_EXE:
                            return str(f)
                    except OSError:   # noqa: BLE001
                        continue
        except (PermissionError, OSError):   # noqa: BLE001
            continue
    return None


def _blender_search() -> str | None:
    if os.name == "nt":
        # typical: ...\Blender Foundation\Blender <ver>\blender.exe
        roots = [_expand(p) for p in WINDOWS_COMMON]
        for root in roots:
            if not root.exists():
                continue
            if root.name.lower().startswith("blender"):
                exe = root / ("blender.exe" if os.name == "nt" else "blender")
                if exe.exists():
                    return str(exe)
            try:
                for d in root.glob("Blender*"):
                    exe = d / ("blender.exe" if os.name == "nt" else "blender")
                    if exe.exists():
                        return str(exe)
            except OSError:   # noqa: BLE001
                continue
    return None


def _run_ver(cmd: list[str], timeout: float = 20) -> str | None:
    try:
        import subprocess
        out = subprocess.run(cmd, capture_output=True, text=True,
                             timeout=timeout)
        return (out.stdout or out.stderr or "").strip().splitlines()[0] \
            if out.returncode == 0 else None
    except Exception:   # noqa: BLE001
        return None


def detect_blender() -> Tool:
    t = Tool("blender", kind="app")
    p = shutil.which("blender") or _blender_search()
    if not p:
        return t
    t.present = True
    t.path = p
    ver = _run_ver([p, "--version"]) if not os.name == "nt" else \
        _run_ver([p, "--version"])
    t.version = (ver or "").split("\n")[0] if ver else None
    return t


def detect_app(name: str, exe: str | None = None) -> Tool:
    t = Tool(name, kind="app")
    exe = exe or name
    p = shutil.which(exe)
    if p:
        t.present, t.path = True, p
    return t


def detect_python() -> Tool:
    t = Tool("python", kind="cli")
    p = shutil.which("python") or shutil.which("python3")
    if not p and os.name == "nt":
        p = _find_win("python.exe")
    t.present = bool(p)
    t.path = p
    t.version = sys.version.split()[0]
    return t


def _module(name: str) -> bool:
    return importlib.util.find_spec(name) is not None


def detect_python_modules() -> dict[str, Tool]:
    out = {}
    for mod, kind, note in [
        ("PIL", "module", "image reading / processing"),
        ("numpy", "module", "numeric image processing"),
        ("opencv", "module", "background removal / silhouettes"),
        ("rembg", "module", "AI background removal (ONNX)"),
        ("onnxruntime", "module", "runtime for rembg / quantized nets"),
        ("torch", "module", "inference for image-to-3D / SD"),
        ("trimesh", "module", "mesh processing / validation (pure python)"),
        ("bpy", "module", "Blender's python module (only inside Blender)"),
    ]:
        ok = _module(mod)
        out[mod] = Tool(mod, present=ok, kind=kind, note=note)
    return out


def detect_comfyui(cfg: Config) -> Tool:
    t = Tool("comfyui", kind="app")
    # check env / override / common locations
    cands = [cfg.override_comfyui_dir]
    env = os.environ.get("COMFYUI_DIR") or os.environ.get("COMFYUI_ROOT")
    if env:
        cands.append(env)
    cands += [str(Path.home() / "ComfyUI"),
              r"C:\ComfyUI", r"%LOCALAPPDATA%\ComfyUI"]
    for c in cands:
        c = os.path.expandvars(os.path.expanduser(c))
        d = Path(c)
        if (d / "main.py").exists():
            t.present = True
            t.path = str(d)
            break
    return t


def detect_stable_diffusion(cfg: Config) -> Tool:
    t = Tool("stable_diffusion", kind="model")
    comfy = detect_comfyui(cfg)
    if comfy.present:
        # look for checkpoint files inside comfy models/checkpoints
        ck = Path(comfy.path) / "models" / "checkpoints"
        if ck.exists():
            t.present = True
            t.path = str(ck)
            t.note = "via ComfyUI checkpoints dir"
    return t


def detect_inkscape() -> Tool:
    t = Tool("inkscape", kind="app")
    p = shutil.which("inkscape") or shutil.which("inkscape.exe")
    if not p and os.name == "nt":
        p = _find_win("inkscape.exe")
    t.present = bool(p)
    t.path = p
    return t


def detect_ffmpeg() -> Tool:
    t = Tool("ffmpeg", kind="cli")
    p = shutil.which("ffmpeg")
    t.present = bool(p)
    t.path = p
    return t


def detect_mesh_utils() -> dict[str, Tool]:
    out = {}
    for nm, exe in [("obj2gltf", "obj2gltf"), ("gltfpack", "gltfpack"),
                    ("meshoptimizer", "meshoptimizer")]:
        p = shutil.which(exe)
        out[nm] = Tool(nm, present=bool(p), path=p, kind="cli")
    return out


def detect_image_to_3d_local(cfg: Config) -> dict[str, Tool]:
    """Look for known local image-to-3D model dirs / checkpoints."""
    out = {}
    known = {
        # name -> list of expected marker files relative to a root dir
        "TripoSR": ["pytorch_model.bin", "config.json", "*.safetensors"],
        "Zero123plus": ["*.safetensors", "config.json"],
        "Trellis": ["*.safetensors", "config.json"],
        "StableFast3D": ["*.safetensors", "config.json"],
    }
    # search a few roots
    roots = [cfg.resolved_state_root() / "models",
             Path.home() / "models", Path.home() / ".cache" / "image-to-3d"]
    if os.name == "nt":
        roots += [Path(r"C:\models"), Path(os.environ.get("USERPROFILE", "")) / "models"]
    for name, markers in known.items():
        found = None
        for root in roots:
            if not root.exists():
                continue
            try:
                for sub in root.rglob("*"):
                    if not sub.is_dir():
                        continue
                    low = sub.name.lower()
                    if name.lower().replace("+", "plus") in low.replace("+", "plus"):
                        # confirm a marker
                        for mk in markers:
                            if list(sub.glob(mk)):
                                found = sub
                                break
                    if found:
                        break
            except (PermissionError, OSError):   # noqa: BLE001
                continue
            if found:
                break
        out[name] = Tool(name, present=bool(found), path=str(found) if found else None,
                         kind="model")
    return out


def detect_all(cfg: Config | None = None) -> dict:
    cfg = cfg or Config()
    det = {
        "python": detect_python(),
        "blender": detect_blender(),
        "inkscape": detect_inkscape(),
        "ffmpeg": detect_ffmpeg(),
        "comfyui": detect_comfyui(cfg),
        "stable_diffusion": detect_stable_diffusion(cfg),
        "python_modules": detect_python_modules(),
        "mesh_utils": detect_mesh_utils(),
        "image_to_3d_local": detect_image_to_3d_local(cfg),
        "os": os.name,
        "platform": __import__("platform").platform(),
        "python_version": sys.version.split()[0],
    }
    return det


def summary(det: dict) -> dict:
    """Human + machine readable capability summary with install guidance."""
    rows = []
    app_items = [
        ("python", "python"),
        ("blender", "Blender"),
        ("inkscape", "Inkscape"),
        ("ffmpeg", "FFmpeg"),
        ("comfyui", "ComfyUI"),
        ("stable_diffusion", "Stable Diffusion checkpoints"),
    ]
    for key, label in app_items:
        t = det.get(key)
        if isinstance(t, Tool):
            rows.append(_row(label, t.present, t.path))
    return {"apps": rows, "modules": det["python_modules"],
            "image_to_3d_local": det["image_to_3d_local"]}


def _row(label, present, path):
    return {"tool": label, "present": bool(present),
            "status": "found" if present else "missing",
            "path": path or None}
