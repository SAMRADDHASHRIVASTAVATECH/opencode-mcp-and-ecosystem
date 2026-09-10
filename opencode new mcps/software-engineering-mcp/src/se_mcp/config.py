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
    timeout: int
    ecosystem_root: Path

    @classmethod
    def load(cls) -> "Settings":
        eco = Path(os.environ.get("SE_MCP_ECOSYSTEM") or Path(__file__).resolve().parents[3])
        # src/se_mcp/config.py → parents[3] may be workspace if installed editable from software-engineering-mcp
        # Prefer explicit env; else cwd; else parent of this package's repo.
        guessed = Path(os.environ.get("SE_MCP_ECOSYSTEM") or os.getcwd()).resolve()
        return cls(
            root=Path(os.environ.get("SE_MCP_ROOT") or os.getcwd()).resolve(),
            read_only=_bool("SE_MCP_READ_ONLY", False),
            timeout=_int("SE_MCP_TIMEOUT", 120),
            ecosystem_root=guessed,
        )


SETTINGS = Settings.load()
