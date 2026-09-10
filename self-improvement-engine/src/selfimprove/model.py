"""Experience-memory data model.

Deterministic knowledge engine - no model/safeguard modification. Lessons are
versioned, validated, reversible knowledge records. Statuses and confidence are
derived by rules, not fabricated.
"""
from __future__ import annotations

from dataclasses import dataclass, field, asdict
import time


def now() -> float:
    return time.time()


# Lesson lifecycle states.
ACTIVE = "active"
STRONG = "strong"        # repeatedly validated -> promoted long-term lesson
OBSOLETE = "obsolete"    # superseded/contradicted; not retrieved by default
ARCHIVED = "archived"    # soft-deleted but reversible

# Where a lesson came from.
SOURCE_MISTAKE = "mistake"
SOURCE_SUCCESS = "success"
SOURCE_CORRECTION = "user_correction"
SOURCE_DISCOVERY = "discovery"
SOURCE_PATTERN = "pattern"
SOURCE_REFLECTION = "reflection"
SOURCES = (SOURCE_MISTAKE, SOURCE_SUCCESS, SOURCE_CORRECTION, SOURCE_DISCOVERY,
           SOURCE_PATTERN, SOURCE_REFLECTION)

# Outcome of an experience.
OUTCOME_OK = "success"
OUTCOME_FAIL = "failure"


def _sanitize_text(s: str) -> str:
    return " ".join(str(s).strip().split())


@dataclass
class Lesson:
    """A single durable, retrievable lesson."""
    id: str = ""                         # unique id (filled by engine)
    statement: str = ""                  # core lesson text (normalized identity)
    category: str = "general"
    detail: str = ""                     # fuller explanation / how to apply
    tags: list = field(default_factory=list)
    source: str = SOURCE_REFLECTION
    context: str = ""                    # what situation it applies to
    confidence: float = 0.5
    times_seen: int = 1
    times_validated: int = 0
    status: str = ACTIVE                 # active | strong | obsolete | archived
    created: float = field(default_factory=now)
    updated: float = field(default_factory=now)
    version: int = 1
    # safety/ownership metadata (policy guardrail)
    protected: bool = False              # True => never auto-consolidated/removed
    author: str = "engine"
    meta: dict = field(default_factory=dict)

    def dict(self) -> dict:
        return asdict(self)

    @property
    def identity(self) -> str:
        """Normalized identity used to detect duplicate lessons."""
        return _sanitize_text(self.statement).lower()


@dataclass
class Experience:
    """A raw recorded event/action with outcome, before it becomes a lesson."""
    action: str
    outcome: str                        # success | failure
    id: str = ""
    detail: str = ""
    error: str = ""
    fix: str = ""
    verdict: str = ""                   # why it worked/failed (analysis)
    category: str = "general"
    tags: list = field(default_factory=list)
    source: str = SOURCE_PATTERN
    ts: float = field(default_factory=now)
    lesson_id: str = ""                 # linked lesson if one was derived

    def dict(self) -> dict:
        return asdict(self)
