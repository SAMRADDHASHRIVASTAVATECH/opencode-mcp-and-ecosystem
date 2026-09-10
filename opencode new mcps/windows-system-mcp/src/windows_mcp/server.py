from __future__ import annotations

from windows_mcp.mcp_compat import create_mcp
from windows_mcp.tools import register

INSTRUCTIONS = """\
Windows system / printer / driver MCP.
Live CIM/PrintManagement calls require Windows. On Linux/macOS, win_platform explains unavailability.
No arbitrary PowerShell. Mutations need confirm=true. Spool directory purge needs WIN_MCP_ALLOW_DESTRUCTIVE=1.
Prefer win_diagnose_printer for print issues instead of guessing individual WMI classes.
"""

mcp = create_mcp("windows-system", INSTRUCTIONS)
register(mcp)


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
