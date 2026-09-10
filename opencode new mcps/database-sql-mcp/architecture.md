# Database / SQL MCP — Architecture

```
MCP client
    ▼
database_mcp.server
    ▼
policy (read-only / write / ddl) + sql_analyze
    ▼
connection manager (named engines, inspect cache)
    ▼
adapters
    sqlite | postgres | mysql | mssql | duckdb | generic sqlalchemy
    ▼
DBAPI / engine
```

## Why adapters

EXPLAIN, stats, and backup are dialect-specific. Schema listing is generic (Inspector). Adapters implement:

- `explain(sql, analyze)`
- `table_stats`
- `backup` / `restore`
- `apply_timeout`
- `set_query_only`

Generic adapter provides best-effort defaults.

## Tools

- `db_connect` `db_disconnect` `db_status`
- `db_introspect` `db_search` `db_relationships` `db_indexes` `db_constraints` `db_stats`
- `db_query` `db_execute` `db_explain` `db_sample`
- `db_export` `db_import` `db_backup` `db_restore`
- `db_migrate` `db_diagnose` `db_compare_schema`
- `sql_analyze`

## Connection URLs

```
sqlite:////abs/path.db
sqlite:///:memory:
postgresql+psycopg2://user:pass@host:5432/db
mysql+pymysql://user:pass@host:3306/db
mssql+pymssql://user:pass@host/db
duckdb:////abs/path.duckdb
duckdb:///:memory:
```

Env `DB_MCP_URL` can auto-connect as `default`.

## Safety pipeline for every SQL tool

1. Strip comments (best effort)
2. Split statements (reject multi unless allowed)
3. Classify: read / write / ddl / dangerous / unknown
4. Enforce policy
5. Apply limit/timeout
6. Execute with bound params
7. Truncate result
8. Close/return connection to pool
