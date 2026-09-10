"""Semantic database tools."""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

from sqlalchemy import text

from database_mcp import adapters
from database_mcp.config import SETTINGS
from database_mcp.errors import NotFoundError, PolicyError, ValidationError
from database_mcp.execute import run_sql
from database_mcp.manager import connect as mgr_connect
from database_mcp.manager import disconnect as mgr_disconnect
from database_mcp.manager import get, inspector, status as mgr_status
from database_mcp.results import run
from database_mcp.sql_policy import classify, enforce, format_sql


def register(mcp: Any) -> None:
    @mcp.tool()
    def db_connect(url: str, name: str = "default") -> dict[str, Any]:
        """Connect to a SQL database.

        URL examples:
          sqlite:////abs/path.db
          sqlite:///:memory:
          postgresql+psycopg2://user:pass@host:5432/db
          mysql+pymysql://user:pass@host:3306/db
          mssql+pymssql://user:pass@host/db
          duckdb:////abs/path.duckdb
        """
        return run(mgr_connect, url=url, name=name)

    @mcp.tool()
    def db_disconnect(name: str = "default") -> dict[str, Any]:
        """Dispose a named connection."""
        return run(mgr_disconnect, name=name)

    @mcp.tool()
    def db_status(name: str | None = None) -> dict[str, Any]:
        """List connections (passwords redacted) and the current write/DDL policy."""
        return run(mgr_status, name=name)

    @mcp.tool()
    def db_introspect(
        name: str = "default",
        schema: str | None = None,
        table: str | None = None,
    ) -> dict[str, Any]:
        """List schemas, tables, views, and optionally describe one table's columns."""
        return run(_introspect, name=name, schema=schema, table=table)

    @mcp.tool()
    def db_search(query: str, name: str = "default") -> dict[str, Any]:
        """Find tables or columns whose names contain the query string."""
        return run(_search, query=query, name=name)

    @mcp.tool()
    def db_relationships(name: str = "default", schema: str | None = None) -> dict[str, Any]:
        """Foreign-key graph for the catalog."""
        return run(_relationships, name=name, schema=schema)

    @mcp.tool()
    def db_indexes(name: str = "default", table: str | None = None, schema: str | None = None) -> dict[str, Any]:
        """List indexes, optionally for one table."""
        return run(_indexes, name=name, table=table, schema=schema)

    @mcp.tool()
    def db_constraints(name: str = "default", table: str | None = None, schema: str | None = None) -> dict[str, Any]:
        """Primary keys, foreign keys, unique constraints."""
        return run(_constraints, name=name, table=table, schema=schema)

    @mcp.tool()
    def db_stats(table: str, name: str = "default", schema: str | None = None) -> dict[str, Any]:
        """Row estimates / size for a table (dialect-aware)."""
        return run(_stats, table=table, name=name, schema=schema)

    @mcp.tool()
    def db_query(
        sql: str,
        name: str = "default",
        params: dict[str, Any] | None = None,
        limit: int | None = None,
    ) -> dict[str, Any]:
        """Run a read-only SQL statement (SELECT/WITH/EXPLAIN/SHOW/PRAGMA read). Never runs DML/DDL."""
        return run(_query, sql=sql, name=name, params=params, limit=limit)

    @mcp.tool()
    def db_execute(
        sql: str,
        name: str = "default",
        params: dict[str, Any] | None = None,
        confirm: bool = False,
    ) -> dict[str, Any]:
        """Run write/DDL SQL. Requires DB_MCP_ALLOW_WRITE and/or DB_MCP_ALLOW_DDL. Destructive needs confirm=true."""
        return run(_execute, sql=sql, name=name, params=params, confirm=confirm)

    @mcp.tool()
    def db_explain(sql: str, name: str = "default", analyze: bool = False) -> dict[str, Any]:
        """Dialect-aware EXPLAIN (ANALYZE optional where supported)."""
        return run(_explain, sql=sql, name=name, analyze=analyze)

    @mcp.tool()
    def db_sample(table: str, name: str = "default", limit: int = 20, schema: str | None = None) -> dict[str, Any]:
        """Return a small sample of rows from a table."""
        return run(_sample, table=table, name=name, limit=limit, schema=schema)

    @mcp.tool()
    def db_export(
        table: str,
        dest: str,
        name: str = "default",
        fmt: str = "csv",
        limit: int = 10000,
    ) -> dict[str, Any]:
        """Export a table to csv or json under the sandbox root."""
        return run(_export, table=table, dest=dest, name=name, fmt=fmt, limit=limit)

    @mcp.tool()
    def db_import(
        dest_table: str,
        src: str,
        name: str = "default",
        if_exists: str = "fail",
    ) -> dict[str, Any]:
        """Import CSV/JSON into a table. Requires write permission. if_exists=fail|append|replace."""
        return run(_import, dest_table=dest_table, src=src, name=name, if_exists=if_exists)

    @mcp.tool()
    def db_backup(dest: str, name: str = "default", tables: list[str] | None = None) -> dict[str, Any]:
        """Backup: SQLite VACUUM INTO, DuckDB EXPORT, otherwise bounded logical INSERT dump."""
        return run(_backup, dest=dest, name=name, tables=tables)

    @mcp.tool()
    def db_restore(src: str, name: str = "default") -> dict[str, Any]:
        """Restore from a logical SQL dump. Requires DDL/write policy. SQLite file replace is refused."""
        return run(_restore, src=src, name=name)

    @mcp.tool()
    def db_migrate(
        operations: list[dict[str, Any]],
        apply: bool = False,
        name: str = "default",
        confirm: bool = False,
    ) -> dict[str, Any]:
        """Generate (and optionally apply) simple migration SQL: create_table, add_column, add_index.

        Default apply=false so the model can review SQL first.
        """
        return run(_migrate, operations=operations, apply=apply, name=name, confirm=confirm)

    @mcp.tool()
    def db_diagnose(name: str = "default") -> dict[str, Any]:
        """Connectivity, dialect, table counts, sqlite compile options / basic health."""
        return run(_diagnose, name=name)

    @mcp.tool()
    def db_compare_schema(name_a: str, name_b: str) -> dict[str, Any]:
        """Compare table/column sets of two named connections."""
        return run(_compare, name_a=name_a, name_b=name_b)

    @mcp.tool()
    def sql_analyze(sql: str) -> dict[str, Any]:
        """Classify SQL (read/write/ddl/destructive), split statements, and pretty-format it. Does not execute."""
        return run(_sql_analyze, sql=sql)


def _sandbox_file(path: str, must_exist: bool = False) -> Path:
    raw = Path(path).expanduser()
    candidate = (raw if raw.is_absolute() else SETTINGS.root / raw).resolve()
    try:
        candidate.relative_to(SETTINGS.root)
    except ValueError as exc:
        if not SETTINGS.allow_any_path:
            raise PolicyError("Path is outside DB_MCP_ROOT") from exc
    if must_exist and not candidate.exists():
        raise NotFoundError(str(candidate))
    return candidate


def _ident(name: str) -> str:
    if not name or not all(c.isalnum() or c in {"_", "."} for c in name):
        raise ValidationError(f"Unsafe identifier: {name}")
    return name


def _introspect(name: str, schema: str | None, table: str | None) -> dict[str, Any]:
    insp = inspector(name)
    schemas = []
    try:
        schemas = list(insp.get_schema_names())
    except Exception:
        schemas = []
    tables = list(insp.get_table_names(schema=schema))
    views = []
    try:
        views = list(insp.get_view_names(schema=schema))
    except Exception:
        pass
    out: dict[str, Any] = {"schemas": schemas, "tables": tables, "views": views, "dialect": get(name).dialect}
    if table:
        cols = insp.get_columns(table, schema=schema)
        out["table"] = table
        out["columns"] = [
            {
                "name": c["name"],
                "type": str(c.get("type")),
                "nullable": c.get("nullable"),
                "default": str(c.get("default")) if c.get("default") is not None else None,
            }
            for c in cols
        ]
        try:
            out["pk"] = insp.get_pk_constraint(table, schema=schema)
        except Exception:
            out["pk"] = None
    return out


def _search(query: str, name: str) -> dict[str, Any]:
    q = query.lower()
    insp = inspector(name)
    hits = []
    for table in insp.get_table_names():
        if q in table.lower():
            hits.append({"table": table, "column": None})
        for col in insp.get_columns(table):
            if q in col["name"].lower():
                hits.append({"table": table, "column": col["name"]})
    return {"hits": hits[:200]}


def _relationships(name: str, schema: str | None) -> dict[str, Any]:
    insp = inspector(name)
    edges = []
    for table in insp.get_table_names(schema=schema):
        for fk in insp.get_foreign_keys(table, schema=schema):
            edges.append(
                {
                    "from_table": table,
                    "from_cols": fk.get("constrained_columns"),
                    "to_table": fk.get("referred_table"),
                    "to_cols": fk.get("referred_columns"),
                    "name": fk.get("name"),
                }
            )
    return {"foreign_keys": edges}


def _indexes(name: str, table: str | None, schema: str | None) -> dict[str, Any]:
    insp = inspector(name)
    tables = [table] if table else insp.get_table_names(schema=schema)
    out = []
    for t in tables:
        try:
            out.append({"table": t, "indexes": insp.get_indexes(t, schema=schema)})
        except Exception as exc:
            out.append({"table": t, "error": str(exc)})
    return {"indexes": out}


def _constraints(name: str, table: str | None, schema: str | None) -> dict[str, Any]:
    insp = inspector(name)
    tables = [table] if table else insp.get_table_names(schema=schema)
    out = []
    for t in tables:
        item: dict[str, Any] = {"table": t}
        try:
            item["pk"] = insp.get_pk_constraint(t, schema=schema)
        except Exception:
            item["pk"] = None
        try:
            item["fk"] = insp.get_foreign_keys(t, schema=schema)
        except Exception:
            item["fk"] = []
        try:
            item["unique"] = insp.get_unique_constraints(t, schema=schema)
        except Exception:
            item["unique"] = []
        out.append(item)
    return {"constraints": out}


def _stats(table: str, name: str, schema: str | None) -> dict[str, Any]:
    return adapters.table_stats(get(name), schema, _ident(table))


def _query(sql: str, name: str, params: dict[str, Any] | None, limit: int | None) -> dict[str, Any]:
    enforce(sql, for_query=True)
    info = get(name)
    return run_sql(info, sql, params=params, limit=limit, fetch=True)


def _execute(sql: str, name: str, params: dict[str, Any] | None, confirm: bool) -> dict[str, Any]:
    enforce(sql, for_query=False, confirm=confirm)
    info = get(name)
    return run_sql(info, sql, params=params, fetch=True)


def _explain(sql: str, name: str, analyze: bool) -> dict[str, Any]:
    # EXPLAIN wrapping: classify inner as read
    inner = sql.strip()
    if not inner.lower().startswith("explain"):
        enforce(inner, for_query=True)
    info = get(name)
    lines = adapters.explain(info, inner, analyze=analyze)
    return {"plan": lines, "dialect": info.dialect, "analyze": analyze}


def _sample(table: str, name: str, limit: int, schema: str | None) -> dict[str, Any]:
    ident = _ident(table)
    q = f'SELECT * FROM "{ident}"'
    if schema:
        q = f'SELECT * FROM "{_ident(schema)}"."{ident}"'
    info = get(name)
    cap = min(max(limit, 1), 200)
    return run_sql(info, q, limit=cap)


def _export(table: str, dest: str, name: str, fmt: str, limit: int) -> dict[str, Any]:
    path = _sandbox_file(dest)
    path.parent.mkdir(parents=True, exist_ok=True)
    info = get(name)
    ident = _ident(table)
    data = run_sql(info, f'SELECT * FROM "{ident}"', limit=min(limit, SETTINGS.max_rows))
    if fmt == "json":
        path.write_text(json.dumps(data["rows"], indent=2, default=str), encoding="utf-8")
    elif fmt == "csv":
        with path.open("w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=data["columns"])
            w.writeheader()
            for row in data["rows"]:
                w.writerow(row)
    else:
        raise ValidationError("fmt must be csv or json")
    return {"path": str(path), "rows": data["rowcount"], "format": fmt}


def _import(dest_table: str, src: str, name: str, if_exists: str) -> dict[str, Any]:
    if not SETTINGS.allow_write:
        raise PolicyError("Writes disabled. Set DB_MCP_ALLOW_WRITE=1")
    path = _sandbox_file(src, must_exist=True)
    info = get(name)
    table = _ident(dest_table)
    if path.suffix.lower() == ".json":
        rows = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(rows, dict) and "rows" in rows:
            rows = rows["rows"]
    else:
        with path.open(newline="", encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
    if not rows:
        return {"inserted": 0}
    cols = list(rows[0].keys())
    for c in cols:
        _ident(c)
    with info.engine.begin() as conn:
        if if_exists == "replace":
            if not SETTINGS.allow_ddl:
                raise PolicyError("replace needs DB_MCP_ALLOW_DDL=1")
            conn.execute(text(f'DROP TABLE IF EXISTS "{table}"'))
        if if_exists in {"replace", "fail"}:
            col_sql = ", ".join(f'"{c}" TEXT' for c in cols)
            if SETTINGS.allow_ddl or if_exists == "fail":
                try:
                    conn.execute(text(f'CREATE TABLE "{table}" ({col_sql})'))
                except Exception:
                    if if_exists == "fail":
                        pass
        placeholders = ", ".join(f":{c}" for c in cols)
        col_list = ", ".join(f'"{c}"' for c in cols)
        ins = text(f'INSERT INTO "{table}" ({col_list}) VALUES ({placeholders})')
        for row in rows:
            conn.execute(ins, {c: row.get(c) for c in cols})
    return {"inserted": len(rows), "table": table}


def _backup(dest: str, name: str, tables: list[str] | None) -> dict[str, Any]:
    path = _sandbox_file(dest)
    return adapters.backup(get(name), path, tables)


def _restore(src: str, name: str) -> dict[str, Any]:
    if not SETTINGS.allow_write:
        raise PolicyError("Writes disabled")
    path = _sandbox_file(src, must_exist=True)
    return adapters.restore(get(name), path)


def _migrate(operations: list[dict[str, Any]], apply: bool, name: str, confirm: bool) -> dict[str, Any]:
    stmts = []
    for op in operations:
        kind = op.get("op")
        if kind == "create_table":
            table = _ident(op["table"])
            cols = []
            for c in op.get("columns") or []:
                cols.append(f'"{_ident(c["name"])}" {c.get("type") or "TEXT"}')
            stmts.append(f'CREATE TABLE "{table}" ({", ".join(cols)})')
        elif kind == "add_column":
            stmts.append(
                f'ALTER TABLE "{_ident(op["table"])}" ADD COLUMN "{_ident(op["column"])}" {op.get("type") or "TEXT"}'
            )
        elif kind == "add_index":
            cols = ", ".join(f'"{_ident(c)}"' for c in op.get("columns") or [])
            iname = _ident(op.get("name") or f"ix_{op['table']}")
            stmts.append(f'CREATE INDEX "{iname}" ON "{_ident(op["table"])}" ({cols})')
        else:
            raise ValidationError(f"Unknown migration op {kind}")
    sql = ";\n".join(stmts) + ";"
    if not apply:
        return {"sql": sql, "applied": False}
    if not SETTINGS.allow_ddl:
        raise PolicyError("Applying migrations needs DB_MCP_ALLOW_DDL=1")
    info = get(name)
    with info.engine.begin() as conn:
        for s in stmts:
            enforce(s, confirm=confirm)
            conn.execute(text(s))
    return {"sql": sql, "applied": True}


def _diagnose(name: str) -> dict[str, Any]:
    info = get(name)
    insp = inspector(name)
    tables = insp.get_table_names()
    counts = {}
    with info.engine.connect() as conn:
        for t in tables[:30]:
            try:
                counts[t] = conn.execute(text(f'SELECT COUNT(*) FROM "{t}"')).scalar()
            except Exception as exc:
                counts[t] = str(exc)
        extra: dict[str, Any] = {}
        if info.dialect == "sqlite":
            extra["compile_options"] = [
                r[0] for r in conn.execute(text("PRAGMA compile_options")).fetchall()
            ][:40]
            extra["integrity"] = conn.execute(text("PRAGMA integrity_check")).scalar()
    return {
        "dialect": info.dialect,
        "url": __import__("database_mcp.redact", fromlist=["redact_url"]).redact_url(info.url),
        "tables": tables,
        "counts": counts,
        "extra": extra if info.dialect == "sqlite" else {},
        "policy": {
            "allow_write": SETTINGS.allow_write,
            "allow_ddl": SETTINGS.allow_ddl,
            "allow_destructive": SETTINGS.allow_destructive,
        },
    }


def _compare(name_a: str, name_b: str) -> dict[str, Any]:
    a = set(inspector(name_a).get_table_names())
    b = set(inspector(name_b).get_table_names())
    only_a, only_b = sorted(a - b), sorted(b - a)
    shared = sorted(a & b)
    col_diff = []
    ia, ib = inspector(name_a), inspector(name_b)
    for t in shared:
        ca = {c["name"] for c in ia.get_columns(t)}
        cb = {c["name"] for c in ib.get_columns(t)}
        if ca != cb:
            col_diff.append({"table": t, "only_a": sorted(ca - cb), "only_b": sorted(cb - ca)})
    return {"only_in_a": only_a, "only_in_b": only_b, "column_diffs": col_diff}


def _sql_analyze(sql: str) -> dict[str, Any]:
    clf = classify(sql)
    return {
        "kind": clf.kind,
        "first_keyword": clf.first_keyword,
        "statement_count": len(clf.statements),
        "statements": clf.statements,
        "formatted": format_sql(sql),
    }
