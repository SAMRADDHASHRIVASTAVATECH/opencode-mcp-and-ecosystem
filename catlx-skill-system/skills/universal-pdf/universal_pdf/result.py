"""Outcome model used by every skill.

Each operation returns an :class:`Outcome` that carries:
  * whether it succeeded or degraded,
  * provenance (see :mod:`universal_pdf.core.provenance`),
  * validation checks and results,
  * messages / warnings that must be surfaced to the caller.

Keeping this uniform makes individual skills and the orchestrator trivial to
reason about without trusting the model's memory.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Optional


@dataclass
class ValidationCheck:
    """A single named post-operation validation check."""
    name: str
    expected: Any
    actual: Any
    passed: bool
    detail: str = ""

    def to_dict(self) -> dict:
        return {"name": self.name, "expected": self.expected,
                "actual": self.actual, "passed": self.passed,
                "detail": self.detail}


@dataclass
class Outcome:
    """Result of one skill / operation invocation."""
    skill: str
    ok: bool = False              # fully succeeded
    degraded: bool = False        # succeeded with a documented fallback
    status: str = "completed"     # completed | degraded | failed | partial
    output_path: Optional[str] = None
    data: Any = None
    checks: list[ValidationCheck] = field(default_factory=list)
    messages: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    provenance: dict = field(default_factory=dict)   # doc/page/chunk refs
    meta: dict = field(default_factory=dict)

    def check(self, name: str, expected: Any, actual: Any,
              passed: bool, detail: str = "") -> "Outcome":
        self.checks.append(ValidationCheck(name, expected, actual, passed, detail))
        return self

    def all_checks_passed(self) -> bool:
        return bool(self.checks) and all(c.passed for c in self.checks)

    def to_dict(self) -> dict:
        return {
            "skill": self.skill,
            "ok": self.ok,
            "degraded": self.degraded,
            "status": self.status,
            "output_path": self.output_path,
            "checks": [c.to_dict() for c in self.checks],
            "messages": self.messages,
            "warnings": self.warnings,
            "provenance": self.provenance,
            "meta": self.meta,
        }

    def __repr__(self) -> str:  # pragma: no cover
        return (f"<Outcome skill={self.skill} status={self.status} "
                f"checks_ok={self.all_checks_passed()}>")
