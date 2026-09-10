from __future__ import annotations

from typing import Any

from database_mcp.errors import DBError


def ok(data: Any, **meta: Any) -> dict[str, Any]:
    return {"ok": True, "data": data, "warnings": [], "meta": meta}


def fail(exc: BaseException) -> dict[str, Any]:
    if isinstance(exc, DBError):
        return {"ok": False, "error": exc.to_dict(), "data": None, "warnings": []}
    return {
        "ok": False,
        "error": {"code": "INTERNAL", "message": str(exc), "details": {"type": type(exc).__name__}},
        "data": None,
        "warnings": [],
    }


def run(fn, **kw):
    try:
        data = fn(**kw)
        if isinstance(data, dict) and "ok" in data:
            return data
        return ok(data)
    except Exception as exc:
        return fail(exc)
