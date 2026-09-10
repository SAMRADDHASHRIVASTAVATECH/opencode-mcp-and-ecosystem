"""Configuration and resource/profile defaults.

Resource-aware execution (requirement 33) reads these defaults and the
machine's real capacities to choose efficient strategies automatically.
"""
from __future__ import annotations

import json
import os
import platform
from dataclasses import dataclass, field, asdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent  # repository root


def _env(key: str, default):
    val = os.environ.get("UPPDF_" + key)
    if val is None:
        return default
    if isinstance(default, bool):
        return val.lower() in {"1", "true", "yes", "on"}
    if isinstance(default, int):
        return int(val)
    if isinstance(default, float):
        return float(val)
    return val


@dataclass
class RuntimeProfile:
    """Describes what this environment can actually do."""
    # LLM / model context
    llm_context_chars: int = _env("LLM_CONTEXT_CHARS", 16_000)
    llm_context_tokens: int = _env("LLM_CONTEXT_TOKENS", 4_000)
    # capabilities
    vision_available: bool = _env("VISION", False)
    ocr_available: bool = _env("OCR", False)
    # resources
    ram_mb: int = 0            # resolved at runtime if 0
    cpu_cores: int = 0
    gpu_available: bool = False
    # processing knobs
    page_batch_size: int = _env("PAGE_BATCH", 20)
    chunk_chars: int = _env("CHUNK_CHARS", 1500)
    chunk_overlap_chars: int = _env("CHUNK_OVERLAP", 150)

    def to_dict(self) -> dict:
        return asdict(self)


def default_profile() -> RuntimeProfile:
    p = RuntimeProfile()
    # Detect host resources (pure-stdlib best effort).
    try:
        import os
        # RAM
        if os.path.exists("/proc/meminfo"):
            with open("/proc/meminfo") as fh:
                for line in fh:
                    if line.startswith("MemTotal"):
                        p.ram_mb = int(line.split()[1]) // 1024
                        break
        p.cpu_cores = os.cpu_count() or 1
    except Exception:
        p.cpu_cores = os.cpu_count() or 1
    return p


@dataclass
class OptimizeProfile:
    """Presets for pdf-compress / pdf-optimize (requirement 17)."""
    name: str
    image_dpi: int
    image_quality: int      # jpeg quality 1-100
    use_garbage: int
    deflate: bool

    def to_dict(self) -> dict:
        return asdict(self)


OPTIMIZE_PROFILES: dict[str, OptimizeProfile] = {
    # image_dpi, jpeg quality, pymupdf garbage level, clean/deflate
    "maximum_quality": OptimizeProfile("maximum_quality", 0, 95, 1, False),
    "balanced":        OptimizeProfile("balanced", 0, 75, 3, True),
    "small_size":      OptimizeProfile("small_size", 120, 55, 4, True),
    "web_optimized":   OptimizeProfile("web_optimized", 110, 60, 3, True),
    "archive_optimized": OptimizeProfile("archive_optimized", 0, 85, 3, True),
}

# --- config file ---
_CONFIG_PATH = ROOT / "registry" / "config.json"


def load_config_file() -> dict:
    """Read registry/config.json if present (agent can override)."""
    if _CONFIG_PATH.exists():
        try:
            return json.loads(_CONFIG_PATH.read_text())
        except Exception:
            return {}
    return {}
