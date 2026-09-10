# Database MCP — second research pass / gap analysis

## Improvements after first implementation

- SQLite `PRAGMA query_only` when writes disabled
- PostgreSQL `default_transaction_read_only` when writes disabled
- Always-deny list for COPY PROGRAM / xp_cmdshell / LOAD_FILE / DROP DATABASE

## Remaining gaps

| Gap | Notes |
|-----|-------|
| sqlglot transpile | Optional later |
| Server-side cursors for huge extracts | fetchmany cap is enough for MCP tokens |
| Oracle / DB2 first-class | SQLAlchemy URL may still work with extra drivers |
| Live query killer | timeout best-effort per dialect |
| Migration version table | db_migrate is explicit SQL generator, not Alembic |
| Row-level security policies admin | Too privileged |

Drivers remain extras so the server imports without PostgreSQL libraries installed.
