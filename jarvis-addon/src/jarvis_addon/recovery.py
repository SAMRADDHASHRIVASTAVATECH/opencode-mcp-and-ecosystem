"""Failure detection / classification / recovery reference logic (section 3, 19).

Defines failure classes and a strategy registry used to pick a recovery action.
This is policy- and host-agnostic plumbing; actual execution is delegated to
the host.
"""
from __future__ import annotations

import time
from dataclasses import dataclass, field, asdict

FAILURE_CLASSES = [
    "ENVIRONMENT", "DEPENDENCY", "TRANSIENT", "RESOURCE", "LOGIC",
    "TOOL", "AUTH", "NETWORK", "CONFIG", "UNKNOWN",
]

RECOVERY_STRATEGIES = [
    "retry", "alternative_strategy", "alternative_tool", "alternative_skill",
    "fallback", "rollback", "escalate", "halt",
]


@dataclass
class Failure:
    operation: str
    message: str
    failure_class: str = "UNKNOWN"
    source: str = ""
    evidence: str = ""
    severity: str = "medium"         # low | medium | high | critical
    timestamp: str = ""

    def to_dict(self):
        return asdict(self)


@dataclass
class RecoveryPlan:
    failure: Failure
    diagnosis: str = ""
    strategy: str = "retry"
    retry_limit: int = 3
    attempts: int = 0
    alternative: str = ""
    rollback_action: str = ""
    verification: dict = field(default_factory=dict)
    termination: str = ""
    escalate_after: int = 5
    notes: list = field(default_factory=list)

    def to_dict(self):
        return asdict(self)


def classify(message: str, source: str = "") -> str:
    m = (message or "").lower()
    if any(k in m for k in ("permission", "denied", "auth", "unauthorized",
                            "forbidden")):
        return "AUTH"
    if any(k in m for k in ("timeout", "connection", "network", "refused",
                            "reset", "dns")):
        return "NETWORK"
    if any(k in m for k in ("not found", "module", "no such", "import",
                            "dependency", "missing", "package")):
        return "DEPENDENCY"
    if any(k in m for k in ("oom", "memory", "vram", "disk full", "no space",
                            "resource")):
        return "RESOURCE"
    if any(k in m for k in ("tool", "mcp", "command failed", "exit code")):
        return "TOOL"
    if any(k in m for k in ("config", "invalid value", "schema")):
        return "CONFIG"
    if any(k in m for k in ("unexpected", "bug", "traceback", "exception",
                            "assert")):
        return "LOGIC"
    return "UNKNOWN"


def choose_strategy(failure: Failure, attempt: int = 0) -> RecoveryPlan:
    plan = RecoveryPlan(failure=failure)
    plan.attempts = attempt
    cls = failure.failure_class
    if cls == "NETWORK":
        plan.strategy = "retry"
        plan.retry_limit = 4
        plan.notes.append("transient network: retry with backoff")
    elif cls == "AUTH":
        plan.strategy = "escalate"
        plan.escalate_after = 1
        plan.notes.append("never retry auth silently; escalate for approval")
    elif cls == "RESOURCE":
        plan.strategy = "alternative_strategy"
        plan.notes.append("reduce resource use / fall back to lighter approach")
    elif cls == "DEPENDENCY":
        plan.strategy = "alternative_tool"
        plan.notes.append("dependency missing: find alternative or repair dep")
    elif cls == "CONFIG":
        plan.strategy = "rollback"
        plan.notes.append("config invalid: rollback to last known-good config")
    elif cls == "TOOL":
        plan.strategy = "alternative_tool"
        plan.retry_limit = 1
        plan.notes.append("tool failed: retry once then switch tool")
    elif cls == "LOGIC":
        plan.strategy = "retry"
        plan.notes.append("logic failure: verify assumption, bounded retry")
    else:
        plan.strategy = "retry"
    if attempt >= plan.retry_limit and plan.strategy != "escalate":
        plan.strategy = "escalate"
    plan.termination = "halt after escalation unless explicitly approved"
    plan.diagnosis = f"class={cls} -> strategy={plan.strategy}"
    return plan
