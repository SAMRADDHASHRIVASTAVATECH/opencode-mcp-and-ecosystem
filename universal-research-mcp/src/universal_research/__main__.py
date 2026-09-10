"""`python -m universal_research [--offline]` runs the MCP stdio server."""
import argparse
import os
import sys


def main(argv=None):
    p = argparse.ArgumentParser(prog="universal-research-mcp",
                                description="Universal Web Research MCP server")
    p.add_argument("--offline", action="store_true",
                   help="run offline against the deterministic mock provider")
    p.add_argument("--list-tools", action="store_true",
                   help="print available tool names and exit")
    p.add_argument("--list-skills", action="store_true",
                   help="print available skill names and exit")
    args = p.parse_args(argv)

    if args.offline:
        os.environ["UR_OFFLINE"] = "1"
    from . import functions as F
    if args.list_tools:
        for t in F.list_tools()["tools"]:
            print(t["name"])
        return 0
    if args.list_skills:
        for s in F.list_skills()["skills"]:
            print(s["name"])
        return 0
    from . import mcp_interface
    mcp_interface.serve_stdio_from_binary()
    return 0


if __name__ == "__main__":
    sys.exit(main())
