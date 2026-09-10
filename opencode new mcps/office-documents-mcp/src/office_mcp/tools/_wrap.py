from __future__ import annotations

from collections.abc import Callable
from typing import Any

from office_mcp.errors import OfficeError
from office_mcp.results import Timer, fail, ok


def run(fn: Callable[..., Any], **kwargs: Any) -> dict[str, Any]:
    timer = Timer()
    try:
        data = fn(**kwargs)
        if isinstance(data, dict) and "ok" in data:
            data.setdefault("meta", {})
            data["meta"]["elapsed_ms"] = timer.ms()
            return data
        return ok(data, elapsed_ms=timer.ms())
    except OfficeError as exc:
        result = fail(exc)
        result["meta"] = {"elapsed_ms": timer.ms()}
        return result
    except Exception as exc:
        result = fail(exc)
        result["meta"] = {"elapsed_ms": timer.ms()}
        return result
