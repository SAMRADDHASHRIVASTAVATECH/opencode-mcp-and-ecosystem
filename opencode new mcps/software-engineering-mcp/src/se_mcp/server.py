from __future__ import annotations

from se_mcp.mcp_compat import create_mcp
from se_mcp.tools import register

INSTRUCTIONS = """\
Universal Software Engineering MCP — the capability layer for this ecosystem.

1. se_route / se_ecosystem first. Do NOT rebuild Office, SQL, Windows, or Android specialists.
2. Android apps → android-development-mcp. Documents → office-documents-mcp.
   Databases → database-sql-mcp. Windows printers/services → windows-system-mcp.
3. For CLI/lib/API/web/desktop/native: se_create_project with an explicit template
   (python-cli, node-express, c-cli, go-cli, rust-cli, java-cli, static-web, … — not MERN-only).
4. Detect toolchains. Missing compilers return DEPENDENCY_MISSING, never fake success.
5. ASCII trees → se_ascii_tree (parse/preview/scan/create). SDLC blueprints → se_sdlc
   (catalog/search/generate/export). Desktop apps → se_launch_gui (ascii_tree|sdlc).
6. Read skills in the ecosystem skills/ directory for how to decide, not just which tool to call.
"""

mcp = create_mcp("software-engineering", INSTRUCTIONS)
register(mcp)


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
