"""Resumable / checkpointed processing (requirement 34).

Long operations over huge documents record per-unit (per-page / per-chunk /
per-file) status into a durable JSON *checkpoint*. If an interruption occurs
the operation can restart and skip already-completed units instead of
reprocessing everything.

Unit status vocabulary: ``pending | processing | completed | failed | retry``.
After the batch, units are *validated* and marked ``validated``.
"""
from __future__ import annotations

import json
import os
import time
from pathlib import Path
from typing import Callable, Iterable, Optional


class Checkpoint:
    def __init__(self, path: str | Path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.data: dict = {"meta": {}, "units": {}, "updated": None}
        self._load()

    def _load(self):
        if self.path.exists():
            try:
                self.data = json.loads(self.path.read_text())
            except Exception:
                self.data = {"meta": {}, "units": {}, "updated": None}

    def _save(self):
        self.data["updated"] = time.time()
        tmp = self.path.with_suffix(".tmp")
        tmp.write_text(json.dumps(self.data, indent=2))
        os.replace(tmp, self.path)

    # -- status query helpers ------------------------------------------------
    def unit_status(self, unit_id: str) -> str:
        return self.data["units"].get(unit_id, {}).get("status", "pending")

    def incomplete(self) -> list[str]:
        return [u for u, s in self.data["units"].items()
                if s.get("status") in ("pending", "failed", "retry")]

    def completed(self) -> list[str]:
        return [u for u, s in self.data["units"].items()
                if s.get("status") in ("completed", "validated")]

    def set_status(self, unit_id: str, status: str, **extra):
        rec = self.data["units"].setdefault(unit_id, {})
        rec["status"] = status
        rec.update(extra)
        rec["updated"] = time.time()
        self._save()

    # -- runner ---------------------------------------------------------------
    def run(self, units: Iterable[str],
            fn: Callable[[str], None],
            only_pending: bool = True) -> dict:
        """Execute ``fn`` over units, skipping completed ones unless requested.

        Returns summary counts.
        """
        summary = {"completed": 0, "failed": 0, "skipped": 0}
        for unit in units:
            if only_pending and self.unit_status(unit) in ("completed", "validated"):
                summary["skipped"] += 1
                continue
            self.set_status(unit, "processing")
            try:
                fn(unit)
                self.set_status(unit, "completed")
                summary["completed"] += 1
            except Exception as exc:  # noqa: BLE001
                self.set_status(unit, "failed", error=str(exc))
                summary["failed"] += 1
        return summary
