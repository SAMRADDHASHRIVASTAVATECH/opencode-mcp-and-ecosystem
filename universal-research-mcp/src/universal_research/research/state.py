"""Research state & job manager (#41-43, #57 research_status/cancel_research).

Tracks every research task through a lifecycle, stores its memory (queries,
sources, claims, gaps) and exposes status/cancellation. Thread-safe.
"""
from __future__ import annotations

import threading
import time
import uuid
from dataclasses import dataclass, field
from typing import Optional

from ..models import ResearchStates, new_id


@dataclass
class ResearchTask:
    id: str
    objective: str
    state: str = ResearchStates.CREATED
    created: float = field(default_factory=time.time)
    updated: float = field(default_factory=time.time)
    plan: list = field(default_factory=list)
    memory: dict = field(default_factory=dict)
    result: dict = field(default_factory=dict)
    error: str = ""
    cancel_flag: bool = False
    stopping_reason: str = ""
    budget: dict = field(default_factory=dict)

    def set_state(self, state: str):
        self.state = state
        self.updated = time.time()

    def to_dict(self) -> dict:
        return {"id": self.id, "objective": self.objective, "state": self.state,
                "created": self.created, "updated": self.updated,
                "stopping_reason": self.stopping_reason,
                "error": self.error, "has_result": bool(self.result),
                "n_plan_steps": len(self.plan),
                "memory_summary": {k: len(v) if isinstance(v, list) else v
                                   for k, v in self.memory.items()
                                   if isinstance(v, list)},
                "result_summary": self.result.get("summary", "") if self.result else ""}


class ResearchManager:
    """Holds all research tasks and their shared KnowledgeGraph."""

    def __init__(self):
        self._tasks: dict[str, ResearchTask] = {}
        self._lock = threading.Lock()

    def create(self, objective: str, budget: Optional[dict] = None) -> ResearchTask:
        with self._lock:
            task = ResearchTask(id=new_id("research"), objective=objective,
                                budget=budget or {})
            task.set_state(ResearchStates.PLANNING)
            self._tasks[task.id] = task
            return task

    def get(self, task_id: str) -> Optional[ResearchTask]:
        return self._tasks.get(task_id)

    def update(self, task_id: str, **fields) -> Optional[ResearchTask]:
        t = self._tasks.get(task_id)
        if not t:
            return None
        for k, v in fields.items():
            if hasattr(t, k):
                setattr(t, k, v)
        t.updated = time.time()
        return t

    def set_state(self, task_id: str, state: str):
        t = self._tasks.get(task_id)
        if t:
            t.set_state(state)

    def request_cancel(self, task_id: str) -> bool:
        t = self._tasks.get(task_id)
        if not t:
            return False
        t.cancel_flag = True
        t.set_state(ResearchStates.CANCELLED)
        return True

    def list_tasks(self) -> list[dict]:
        return [t.to_dict() for t in
                sorted(self._tasks.values(), key=lambda x: -x.created)]

    def memory(self, task_id: str) -> dict:
        t = self._tasks.get(task_id)
        return t.memory if t else {}

    def record(self, task_id: str, kind: str, item):
        """Store into research memory lists (#39): queries, sources, claims,
        evidence, terminology, gaps, errors."""
        t = self._tasks.get(task_id)
        if not t:
            return
        mem = t.memory
        mem.setdefault(kind, [])
        if isinstance(item, dict):
            # avoid exact dupes by identity key
            key = item.get("id") or item.get("url") or item.get("text") or str(item)
            for existing in mem[kind]:
                ek = existing.get("id") or existing.get("url") or existing.get("text")
                if ek == key:
                    return
            mem[kind].append(item)
        else:
            if item not in mem[kind]:
                mem[kind].append(item)
        t.updated = time.time()
