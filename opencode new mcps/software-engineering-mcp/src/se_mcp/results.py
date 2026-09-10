from __future__ import annotations

from typing import Any

from se_mcp.errors import SEError


def ok(data: Any, warnings: list[str] | None = None, **meta: Any) -> dict[str, Any]:
    return {"ok": True, "data": data, "warnings": warnings or [], "meta": meta}


def fail(exc: BaseException) -> dict[str, Any]:
    if isinstance(exc, SEError):
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
