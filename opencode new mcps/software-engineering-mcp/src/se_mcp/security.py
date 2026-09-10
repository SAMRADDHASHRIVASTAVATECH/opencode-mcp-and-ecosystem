from __future__ import annotations

from pathlib import Path

from se_mcp.config import SETTINGS, Settings
from se_mcp.errors import NotFoundError, PolicyError, ValidationError


def safe_path(path: str | Path, *, must_exist: bool = False, settings: Settings | None = None) -> Path:
    settings = settings or SETTINGS
    if not path:
        raise ValidationError("Path is required")
    raw = Path(str(path)).expanduser()
    candidate = (raw if raw.is_absolute() else settings.root / raw).resolve()
    try:
        candidate.relative_to(settings.root)
    except ValueError as exc:
        raise PolicyError("Path is outside SE_MCP_ROOT sandbox", {"path": str(path), "root": str(settings.root)}) from exc
    if must_exist and not candidate.exists():
        raise NotFoundError(f"Not found: {candidate}")
    return candidate


def ensure_writable(settings: Settings | None = None) -> None:
    if (settings or SETTINGS).read_only:
        raise PolicyError("Server is read-only (SE_MCP_READ_ONLY)")


def require_confirm(confirm: bool, action: str) -> None:
    if not confirm:
        raise PolicyError(f"{action} requires confirm=true")
