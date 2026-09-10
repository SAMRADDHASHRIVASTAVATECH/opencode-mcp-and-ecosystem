"""Event engine (spec section 12, 13).

Typed pub/sub bus with priorities. High-priority events (new speech, interrupt)
can supersede stale low-priority reasoning via the interruption manager.
"""
from __future__ import annotations

import threading
import time
from collections import deque
from typing import Callable

EVENT_TYPES = {
    "audio.started", "audio.stopped", "speech.detected", "transcript.partial",
    "transcript.final", "question.detected", "screen.changed", "window.changed",
    "task.detected", "tool.started", "tool.completed", "tool.failed",
    "mode.changed", "session.started", "session.paused", "session.resumed",
    "session.ended", "model.changed", "interruption", "generation.started",
    "generation.completed", "generation.cancelled", "emergency_stop",
    "error", "health", "state.changed",
}

# Priority: higher interrupts lower. Default 5. Interrupts = 100.
PRIORITY = {e: 5 for e in EVENT_TYPES}
PRIORITY["interruption"] = 100
PRIORITY["speech.detected"] = 60
PRIORITY["generation.cancelled"] = 90
PRIORITY["emergency_stop"] = 200
PRIORITY["mode.changed"] = 40


class Event:
    __slots__ = ("type", "ts", "seq", "priority", "payload")

    def __init__(self, type_, priority, seq, payload):
        self.type = type_
        self.ts = time.time()
        self.seq = seq
        self.priority = priority
        self.payload = payload

    def dict(self):
        return {"type": self.type, "ts": self.ts, "seq": self.seq,
                "priority": self.priority, "payload": self.payload}


class EventBus:
    def __init__(self, capacity=2000):
        self._lock = threading.Lock()
        self._subs = []
        self._history = deque(maxlen=capacity)
        self._seq = 0

    def subscribe(self, fn: Callable):
        with self._lock:
            self._subs.append(fn)
        return fn

    def unsubscribe(self, fn):
        with self._lock:
            if fn in self._subs:
                self._subs.remove(fn)

    def publish(self, type_, payload=None, priority=None):
        if type_ not in EVENT_TYPES:
            type_ = "state.changed"
        pri = priority if priority is not None else PRIORITY.get(type_, 5)
        with self._lock:
            self._seq += 1
            ev = Event(type_, pri, self._seq, payload or {})
            self._history.append(ev)
            subs = list(self._subs)
        for s in subs:
            try:
                s(ev)
            except Exception:
                pass
        return ev

    def recent(self, types=None, limit=200):
        out = list(self._history)
        if types:
            out = [e for e in out if e["type"] in types]
        return [e.dict() for e in out[-limit:]]
