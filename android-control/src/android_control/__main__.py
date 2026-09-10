"""CLI entry point.

Usage:
    python -m android_control --offline                # master boot report
    python -m android_control --offline --goal "Open the camera on every phone"
    python -m android_control --offline --goal "Take screenshots of every phone"
    android-control --offline --discover
"""
from __future__ import annotations

import argparse
import json
import sys


def _dump(result):
    print(json.dumps(result.to_dict() if hasattr(result, "to_dict") else result,
                     indent=2, default=str))


def main(argv=None):
    p = argparse.ArgumentParser(prog="android-control",
                                description="Universal Android Control")
    p.add_argument("--offline", action="store_true",
                   help="deterministic mock mode (no hardware)")
    p.add_argument("--goal", type=str, default="",
                   help="natural-language goal, e.g. 'open the camera on every phone'")
    p.add_argument("--discover", action="store_true",
                   help="discover devices and print the fleet")
    p.add_argument("--list-skills", action="store_true",
                   help="list available skill names")
    p.add_argument("--remote-touchpad", type=str, default="",
                   metavar="ACTION",
                   help="manage the Remote-Touchpad companion: start|status|stop|resolve")
    p.add_argument("--mcp", action="store_true",
                   help="serve the MCP stdio server (agent-callable)")
    p.add_argument("--version", action="version", version="android-control 1.0.0")
    args = p.parse_args(argv)

    if args.mcp:
        from .mcp import serve_stdio
        serve_stdio()
        return 0

    if args.list_skills:
        from .skills import ALL_SKILLS
        print("\n".join(sorted(ALL_SKILLS)))
        return 0

    if args.remote_touchpad:
        from .skills import android_remote_touchpad
        _dump(android_remote_touchpad(action=args.remote_touchpad))
        return 0

    if args.goal:
        from . import run_goal
        r = run_goal(args.goal, offline=args.offline)
        _dump(r)
        return 0

    # master boot report
    from .skills import android_control
    r = android_control(offline=args.offline)
    _dump(r)
    if args.discover:
        return 0
    return 0


if __name__ == "__main__":
    sys.exit(main())
