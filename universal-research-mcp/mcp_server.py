#!/usr/bin/env python3
"""Entry point that runs the Universal Web Research MCP stdio server.

This module is what an MCP client (Claude Desktop, Cursor, npx-style tooling,
OpenCode, etc.) launches. It speaks MCP over stdio using newline-delimited
JSON-RPC 2.0 and requires NO external MCP SDK — only `httpx` + parsing libs.

Run directly:
    python mcp_server.py [--offline]
or via the console script / module:
    universal-research-mcp [--offline]
    python -m universal_research [--offline]
"""
import argparse
import os
import sys


def main(argv=None):
    p = argparse.ArgumentParser(prog="mcp_server",
                                description="Universal Web Research MCP server")
    p.add_argument("--offline", action="store_true",
                   help="run offline against the deterministic mock provider")
    p.add_argument("--version", action="version", version="universal-research-mcp 1.0.0")
    args = p.parse_args(argv)
    if args.offline:
        os.environ["UR_OFFLINE"] = "1"
    from universal_research import mcp_interface
    mcp_interface.serve_stdio_from_binary()
    return 0


if __name__ == "__main__":
    sys.exit(main())
