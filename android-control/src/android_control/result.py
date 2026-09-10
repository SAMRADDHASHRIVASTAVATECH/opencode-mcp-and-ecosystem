"""Structured result envelopes and status vocabulary.

Every completed operation returns one of these statuses (never collapses
multi-device results into a single ambiguous status).
"""
from __future__ import annotations

import time
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional

# Canonical status vocabulary (§42)
SUCCESS = "SUCCESS"
PARTIAL_SUCCESS = "PARTIAL_SUCCESS"
FAILED = "FAILED"
OFFLINE = "OFFLINE"
REQUIRES_AUTHORIZATION = "REQUIRES_AUTHORIZATION"
UNSUPPORTED = "UNSUPPORTED"
TIMEOUT = "TIMEOUT"
RUNNING = "RUNNING"
CANCELLED = "CANCELLED"
SKIPPED = "SKIPPED"

_ALL_STATUS = {SUCCESS, PARTIAL_SUCCESS, FAILED, OFFLINE,
               REQUIRES_AUTHORIZATION, UNSUPPORTED, TIMEOUT, RUNNING,
               CANCELLED, SKIPPED}


def is_status(value: str) -> bool:
    return value in _ALL_STATUS


@dataclass
class DeviceOutcome:
    """One device's result inside a multi-device result set."""
    device_id: str
    serial: str = ""
    model: str = ""
    status: str = SUCCESS
    data: Any = None
    error: str = ""
    duration_ms: float = 0.0
    verification: str = ""
    recovery: str = ""

    def to_dict(self) -> dict:
        d = asdict(self)
        if isinstance(d.get("data"), bytes):
            d["data"] = f"<bytes:{len(d['data'])}>"
        return d


@dataclass
class ActionResult:
    """Result of a single (possibly multi-device) operation."""
    operation: str
    status: str = SUCCESS
    data: Any = None
    error: str = ""
    # per-device outcomes for multi-device ops
    devices: List[DeviceOutcome] = field(default_factory=list)
    duration_ms: float = 0.0
    note: str = ""

    def single_outcome(self) -> Optional[DeviceOutcome]:
        return self.devices[0] if len(self.devices) == 1 else None

    def aggregate_from_outcomes(self):
        """Derive top-level status from per-device outcomes."""
        if not self.devices:
            return
        statuses = {d.status for d in self.devices}
        if statuses == {SUCCESS}:
            self.status = SUCCESS
        elif FAILED in statuses and statuses - {FAILED}:
            self.status = PARTIAL_SUCCESS
        elif statuses == {FAILED}:
            self.status = FAILED
        elif OFFLINE in statuses and statuses - {OFFLINE}:
            self.status = PARTIAL_SUCCESS
        elif OFFLINE in statuses:
            self.status = OFFLINE
        elif REQUIRES_AUTHORIZATION in statuses:
            self.status = REQUIRES_AUTHORIZATION
        elif TIMEOUT in statuses:
            self.status = TIMEOUT
        elif UNSUPPORTED in statuses:
            self.status = UNSUPPORTED
        else:
            self.status = FAILED

    def to_dict(self) -> dict:
        return {
            "operation": self.operation,
            "status": self.status,
            "error": self.error,
            "note": self.note,
            "duration_ms": round(self.duration_ms, 1),
            "devices": [d.to_dict() for d in self.devices],
            "data": self.data,
        }


class ResultBuilder:
    """Helper to build single- and multi-device action results."""

    def __init__(self, operation: str):
        self.operation = operation
        self._t = time.monotonic()
        self._single_data = None
        self._outcomes: List[DeviceOutcome] = []
        self._error = ""
        self._note = ""

    def single(self, status: str = SUCCESS, data: Any = None,
               error: str = "") -> ActionResult:
        r = ActionResult(self.operation, status=status, data=data, error=error)
        r.duration_ms = (time.monotonic() - self._t) * 1000.0
        return r

    def per_device(self, device_id: str, *, serial: str = "", model: str = "",
                   status: str = SUCCESS, data: Any = None, error: str = "",
                   verification: str = "", recovery: str = "") -> None:
        self._outcomes.append(DeviceOutcome(
            device_id=device_id, serial=serial, model=model, status=status,
            data=data, error=error, verification=verification,
            recovery=recovery,
            duration_ms=(time.monotonic() - self._t) * 1000.0))

    def build(self) -> ActionResult:
        r = ActionResult(self.operation, devices=self._outcomes,
                         error=self._error, note=self._note)
        r.duration_ms = (time.monotonic() - self._t) * 1000.0
        r.aggregate_from_outcomes()
        return r
