"""MCP tool registration."""

from __future__ import annotations

from typing import Any


def register_all(mcp: Any) -> None:
    from office_mcp.tools import excel_tools, office_tools, pptx_tools, word_tools

    office_tools.register(mcp)
    word_tools.register(mcp)
    excel_tools.register(mcp)
    pptx_tools.register(mcp)
