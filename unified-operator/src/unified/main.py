"""Entry point for the unified operator MCP server."""
from __future__ import annotations

import argparse
import asyncio
import json

from .server import OperatorServer
from .registry import Runtime


def build_server(offline: bool = False) -> OperatorServer:
    rt = Runtime(offline=offline)
    return OperatorServer(rt)


async def _list(srv: OperatorServer) -> None:
    tools = await srv.list_tools()
    out = [{"name": t.name, "description": (t.description or "")[:200]} for t in tools]
    print(json.dumps({"count": len(out), "tools": out}, indent=1))


def main() -> None:
    ap = argparse.ArgumentParser(description="Unified Operator MCP server")
    ap.add_argument("--offline", action="store_true",
                    help="Deterministic offline mode (no live credentials needed)")
    ap.add_argument("--list-tools", action="store_true", help="List tools and exit")
    args = ap.parse_args()
    srv = build_server(offline=args.offline)
    if args.list_tools:
        asyncio.run(_list(srv))
        return
    try:
        asyncio.run(srv.run_stdio_async())
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
