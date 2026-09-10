"""PowerPoint-specific tools."""

from __future__ import annotations

from typing import Any

from office_mcp.adapters import pptx_adapter as pptx_ad
from office_mcp.security import check_size, ensure_writable, inspect_zip_bomb, safe_path
from office_mcp.tools._wrap import run


def register(mcp: Any) -> None:
    @mcp.tool()
    def pptx_extract(path: str) -> dict[str, Any]:
        """Extract slide texts, tables, notes, layouts, and a plain-text outline from a PPTX."""
        return run(_extract, path=path)

    @mcp.tool()
    def pptx_edit(path: str, ops: list[dict[str, Any]]) -> dict[str, Any]:
        """Apply slide operations in one call.

        op values: add_slide, set_title, set_body, add_textbox, add_picture, add_table, set_notes, delete_slide.
        Slide indexes are 1-based.
        """
        return run(_edit, path=path, ops=ops)


def _extract(path: str) -> dict[str, Any]:
    p = safe_path(path, must_exist=True)
    check_size(p)
    inspect_zip_bomb(p)
    return pptx_ad.extract(p)


def _edit(path: str, ops: list[dict[str, Any]]) -> dict[str, Any]:
    ensure_writable()
    p = safe_path(path, must_exist=True)
    inspect_zip_bomb(p)
    return pptx_ad.apply_ops(p, ops)
