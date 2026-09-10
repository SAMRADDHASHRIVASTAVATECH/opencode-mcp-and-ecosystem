"""Dialect-specific EXPLAIN, stats, backup."""

from __future__ import annotations

import shutil
from pathlib import Path
from typing import Any

from sqlalchemy import text

from database_mcp.errors import DependencyMissing, UnsupportedError, ValidationError
from database_mcp.manager import ConnectionInfo


def explain(info: ConnectionInfo, sql: str, analyze: bool = False) -> list[str]:
    dialect = info.dialect
    if dialect == "postgresql":
        prefix = "EXPLAIN (ANALYZE, BUFFERS, FORMAT TEXT) " if analyze else "EXPLAIN "
        q = prefix + sql
    elif dialect == "sqlite":
        q = "EXPLAIN QUERY PLAN " + sql
    elif dialect == "mysql":
        q = "EXPLAIN " + sql
    elif dialect == "duckdb":
        q = ("EXPLAIN ANALYZE " if analyze else "EXPLAIN ") + sql
    elif dialect == "mssql":
        q = "SET SHOWPLAN_TEXT ON; "  # not mixed easily
        q = sql  # fallback: run SET then explain not portable; just prefix comment
        with info.engine.connect() as conn:
            conn.execute(text("SET SHOWPLAN_TEXT ON"))
            try:
                result = conn.execute(text(sql))
                return [str(row[0]) if len(row) == 1 else str(list(row)) for row in result]
            finally:
                conn.execute(text("SET SHOWPLAN_TEXT OFF"))
    else:
        q = "EXPLAIN " + sql
    with info.engine.connect() as conn:
        result = conn.execute(text(q))
        lines = []
        for row in result:
            lines.append(" | ".join("" if c is None else str(c) for c in row))
        return lines


def table_stats(info: ConnectionInfo, schema: str | None, table: str) -> dict[str, Any]:
    dialect = info.dialect
    with info.engine.connect() as conn:
        if dialect == "sqlite":
            n = conn.execute(text(f'SELECT COUNT(*) FROM "{table}"')).scalar()
            return {"table": table, "row_estimate": n, "engine": "sqlite"}
        if dialect == "duckdb":
            n = conn.execute(text(f'SELECT COUNT(*) FROM "{table}"')).scalar()
            return {"table": table, "row_estimate": n, "engine": "duckdb"}
        if dialect == "postgresql":
            row = conn.execute(
                text(
                    """
                    SELECT c.reltuples::bigint AS est,
                           pg_total_relation_size(c.oid) AS bytes
                    FROM pg_class c
                    JOIN pg_namespace n ON n.oid = c.relnamespace
                    WHERE c.relname = :t AND (CAST(:s AS text) IS NULL OR n.nspname = :s)
                    """
                ),
                {"t": table, "s": schema},
            ).first()
            if not row:
                return {"table": table, "row_estimate": None}
            return {"table": table, "row_estimate": int(row[0] or 0), "bytes": int(row[1] or 0)}
        if dialect == "mysql":
            row = conn.execute(
                text(
                    """
                    SELECT TABLE_ROWS, DATA_LENGTH+INDEX_LENGTH
                    FROM information_schema.TABLES
                    WHERE TABLE_NAME=:t AND (:s IS NULL OR TABLE_SCHEMA=:s)
                    """
                ),
                {"t": table, "s": schema},
            ).first()
            if not row:
                return {"table": table}
            return {"table": table, "row_estimate": row[0], "bytes": row[1]}
        n = conn.execute(text(f"SELECT COUNT(*) FROM {table}")).scalar()
        return {"table": table, "row_estimate": n}


def backup(info: ConnectionInfo, dest: Path, tables: list[str] | None = None) -> dict[str, Any]:
    dest.parent.mkdir(parents=True, exist_ok=True)
    dialect = info.dialect
    if dialect == "sqlite":
        url = info.url
        # sqlite:////path
        src = _sqlite_path(url)
        if src is None:
            raise ValidationError("Cannot backup in-memory SQLite unless you VACUUM INTO from a file DB")
        with info.engine.connect() as conn:
            conn.execute(text(f"VACUUM INTO '{dest.as_posix()}'"))
        return {"path": str(dest), "method": "sqlite VACUUM INTO"}
    if dialect == "duckdb":
        with info.engine.connect() as conn:
            conn.execute(text(f"EXPORT DATABASE '{dest.as_posix()}'"))
        return {"path": str(dest), "method": "duckdb EXPORT DATABASE"}
    if dialect == "postgresql":
        pg_dump = shutil.which("pg_dump")
        if not pg_dump:
            return _logical_dump(info, dest, tables)
        raise DependencyMissing("pg_dump found but URL-based subprocess dump is not auto-run to avoid leaking passwords on argv; use logical dump")
    return _logical_dump(info, dest, tables)


def _logical_dump(info: ConnectionInfo, dest: Path, tables: list[str] | None) -> dict[str, Any]:
    from sqlalchemy import inspect as sa_inspect

    insp = sa_inspect(info.engine)
    names = tables or insp.get_table_names()
    parts = [f"-- logical dump dialect={info.dialect}"]
    with info.engine.connect() as conn:
        for table in names:
            cols = [c["name"] for c in insp.get_columns(table)]
            col_list = ", ".join(f'"{c}"' for c in cols)
            rows = conn.execute(text(f'SELECT {col_list} FROM "{table}"')).fetchmany(10_000)
            parts.append(f"-- table {table} ({len(rows)} rows dumped, cap 10000)")
            for row in rows:
                vals = []
                for v in row:
                    if v is None:
                        vals.append("NULL")
                    elif isinstance(v, (int, float)):
                        vals.append(str(v))
                    else:
                        s = str(v).replace("'", "''")
                        vals.append(f"'{s}'")
                parts.append(f'INSERT INTO "{table}" ({col_list}) VALUES ({", ".join(vals)});')
    dest.write_text("\n".join(parts) + "\n", encoding="utf-8")
    return {"path": str(dest), "method": "logical INSERT dump", "tables": names}


def restore(info: ConnectionInfo, src: Path) -> dict[str, Any]:
    dialect = info.dialect
    if dialect == "sqlite":
        raise UnsupportedError(
            "SQLite restore is replacing a file database. Connect to the backup file instead of overwriting live DBs from the MCP."
        )
    sql = src.read_text(encoding="utf-8")
    statements = [s.strip() for s in sql.split(";") if s.strip() and not s.strip().startswith("--")]
    applied = 0
    with info.engine.begin() as conn:
        for stmt in statements[:5000]:
            conn.execute(text(stmt))
            applied += 1
    return {"applied": applied, "path": str(src)}


def apply_timeout(info: ConnectionInfo, seconds: int) -> None:
    dialect = info.dialect
    try:
        with info.engine.connect() as conn:
            if dialect == "postgresql":
                conn.execute(text(f"SET statement_timeout = {int(seconds * 1000)}"))
                conn.commit()
            elif dialect == "mysql":
                conn.execute(text(f"SET SESSION MAX_EXECUTION_TIME={int(seconds * 1000)}"))
    except Exception:
        pass


def _sqlite_path(url: str) -> Path | None:
    from sqlalchemy.engine import make_url

    u = make_url(url)
    db = u.database
    if not db or db == ":memory:":
        return None
    return Path(db)
