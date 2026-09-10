"""MCP entrypoint for the OLCAP realtime assistant (stdio)."""
from __future__ import annotations

import argparse
import asyncio
import json

from .assistant import Assistant
from .config import AppConfig
from .server import OlcapRealtimeServer


async def _list(srv):
    ts = await srv.list_tools()
    out = [{"name": t.name, "description": (t.description or "")[:120]} for t in ts]
    print(json.dumps({"count": len(out), "tools": out}, indent=1))


def build(config_path: str = ""):
    cfg = AppConfig.from_json(config_path) if config_path else AppConfig()
    a = Assistant(cfg)
    return a, OlcapRealtimeServer(a)


def main():
    ap = argparse.ArgumentParser(description="OLCAP Realtime Assistant MCP server")
    ap.add_argument("--config", default="", help="JSON config path (optional).")
    ap.add_argument("--list-tools", action="store_true", help="List tools and exit.")
    ap.add_argument("--health", action="store_true",
                    help="Print a health report and exit (no hardware assumed).")
    ap.add_argument("--diag", action="store_true", help="Run the pipeline diagnostic.")
    args = ap.parse_args()

    assistant, srv = build(args.config)
    if args.list_tools:
        asyncio.run(_list(srv))
        return
    if args.health or args.diag:
        print(json.dumps(assistant.diag() if args.diag else assistant.health(),
                         default=str, indent=1))
        return
    try:
        asyncio.run(srv.run_stdio_async())
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
