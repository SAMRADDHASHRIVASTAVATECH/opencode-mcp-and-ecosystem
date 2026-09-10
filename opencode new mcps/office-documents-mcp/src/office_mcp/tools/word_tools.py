"""Word-specific tools."""

from __future__ import annotations

from typing import Any

from office_mcp.adapters import word as word_ad
from office_mcp.security import check_size, ensure_writable, inspect_zip_bomb, safe_path
from office_mcp.tools._wrap import run


def register(mcp: Any) -> None:
    @mcp.tool()
    def word_extract(
        path: str,
        include_tables: bool = True,
        include_headers: bool = True,
    ) -> dict[str, Any]:
        """Extract paragraphs, tables, headers/footers, comments, images, and plain text from a DOCX."""
        return run(_extract, path=path, include_tables=include_tables, include_headers=include_headers)

    @mcp.tool()
    def word_edit(path: str, ops: list[dict[str, Any]]) -> dict[str, Any]:
        """Apply a list of Word edits in one call.

        Each op is an object with 'op' set to one of:
        add_heading, add_paragraph, add_list, add_table, add_page_break, add_picture, add_comment.

        Examples:
          {"op":"add_heading","text":"Intro","level":1}
          {"op":"add_paragraph","text":"Hello","bold":false}
          {"op":"add_list","items":["a","b"],"ordered":false}
          {"op":"add_table","rows":[["A","B"],["1","2"]]}
        """
        return run(_edit, path=path, ops=ops)

    @mcp.tool()
    def word_find_replace(
        path: str,
        find: str,
        replace: str,
        regex: bool = False,
        count: int = 0,
    ) -> dict[str, Any]:
        """Find and replace text in paragraphs and tables. count=0 means unlimited (capped internally)."""
        return run(_fr, path=path, find=find, replace=replace, regex=regex, count=count)

    @mcp.tool()
    def word_layout(
        path: str,
        header: str | None = None,
        footer: str | None = None,
        orientation: str | None = None,
        page_width_in: float | None = None,
        page_height_in: float | None = None,
        margins_in: dict[str, float] | None = None,
        section: int = 0,
    ) -> dict[str, Any]:
        """Set headers, footers, page size, orientation, and margins for a section."""
        return run(
            _layout,
            path=path,
            spec={
                "header": header,
                "footer": footer,
                "orientation": orientation,
                "page_width_in": page_width_in,
                "page_height_in": page_height_in,
                "margins_in": margins_in,
                "section": section,
            },
        )


def _extract(path: str, include_tables: bool, include_headers: bool) -> dict[str, Any]:
    p = safe_path(path, must_exist=True)
    check_size(p)
    inspect_zip_bomb(p)
    return word_ad.extract(p, include_tables=include_tables, include_headers=include_headers)


def _edit(path: str, ops: list[dict[str, Any]]) -> dict[str, Any]:
    ensure_writable()
    p = safe_path(path, must_exist=True)
    inspect_zip_bomb(p)
    return word_ad.apply_ops(p, ops)


def _fr(path: str, find: str, replace: str, regex: bool, count: int) -> dict[str, Any]:
    ensure_writable()
    p = safe_path(path, must_exist=True)
    return word_ad.find_replace(p, find, replace, regex=regex, count=count)


def _layout(path: str, spec: dict[str, Any]) -> dict[str, Any]:
    ensure_writable()
    p = safe_path(path, must_exist=True)
    cleaned = {k: v for k, v in spec.items() if v is not None}
    return word_ad.layout(p, cleaned)
