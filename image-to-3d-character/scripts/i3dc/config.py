"""Skill configuration: paths, options and preferences.

Kept out of the library so the OpenCode agent can override per-invocation.
Loaded from a JSON/YAML config file or defaulted. This module never guesses a
hard-coded tool path; paths come from tool detection.
"""
from __future__ import annotations

import json
import os
from dataclasses import dataclass, field, asdict
from pathlib import Path


@dataclass
class Config:
    # project / working areas
    state_root: str = ""                 # where projects + caches live ('' => auto)
    project_subdir: str = "projects"     # each run gets <project_subdir>/<name>/

    # behaviour defaults (overridable on the command line)
    output_format: str = "glb"           # glb | gltf | fbx | obj
    quality: str = "balanced"            # draft | balanced | high
    rig: bool = True
    facial_rig: bool = True
    low_poly: bool = False
    anime: bool = True
    device: str = "auto"                 # auto | gpu | cpu
    poly_target: int = 0                 # 0 => pick automatically
    texture_resolution: int = 2048

    # reconstruction backend preference order (see references/models.md)
    recon_preferences: list = field(
        default_factory=lambda: ["local", "blender", "lightweight", "external"])

    # external service use is always opt-in (never silent uploads)
    allow_external_service: bool = False
    external_service: str = ""           # e.g. TripoSR HF-space via API endpoint name
    external_api_key: str = ""           # read from env in practice, never store

    # paths to inject if auto-detection fails (all optional)
    override_blender: str = ""
    override_python: str = ""
    override_stable_diffusion_dir: str = ""
    override_comfyui_dir: str = ""
    override_inkscape: str = ""
    override_ffmpeg: str = ""

    config_file: str = ""

    def resolved_state_root(self) -> Path:
        if self.state_root:
            return Path(self.state_root).expanduser()
        # default under a user-appropriate location
        home = Path.home()
        base = os.environ.get("LOCALAPPDATA") or os.environ.get("XDG_DATA_HOME") \
            or str(home / ".local" / "share")
        return Path(base) / "image-to-3d-character"

    def project_dir(self, name: str) -> Path:
        return self.resolved_state_root() / self.project_subdir / _safe(name)

    def to_dict(self) -> dict:
        return asdict(self)


def _safe(name: str) -> str:
    keep = "".join(ch if ch.isalnum() or ch in "-_." else "_" for ch in name)
    return keep.strip(" .") or "character"


def _find_config_file() -> str:
    here = Path(__file__).resolve().parent.parent.parent
    candidates = [
        here / "config.json",
        here / "config.yaml",
        Path.home() / ".config" / "image-to-3d-character" / "config.json",
    ]
    for c in candidates:
        if c.exists():
            return str(c)
    return ""


def load_config(explicit: str = "") -> Config:
    cfg = Config()
    path = explicit or _find_config_file()
    if path and Path(path).exists():
        raw = {}
        try:
            if path.endswith(".yaml") or path.endswith(".yml"):
                import yaml
                raw = yaml.safe_load(Path(path).read_text(encoding="utf-8")) or {}
            else:
                raw = json.loads(Path(path).read_text(encoding="utf-8"))
        except Exception:   # noqa: BLE001
            raw = {}
        # apply only known fields
        for k, v in (raw or {}).items():
            if hasattr(cfg, k) and not isinstance(getattr(cfg, k), dict):
                setattr(cfg, k, v)
    cfg.config_file = path or ""
    return cfg
