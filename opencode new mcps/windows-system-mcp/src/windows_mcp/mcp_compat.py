from __future__ import annotations

from typing import Any


def create_mcp(name: str, instructions: str = "") -> Any:
    try:
        from mcp.server import MCPServer  # type: ignore

        try:
            return MCPServer(name, instructions=instructions)
        except TypeError:
            return MCPServer(name)
    except Exception:
        pass
    try:
        from mcp.server.fastmcp import FastMCP  # type: ignore

        try:
            return FastMCP(name, instructions=instructions)
        except TypeError:
            return FastMCP(name)
    except Exception as exc:  # pragma: no cover
        raise ImportError("Install mcp: pip install 'mcp>=1.2'") from exc
