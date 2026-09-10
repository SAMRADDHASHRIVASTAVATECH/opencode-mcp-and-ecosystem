"""Structured logging for the Android Control system.

Each record carries: timestamp, device_id, operation, command, result,
duration, verification, error, recovery. Normal mode stays concise; debug mode
emits command detail. Secrets are never logged.
"""
from __future__ import annotations

import json
import re
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

_SECRET_RE = re.compile(
    r"(?i)(pairing|code|token|apikey|api_key|secret|password|passwd|authorization)"
    r"[\"':=\s]*([A-Za-z0-9._/\-+]{4,})")


def redact(text: str) -> str:
    """Scrub obvious secrets from a string before it is logged."""
    if not text:
        return text
    return _SECRET_RE.sub(lambda m: m.group(1) + "=***REDACTED***", text)


class OperationLog:
    """Collects structured log records for a run and flushes to a file."""

    def __init__(self, log_dir: str, debug: bool = False):
        self.debug = debug
        self._records: list = []
        self._path = None
        if log_dir:
            p = Path(log_dir)
            p.mkdir(parents=True, exist_ok=True)
            stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
            self._path = p / f"android_control_{stamp}.jsonl"

    def record(self, *, device_id: str = "", operation: str = "",
               command: str = "", result: str = "", duration_ms: float = 0.0,
               verification: str = "", error: str = "", recovery: str = ""):
        rec = {
            "ts": datetime.now(timezone.utc).isoformat(),
            "device_id": device_id,
            "operation": operation,
            "command": redact(command) if command else "",
            "result": result,
            "duration_ms": round(duration_ms, 1),
            "verification": verification,
            "error": redact(str(error)) if error else "",
            "recovery": recovery,
        }
        self._records.append(rec)
        if self._path is not None:
            try:
                with self._path.open("a", encoding="utf-8") as fh:
                    fh.write(json.dumps(rec) + "\n")
            except OSError:
                pass

    def records(self) -> list:
        return self._records

    @property
    def path(self):
        return self._path


class _Reporter:
    """Tiny helper: captures timed, bounded logs for a top-level operation."""

    def __init__(self, log: OperationLog, operation: str):
        self.log = log
        self.operation = operation
        self._t = time.monotonic()

    def done(self, device_id: str = "", result: str = "ok",
             command: str = "", verification: str = "", error: str = "",
             recovery: str = ""):
        self.log.record(device_id=device_id, operation=self.operation,
                        command=command, result=result,
                        duration_ms=(time.monotonic() - self._t) * 1000.0,
                        verification=verification, error=error,
                        recovery=recovery)
