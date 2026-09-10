# Database / SQL MCP — Technology Evaluation

## Decision summary

| Concern | Primary | Fallback | Not chosen as primary |
|---------|---------|----------|----------------------|
| Abstraction | SQLAlchemy 2.0 Core + Inspector | Native drivers for DuckDB extras | ORM, raw per-engine copies |
| SQLite | stdlib sqlite3 via SQLAlchemy | sqlite3 backup API directly | — |
| PostgreSQL | psycopg2-binary (ubiquity) | psycopg3 if installed | asyncpg (async complexity) |
| MySQL/MariaDB | PyMySQL | mysqlclient | — |
| SQL Server | pymssql | pyodbc if installed | — |
| DuckDB | duckdb package + SQLAlchemy duckdb:// | native duckdb.connect | Polars-only |
| SQL parse | sqlparse | regex classifier | sqlglot (heavier, optional later) |
| MCP | official Python SDK | — | — |

## Why SQLAlchemy 2 over “just psycopg”

MCP Alchemy already proved multi-engine via SQLAlchemy. Inspector API covers 90% of schema tools without writing information_schema queries per dialect. We still emit dialect SQL for EXPLAIN, stats, and backup.

## Driver choice rationale

- **psycopg2-binary**: easiest install; wheels. psycopg3 is better long-term but mixed MCP ecosystem still on psycopg2.
- **PyMySQL**: pure Python, no native MySQL client required.
- **pymssql**: no system ODBC required (pyodbc is better on Windows with real ODBC but fails in Linux sandboxes without msodbcsql).
- **duckdb**: in-process, MIT, first-class CSV/Parquet — the right OLAP companion to SQLite.

Drivers are **optional extras**. SQLite always works. Missing driver → `DEPENDENCY_MISSING` with install hint, never a crash at import of the server.

## sqlparse vs sqlglot

sqlparse: small, enough to split statements and get the first keyword.  
sqlglot: excellent dialect transpile; larger dependency. Start with sqlparse; classify dangerous keywords with a conservative regex on the stripped SQL.

## Pandas?

Not required for core SQL. Export uses csv/json stdlib. Optional future.

## License

SQLAlchemy MIT, DuckDB MIT, PyMySQL MIT, sqlparse BSD, psycopg LGPL (binary extra). Core MCP works with only SQLAlchemy + stdlib sqlite.
