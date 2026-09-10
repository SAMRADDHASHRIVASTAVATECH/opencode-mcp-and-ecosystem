# Database / SQL MCP

Standalone MCP server for **SQLite, PostgreSQL, MySQL/MariaDB, SQL Server, and DuckDB**.

Default policy is **read-only**. Destructive SQL is gated. `DROP DATABASE` is never executed.

Research artifacts in this folder: `research-report.md`, `capability-matrix.md`, `technology-evaluation.md`, `architecture.md`, `security-model.md`.

## Why SQLAlchemy 2 + sqlparse

- One inspector API for schema/PK/FK/indexes across dialects
- Optional drivers: the server starts with only SQLite
- sqlparse classifies statements; combined with a denylist and multi-statement rejection

## Install

```bash
pip install -e ./database-sql-mcp
# extras:
pip install -e "./database-sql-mcp[postgres]"   # psycopg2-binary
pip install -e "./database-sql-mcp[mysql]"
pip install -e "./database-sql-mcp[mssql]"
pip install -e "./database-sql-mcp[duckdb]"
```

## Run

```bash
python -m database_mcp
```

```json
{
  "mcpServers": {
    "database-sql": {
      "command": "python",
      "args": ["-m", "database_mcp"],
      "env": {
        "DB_MCP_URL": "sqlite:////abs/path/app.db",
        "DB_MCP_ROOT": "/abs/path",
        "DB_MCP_ALLOW_WRITE": "0"
      }
    }
  }
}
```

## Policy env

| Variable | Default | Effect |
|----------|---------|--------|
| `DB_MCP_ALLOW_WRITE` | false | INSERT/UPDATE/DELETE |
| `DB_MCP_ALLOW_DDL` | false | CREATE/ALTER |
| `DB_MCP_ALLOW_DESTRUCTIVE` | false | DROP/TRUNCATE + confirm=true |
| `DB_MCP_ALLOW_MULTI` | false | Multiple statements |
| `DB_MCP_MAX_ROWS` | 5000 | Hard cap |
| `DB_MCP_DEFAULT_LIMIT` | 200 | Default SELECT cap |

## Tools

`db_connect` `db_disconnect` `db_status` `db_introspect` `db_search` `db_relationships` `db_indexes` `db_constraints` `db_stats` `db_query` `db_execute` `db_explain` `db_sample` `db_export` `db_import` `db_backup` `db_restore` `db_migrate` `db_diagnose` `db_compare_schema` `sql_analyze`
