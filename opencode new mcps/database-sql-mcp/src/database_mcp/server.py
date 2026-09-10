"""Database / SQL MCP entrypoint."""

from __future__ import annotations

from database_mcp.mcp_compat import create_mcp
from database_mcp.tools import register

INSTRUCTIONS = """\
SQL / Database MCP. Default is READ-ONLY.
Connect with db_connect, explore with db_introspect / db_relationships, read with db_query.
Writes require DB_MCP_ALLOW_WRITE=1 and db_execute. DROP/TRUNCATE need DB_MCP_ALLOW_DESTRUCTIVE and confirm=true.
DROP DATABASE is never executed. Passwords in URLs are redacted from status/errors.
"""

mcp = create_mcp("database-sql", INSTRUCTIONS)
register(mcp)


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
