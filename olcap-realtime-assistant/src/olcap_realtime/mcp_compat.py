"""Compatibility shim: mcp.server.mcpserver.MCPServer was removed in modern mcp.

This project targets the older mcp API (MCPServer with a ``tool()`` decorator and
``run_stdio_async()``). Modern mcp (>= 1.0 era) provides FastMCP with the same
surface, so MCPServer is re-exposed here as a thin FastMCP subclass.
"""
from __future__ import annotations

from mcp.server.fastmcp import FastMCP


class MCPServer(FastMCP):
    def __init__(self, name: str = "", instructions: str | None = None,
                 version: str | None = None, **kwargs):
        kwargs.pop("version", None)
        super().__init__(name=name, instructions=instructions,
                         warn_on_duplicate_tools=False, **kwargs)
        self.version = version or ""