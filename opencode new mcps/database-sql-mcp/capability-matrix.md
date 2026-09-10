# Database / SQL MCP — Capability Matrix

## BASIC

| Capability | Status | Tool |
|------------|--------|------|
| Connect via URL | P | `db_connect` |
| Disconnect / list connections | P | `db_disconnect`, `db_status` |
| List schemas/tables/views | P | `db_introspect` |
| Describe columns & types | P | `db_introspect` |
| Run SELECT | P | `db_query` |
| Sample rows | P | `db_sample` |
| Export to CSV/JSON | P | `db_export` |

## ADVANCED

| Capability | Status | Tool |
|------------|--------|------|
| Parameterized SQL | P | `db_query`, `db_execute` |
| DML (insert/update/delete) | P | `db_execute` (gated) |
| EXPLAIN / EXPLAIN ANALYZE | P | `db_explain` |
| Indexes | P | `db_indexes` |
| Constraints PK/FK/UNIQUE/CHECK | P | `db_constraints` |
| Relationship graph | P | `db_relationships` |
| Search tables/columns by name | P | `db_search` |
| Table/index size stats | P | `db_stats` |
| Import CSV/JSON | P | `db_import` |
| SQL classify/format | P | `sql_analyze` |

## EXPERT / ADMIN / DIAGNOSTICS

| Capability | Status | Tool |
|------------|--------|------|
| Dialect-aware identifier quoting | P | adapters |
| Read-only transaction enforcement | P | policy + engine |
| SQLite backup API / VACUUM INTO | P | `db_backup` |
| DuckDB export database | P | `db_backup` |
| pg_dump/mysqldump if present | F | `db_backup` |
| Logical table dump | P | `db_backup` |
| Restore file engines | P | `db_restore` |
| Generate migration SQL (not apply) | P | `db_migrate` |
| Diagnose connectivity/locks/counts | P | `db_diagnose` |
| Multi-connection | P | `db_connect` names |
| DuckDB read CSV/Parquet via SQL | P | `db_query` on duckdb |

## BATCH / ANALYSIS / CONVERSION

| Capability | Status | Tool |
|------------|--------|------|
| Multi-table export | BATCH | `db_export` |
| Compare two schemas | ANALYSIS | `db_compare_schema` |
| CSV/JSON/Parquet interchange | CONVERSION | `db_export` / `db_import` |

## Out of scope

| Item | Reason |
|------|--------|
| Execute OS commands from SQL (`COPY TO PROGRAM`) | RCE |
| Superuser role management as default | Too dangerous |
| Automatic DROP DATABASE | Refuse |
| Oracle/DB2 first-class (SQLAlchemy may still connect) | Driver/license complexity; generic URL may work |
