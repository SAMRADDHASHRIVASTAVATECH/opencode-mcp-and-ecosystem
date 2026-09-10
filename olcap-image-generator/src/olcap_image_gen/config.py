"""Persistent configuration.

Never hard-codes a user home path. The state/config root is discovered via:
1. env OLCAP_IMAGE_STATE_DIR
2. a local ./state under the project
3. platform user-dir fallback
All directories (models/outputs/cache/logs) derive from that root unless the
user overrides them. Merges a YAML config file over defaults. Environment
variables OLCAP_IMAGE_* override YAML, coerced to the declared field type.
"""
from __future__ import annotations

import os
import platform
from dataclasses import dataclass, field
from pathlib import Path

ENV_PREFIX = "OLCAP_IMAGE_"


def _default_root() -> Path:
    env = os.environ.get(ENV_PREFIX + "STATE_DIR")
    if env:
        return Path(env).expanduser()
    if platform.system() == "Windows":
        base = Path(os.environ.get("USERPROFILE", str(Path.home())))
        return base / "olcap" / "image-generator"
    return Path.home() / ".olcap" / "image-generator"


@dataclass
class Settings:
    # identity
    project_name: str = "OLCAP Image Generator"
    project_version: str = "1.0.0"

    # quality / generation defaults
    default_quality: str = "maximum"
    default_width: int = 1024
    default_height: int = 1024
    default_format: str = "png"
    default_steps: int = 30

    # hardware defaults are "auto"; profiler computes real values
    gpu_offload: str = "auto"
    cpu_offload: bool = True
    ram_limit_gb: str = "auto"
    vram_reserve_mb: str = "auto"

    # runtime
    backend: str = "auto"
    auto_start: bool = False
    comfyui_port: int = 8188
    comfyui_host: str = "127.0.0.1"

    # models
    preferred_family: str = "auto"
    preferred_quantization: str = "highest_compatible"
    auto_install_models: bool = False
    model_download_roots: list = field(default_factory=list)

    # paths (state_dir derived; subdirs overridable)
    state_dir: str = ""
    models_dir: str = ""
    outputs_dir: str = ""
    cache_dir: str = ""
    workflows_dir: str = ""
    logs_dir: str = ""
    config_file: str = ""

    def resolved_root(self) -> Path:
        return Path(self.state_dir or _default_root()).expanduser()

    def resolved_models_dir(self) -> Path:
        return Path(self.models_dir or (self.resolved_root() / "models")).expanduser()

    def resolved_outputs_dir(self) -> Path:
        return Path(self.outputs_dir or (self.resolved_root() / "outputs")).expanduser()

    def resolved_cache_dir(self) -> Path:
        return Path(self.cache_dir or (self.resolved_root() / "cache")).expanduser()

    def resolved_logs_dir(self) -> Path:
        return Path(self.logs_dir or (self.resolved_root() / "logs")).expanduser()

    def resolved_workflows_dir(self) -> Path:
        return Path(self.workflows_dir or (self.resolved_root() / "workflows")).expanduser()

    def ensure_dirs(self) -> None:
        for d in (self.resolved_root(), self.resolved_models_dir(),
                  self.resolved_outputs_dir(), self.resolved_cache_dir(),
                  self.resolved_logs_dir(), self.resolved_workflows_dir()):
            d.mkdir(parents=True, exist_ok=True)

    def registry_path(self) -> Path:
        return self.resolved_root() / "model-registry.json"

    def selection_cache_path(self) -> Path:
        return self.resolved_root() / "selection-benchmarks.json"

    def to_dict(self) -> dict:
        import dataclasses
        return dataclasses.asdict(self)


def load_settings(state_dir: str = "") -> Settings:
    """Load settings: env overrides + optional YAML config file."""
    base = Settings()
    root = Path(state_dir or _default_root()).expanduser()
    cfg_candidates = [
        root / "config.yaml",
        Path(__file__).resolve().parent.parent.parent / "configs" / "config.example.yaml",
    ]
    yaml_cfg: dict = {}
    cfg_path = ""
    import yaml
    for c in cfg_candidates:
        if c.exists():
            try:
                yaml_cfg = yaml.safe_load(c.read_text(encoding="utf-8")) or {}
                cfg_path = str(c)
                break
            except Exception:   # noqa: BLE001
                yaml_cfg = {}
    fields = {f.name: f.type for f in Settings.__dataclass_fields__.values()}
    merged = base.to_dict()
    _apply_yaml(merged, yaml_cfg)
    for k in list(merged):
        envname = ENV_PREFIX + k.upper()
        v = os.environ.get(envname)
        if v is not None and v != "":
            merged[k] = _coerce(v, fields.get(k))
    merged["state_dir"] = str(root)
    merged["config_file"] = cfg_path
    merged = {k: v for k, v in merged.items() if k in fields}
    s = Settings(**merged)
    s.ensure_dirs()
    return s


def _coerce(value, typ):
    if value is None:
        return value
    tname = typ if isinstance(typ, str) else getattr(typ, "__name__", "")
    if tname == "bool":
        return str(value).strip().lower() in ("1", "true", "yes", "on")
    if tname == "int":
        try:
            return int(value)
        except Exception:   # noqa: BLE001
            return value
    if tname == "float":
        try:
            return float(value)
        except Exception:   # noqa: BLE001
            return value
    return value


def _apply_yaml(flat: dict, cfg: dict) -> None:
    leaves = []

    def walk(prefix: str, node):
        for k, v in node.items():
            key = f"{prefix}{k}".strip(".")
            if isinstance(v, dict):
                walk(key + ".", v)
            else:
                leaves.append((key, k, v))
    walk("", cfg)
    for full, tail, v in leaves:
        if full in flat:
            flat[full] = v
        elif tail in flat:
            flat[tail] = v
