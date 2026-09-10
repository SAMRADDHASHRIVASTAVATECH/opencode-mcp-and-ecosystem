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
    default_url: str | None
    allow_write: bool
    allow_ddl: bool
    allow_destructive: bool
    allow_multi: bool
    allow_any_path: bool
    max_rows: int
    default_limit: int
    max_cell_chars: int
    query_timeout: int

    @classmethod
    def load(cls) -> "Settings":
        return cls(
            root=Path(os.environ.get("DB_MCP_ROOT") or os.getcwd()).resolve(),
            default_url=os.environ.get("DB_MCP_URL") or None,
            allow_write=_bool("DB_MCP_ALLOW_WRITE", False),
            allow_ddl=_bool("DB_MCP_ALLOW_DDL", False),
            allow_destructive=_bool("DB_MCP_ALLOW_DESTRUCTIVE", False),
            allow_multi=_bool("DB_MCP_ALLOW_MULTI", False),
            allow_any_path=_bool("DB_MCP_ALLOW_ANY_PATH", False),
            max_rows=_int("DB_MCP_MAX_ROWS", 5000),
            default_limit=_int("DB_MCP_DEFAULT_LIMIT", 200),
            max_cell_chars=_int("DB_MCP_MAX_CELL_CHARS", 500),
            query_timeout=_int("DB_MCP_TIMEOUT", 30),
        )


SETTINGS = Settings.load()
