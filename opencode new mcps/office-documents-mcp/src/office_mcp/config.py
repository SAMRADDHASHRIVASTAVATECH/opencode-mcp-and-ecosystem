"""Configuration from environment."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


def _bool(name: str, default: bool = False) -> bool:
    raw = os.environ.get(name)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}


def _int(name: str, default: int) -> int:
    raw = os.environ.get(name)
    if not raw:
        return default
    try:
        return int(raw)
    except ValueError:
        return default


@dataclass(frozen=True)
class Settings:
    root: Path
    read_only: bool
    max_bytes: int
    max_cells: int
    max_batch: int
    max_text: int
    allow_soffice: bool
    conversion_timeout: int

    @classmethod
    def load(cls) -> "Settings":
        root = Path(os.environ.get("OFFICE_MCP_ROOT") or os.getcwd()).resolve()
        return cls(
            root=root,
            read_only=_bool("OFFICE_MCP_READ_ONLY", False),
            max_bytes=_int("OFFICE_MCP_MAX_BYTES", 50 * 1024 * 1024),
            max_cells=_int("OFFICE_MCP_MAX_CELLS", 200_000),
            max_batch=_int("OFFICE_MCP_MAX_BATCH", 50),
            max_text=_int("OFFICE_MCP_MAX_TEXT", 200_000),
            allow_soffice=_bool("OFFICE_MCP_ALLOW_SOFFICE", True),
            conversion_timeout=_int("OFFICE_MCP_CONVERT_TIMEOUT", 60),
        )


SETTINGS = Settings.load()
