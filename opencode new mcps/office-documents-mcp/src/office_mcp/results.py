"""Standard tool results."""

from __future__ import annotations

import time
from typing import Any

from office_mcp.errors import OfficeError


def ok(data: Any, warnings: list[str] | None = None, **meta: Any) -> dict[str, Any]:
    return {
        "ok": True,
        "data": data,
        "warnings": warnings or [],
        "meta": meta,
    }


def fail(exc: BaseException) -> dict[str, Any]:
    if isinstance(exc, OfficeError):
        return {"ok": False, "error": exc.to_dict(), "data": None, "warnings": []}
    return {
        "ok": False,
        "error": {
            "code": "INTERNAL",
            "message": str(exc) or exc.__class__.__name__,
            "details": {"type": type(exc).__name__},
        },
        "data": None,
        "warnings": [],
    }


class Timer:
    def __init__(self) -> None:
        self._t = time.perf_counter()

    def ms(self) -> int:
        return int((time.perf_counter() - self._t) * 1000)
