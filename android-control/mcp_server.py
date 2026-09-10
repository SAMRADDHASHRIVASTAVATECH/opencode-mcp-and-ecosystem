#!/usr/bin/env python3
"""MCP stdio server for the unified Android Control system.

Serves the whole agent surface (ADB Android-control engine + Remote Touchpad
companion) as MCP tools/resources/prompts over stdio. SDK-independent
(newline-delimited JSON-RPC 2.0).

Run (stdio, for an MCP client):
    android-control-mcp [--offline]
    python mcp_server.py [--offline]
    python -m android_control --mcp [--offline]
"""
import argparse
import os
import sys


def main(argv=None):
    p = argparse.ArgumentParser(prog="android-control-mcp",
                                description="Unified Android Control MCP server")
    p.add_argument("--offline", action="store_true",
                   help="deterministic mock mode (no hardware)")
    p.add_argument("--version", action="version", version="android-control-mcp 1.0.0")
    args = p.parse_args(argv)
    if args.offline:
        os.environ["AC_OFFLINE"] = "1"
    from android_control.mcp import serve_stdio
    serve_stdio()
    return 0


if __name__ == "__main__":
    sys.exit(main())
