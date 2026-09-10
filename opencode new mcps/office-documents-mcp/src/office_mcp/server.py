"""MCP server entrypoint for Office documents."""

from __future__ import annotations

from office_mcp.mcp_compat import create_mcp
from office_mcp.tools import register_all

INSTRUCTIONS = """\
Office Documents MCP — local DOCX/XLSX/PPTX specialist.

Does not require Microsoft Office. File I/O is sandboxed to OFFICE_MCP_ROOT (cwd by default).
Macros are detected, never executed. PDF export and formula recalc need LibreOffice if present.
Prefer office_inspect first on unknown files. Use batch ops lists (word_edit, excel_write, pptx_edit)
instead of many tiny calls.
"""

mcp = create_mcp("office-documents", INSTRUCTIONS)
register_all(mcp)


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
