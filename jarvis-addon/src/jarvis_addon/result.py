"""Universal result + verification + evidence contracts.

Implements section 17 (Universal Result), section 18 (Verification Contract)
and the reliability principle from section 17: an action is never considered
successful merely because a tool returned; success requires observed evidence.
"""
from __future__ import annotations

import enum
import time
from dataclasses import dataclass, field, asdict


class ResultStatus(str, enum.Enum):
    SUCCESS = "success"
    PARTIAL = "partial"
    FAILED = "failed"
    BLOCKED = "blocked"


@dataclass
class Evidence:
    source: str
    claim: str
    method: str = "observed"        # observed | asserted | verified | predicted
    confidence: float = 1.0
    timestamp: str = ""

    def to_dict(self):
        return asdict(self)


@dataclass
class Verification:
    expected_state: dict = field(default_factory=dict)
    observed_state: dict = field(default_factory=dict)
    method: str = ""
    passed: bool = False
    evidence: list = field(default_factory=list)
    confidence: float = 0.0
    timestamp: str = ""

    def to_dict(self):
        return asdict(self)


@dataclass
class UniversalResult:
    status: str = ResultStatus.SUCCESS.value
    result: dict = field(default_factory=dict)
    artifacts: list = field(default_factory=list)
    verification: dict = field(default_factory=dict)
    evidence: list = field(default_factory=list)
    warnings: list = field(default_factory=list)
    errors: list = field(default_factory=list)
    next_action: str | None = None
    timestamp: str = ""

    def success(self):
        self.status = ResultStatus.SUCCESS.value
        return self

    def with_timestamp(self):
        self.timestamp = self.timestamp or time.strftime("%Y-%m-%dT%H:%M:%SZ")
        return self

    def to_dict(self):
        return {
            "status": self.status,
            "result": self.result,
            "artifacts": self.artifacts,
            "verification": self.verification,
            "evidence": [e.to_dict() if hasattr(e, "to_dict") else e
                         for e in self.evidence],
            "warnings": self.warnings,
            "errors": self.errors,
            "next_action": self.next_action,
            "timestamp": self.timestamp,
        }

    @classmethod
    def failed(cls, errors, warnings=None):
        r = cls(status=ResultStatus.FAILED.value, errors=errors,
                warnings=warnings or [])
        return r.with_timestamp()

    @classmethod
    def ok(cls, result=None, artifacts=None, verification=None, evidence=None):
        r = cls(result=result or {}, artifacts=artifacts or [],
                verification=verification or {},
                evidence=evidence or [])
        return r.with_timestamp()
