# Database / SQL MCP — Implementation Plan

1. Errors, policy, sql_analyze
2. Connection manager + SQLAlchemy generic adapter
3. SQLite + DuckDB native extras (backup, explain)
4. Postgres/MySQL/MSSQL explain/stats methods
5. Tools
6. Tests: sqlite memory workflows covering read, write gate, injection-ish multi-statement, export, backup, introspect, explain
7. README

SQLite is the test engine in CI/sandbox. Other dialects are unit-tested via SQL classification and adapter method presence.
