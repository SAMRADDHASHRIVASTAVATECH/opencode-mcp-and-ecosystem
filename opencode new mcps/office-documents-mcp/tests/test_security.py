from pathlib import Path

import pytest

from office_mcp.config import Settings
from office_mcp.errors import SecurityError, ValidationError
from office_mcp.security import check_overwrite, safe_path


def test_sandbox_blocks_escape(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    settings = Settings(
        root=tmp_path.resolve(),
        read_only=False,
        max_bytes=10_000_000,
        max_cells=1000,
        max_batch=10,
        max_text=1000,
        allow_soffice=False,
        conversion_timeout=5,
    )
    monkeypatch.setattr("office_mcp.security.SETTINGS", settings)
    with pytest.raises(SecurityError):
        safe_path("../etc/passwd", settings=settings)


def test_overwrite_guard(tmp_path: Path) -> None:
    p = tmp_path / "a.docx"
    p.write_text("x")
    with pytest.raises(ValidationError):
        check_overwrite(p, overwrite=False)
    check_overwrite(p, overwrite=True)
