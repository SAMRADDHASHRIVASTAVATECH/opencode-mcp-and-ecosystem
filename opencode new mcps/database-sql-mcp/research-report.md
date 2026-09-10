# Database / SQL MCP — Research Report

**Domain:** Relational and analytical SQL databases  
**Date:** 2026-09-09  
**Status:** Research complete.

---

## 1. Domain model

A SQL MCP is not “run any string as SQL.” Expert use is:

1. Discover what exists (catalog, schemas, tables, views, columns, types).
2. Understand relationships (PK/FK, unique, check, indexes).
3. Run **bounded**, preferably parameterized, queries.
4. Explain and diagnose slow or failing SQL.
5. Move data (export/import/backup) without destroying the source.
6. Generate migrations rather than improvising DDL in production.
7. Stay inside a safety policy (read-only by default).

**Terminology**

- Catalog / database / schema / namespace
- Relation: table, view, materialized view
- Constraint: PK, FK, UNIQUE, CHECK, NOT NULL
- Index / covering index / partial index
- Transaction isolation
- Dialect: identifier quoting, types, LIMIT vs TOP vs FETCH
- Plan: EXPLAIN / EXPLAIN ANALYZE (vendor-specific)
- OLTP vs OLAP (DuckDB, column stores)

**Failure modes (research)**

- SQL injection via concatenated LLM-produced SQL (the #1 MCP risk)
- Multi-statement smuggling (`SELECT 1; DROP TABLE`)
- Transaction left open
- Unbounded `SELECT *` blowing memory/tokens
- DDL in “query” tools
- Credential leakage in URLs and error messages
- Locking / vacuum / autovacuum issues
- Encoding and timezone surprises
- Identifier case-folding (Postgres lowercases unquoted)

---

## 2. Official drivers and engines

| Engine | Official / recommended Python driver | Notes |
|--------|--------------------------------------|-------|
| SQLite | stdlib `sqlite3` | Always available; file or `:memory:` |
| PostgreSQL | `psycopg` v3 or `psycopg2` | `psycopg[binary]` preferred modern |
| MySQL | `mysqlclient` or `pymysql` | pymysql is pure Python, easy |
| MariaDB | same as MySQL | dialect `mariadb+pymysql` |
| SQL Server | `pyodbc` or `pymssql` | pyodbc needs system ODBC driver |
| DuckDB | `duckdb` | In-process OLAP; reads CSV/Parquet |
| Generic | SQLAlchemy 2.x + DBAPI | Dialect unification |

ODBC (`pyodbc`) is the escape hatch for exotic engines but requires native drivers.

---

## 3. Existing MCP servers (lessons)

| Project | Approach | Lesson |
|---------|----------|--------|
| Official postgres MCP | Read-only queries + schema | Read-only default is the right default |
| Official sqlite MCP | Read-write + memo | Fine for local files; dangerous if copied blindly to network DBs |
| MCP Alchemy (SQLAlchemy) | Multi-engine, schema, truncated results | SQLAlchemy is the right abstraction |
| executeautomation/mcp-database-server | Node, multi-engine CLI flags | Connection via URL/flags, not one-DB-only |
| Various “run SQL” servers | Thin wrappers | Missing EXPLAIN, FK graph, safety classifier |

**Gaps we will fill**

- SQL statement classifier (read vs write vs DDL vs dangerous)
- EXPLAIN per dialect
- Relationship graph
- Backup/restore for file engines; dump SQL for others
- Import/export CSV/JSON/Parquet (DuckDB/SQLite)
- Query cost guards (timeout, row cap, byte cap)
- Multiple named connections
- Diagnose (locks, size, missing indexes heuristics)
- Never log passwords from DSN

---

## 4. SQLAlchemy 2.0 as the adapter spine

SQLAlchemy Core 2.0 (`create_engine`, `text()`, `inspect()`) gives:

- Unified inspector: tables, columns, PK, FK, indexes, comments
- Connection pooling
- Dialect-specific compiler
- `execution_options(isolation_level="AUTOCOMMIT")` when needed

We will **not** force ORM models. MCP users speak SQL and schema, not Session/Mapped.

Raw DuckDB connection is used when the URL is `duckdb://` because some OLAP features (read_csv_auto, COPY PARQUET) are cleaner natively, with SQLAlchemy as fallback where it works.

---

## 5. Backup / restore reality

| Engine | Practical backup | Restore |
|--------|------------------|---------|
| SQLite | `VACUUM INTO` / file copy with backup API | Replace file or `.restore` |
| DuckDB | `EXPORT DATABASE` / file copy | `IMPORT DATABASE` |
| PostgreSQL | `pg_dump` if CLI present; else SQL COPY | `pg_restore` / psql |
| MySQL | `mysqldump` if CLI present | mysql client |
| SQL Server | `BACKUP DATABASE` (needs permission, path on server) | `RESTORE` — often too privileged |

MCP must not pretend `pg_dump` exists. Detect CLI, else offer logical SQL dump of selected tables (bounded).

---

## 6. Query optimization & diagnostics

- PostgreSQL: `EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON)` when analyze=true
- SQLite: `EXPLAIN QUERY PLAN`
- MySQL/MariaDB: `EXPLAIN FORMAT=JSON`
- SQL Server: `SET SHOWPLAN_TEXT` / `EXPLAIN` (version-dependent)
- DuckDB: `EXPLAIN` / `EXPLAIN ANALYZE`

Index advice will be heuristic (filter/join columns without indexes), not a query-tuner product.

---

## 7. Security research (SQL-specific)

See `security-model.md`.

Default policy: **read-only**. `db_query` accepts SELECT/WITH/EXPLAIN/SHOW/PRAGMA(read). Writes require `DB_MCP_ALLOW_WRITE=1` and `db_execute`. Destructive DDL (`DROP`, `TRUNCATE`, `ALTER … DROP`) requires `DB_MCP_ALLOW_DDL=1` plus explicit `confirm=true`.

SQL parsing: sqlparse for split/classification. Not a full security boundary (parser can be fooled); combine with:

- Reject multiple statements unless `allow_multi=true`
- Bind parameters when `params` provided
- Engine-level role: Postgres `default_transaction_read_only`, SQLite `query_only` pragma when read-only
- Row limit wrapping where dialect allows

---

## 8. Performance

- Server-side cursors / fetchmany for large results
- Truncate cell values (default 500 chars)
- Default `limit=200`, hard cap 5000
- Query timeout via statement_timeout (PG), max_execution_time (MySQL), or Python watchdog
- Inspector results cached per connection id for a few seconds

---

## 9. What will not be built

- A query optimizer product
- Replication management
- Cloud vendor control planes (RDS APIs)
- Automatic production migrations without confirm
- ORM codegen as a primary feature
