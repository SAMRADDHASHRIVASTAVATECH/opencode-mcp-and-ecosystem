"""Path sandbox, size limits, zip-bomb guards."""

from __future__ import annotations

import zipfile
from pathlib import Path

from office_mcp.config import SETTINGS, Settings
from office_mcp.errors import (
    MalformedError,
    NotFoundError,
    PermissionDenied,
    SecurityError,
    ValidationError,
)

MAX_ZIP_RATIO = 100
MAX_ZIP_FILES = 5000


def safe_path(
    path: str | Path,
    *,
    must_exist: bool = False,
    settings: Settings | None = None,
) -> Path:
    settings = settings or SETTINGS
    if not path:
        raise ValidationError("Path is required")
    raw = Path(path).expanduser()
    candidate = (raw if raw.is_absolute() else settings.root / raw).resolve()
    try:
        candidate.relative_to(settings.root)
    except ValueError as exc:
        raise SecurityError(
            "Path is outside OFFICE_MCP_ROOT sandbox",
            {"path": str(path), "root": str(settings.root)},
        ) from exc
    if must_exist and not candidate.exists():
        raise NotFoundError(f"File not found: {candidate}")
    return candidate


def ensure_writable(settings: Settings | None = None) -> None:
    settings = settings or SETTINGS
    if settings.read_only:
        raise PermissionDenied("Server is in read-only mode (OFFICE_MCP_READ_ONLY)")


def check_overwrite(path: Path, overwrite: bool) -> None:
    if path.exists() and not overwrite:
        raise ValidationError(
            "File exists; pass overwrite=true to replace it",
            {"path": str(path)},
        )


def check_size(path: Path, settings: Settings | None = None) -> None:
    settings = settings or SETTINGS
    if path.exists() and path.is_file() and path.stat().st_size > settings.max_bytes:
        raise ValidationError(
            f"File exceeds max size of {settings.max_bytes} bytes",
            {"path": str(path), "size": path.stat().st_size},
        )


def inspect_zip_bomb(path: Path, settings: Settings | None = None) -> None:
    settings = settings or SETTINGS
    if not zipfile.is_zipfile(path):
        return
    try:
        with zipfile.ZipFile(path) as zf:
            infos = zf.infolist()
            if len(infos) > MAX_ZIP_FILES:
                raise SecurityError("OOXML package has too many parts", {"count": len(infos)})
            total = 0
            compressed = max(path.stat().st_size, 1)
            for info in infos:
                if info.file_size < 0:
                    raise SecurityError("Negative ZIP size")
                total += info.file_size
                if total > settings.max_bytes * 4:
                    raise SecurityError(
                        "Uncompressed package exceeds safety limit",
                        {"uncompressed": total},
                    )
            if total / compressed > MAX_ZIP_RATIO and total > 10 * 1024 * 1024:
                raise SecurityError(
                    "ZIP compression ratio looks like a zip bomb",
                    {"ratio": round(total / compressed, 2)},
                )
    except zipfile.BadZipFile as exc:
        raise MalformedError("File is not a valid ZIP/OOXML package") from exc
