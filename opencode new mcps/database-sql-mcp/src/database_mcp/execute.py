"""Run SQL with limits and truncation."""

from __future__ import annotations

from typing import Any

from sqlalchemy import text

from database_mcp.config import SETTINGS
from database_mcp.manager import ConnectionInfo


def run_sql(
    info: ConnectionInfo,
    sql: str,
    params: dict[str, Any] | None = None,
    limit: int | None = None,
    fetch: bool = True,
) -> dict[str, Any]:
    cap = min(limit or SETTINGS.default_limit, SETTINGS.max_rows)
    with info.engine.connect() as conn:
        result = conn.execute(text(sql), params or {})
        if not fetch or result.returns_rows is False:
            try:
                conn.commit()
            except Exception:
                pass
            return {
                "rowcount": result.rowcount,
                "returns_rows": False,
            }
        keys = list(result.keys())
        rows = []
        truncated = False
        for i, row in enumerate(result):
            if i >= cap:
                truncated = True
                break
            mapping = row._mapping
            item = {}
            for k in keys:
                item[k] = _cell(mapping[k])
            rows.append(item)
        try:
            conn.commit()
        except Exception:
            pass
        return {
            "columns": keys,
            "rows": rows,
            "rowcount": len(rows),
            "truncated": truncated,
            "limit": cap,
        }


def _cell(v: Any) -> Any:
    if v is None:
        return None
    if isinstance(v, (int, float, bool)):
        return v
    if isinstance(v, (bytes, memoryview)):
        return f"<bytes {len(v)}>"
    s = v if isinstance(v, str) else str(v)
    if len(s) > SETTINGS.max_cell_chars:
        return s[: SETTINGS.max_cell_chars] + "…"
    return s
