"""Entry points for the OLCAP MCP control plane (stdio).

Run as an MCP stdio server so OpenClaw/OpenCode can connect and discover the
phone.* tools. --list-tools prints the manifest for config validation.
"""
from __future__ import annotations

import argparse
import asyncio
import json

from .config import AppConfig
from .manager import PhoneManager
from .server import OlcapServer


def build(offline: bool = True):
    cfg = AppConfig()
    pm = PhoneManager(cfg)
    return pm, OlcapServer(pm)


async def _list(srv: OlcapServer):
    ts = await srv.list_tools()
    out = [{"name": t.name, "description": (t.description or "")[:160]} for t in ts]
    print(json.dumps({"count": len(out), "tools": out}, indent=1))


def main():
    ap = argparse.ArgumentParser(description="OLCAP Phone Call Management MCP server")
    ap.add_argument("--list-tools", action="store_true",
                    help="List tools and exit")
    ap.add_argument("--config", default="",
                    help="Path to a JSON config file (optional).")
    args = ap.parse_args()

    cfg = AppConfig.from_json(args.config) if args.config else AppConfig()
    pm = PhoneManager(cfg)
    srv = OlcapServer(pm)
    if args.list_tools:
        asyncio.run(_list(srv))
        return
    try:
        asyncio.run(srv.run_stdio_async())
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
