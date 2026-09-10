"""Event system + realtime event stream (spec sections 23, 24).

An in-process pub/sub bus emits typed events. A realtime transport (WebSocket/SSE
on Android, or an MCP/stdio adapter) can subscribe. The bus is deliberately
push-based - no aggressive polling. Out-of-process delivery is handled by the MCP
layer over its chosen transport.
"""
from __future__ import annotations

import json
import time
import threading
from collections import deque
from typing import Callable

EVENT_TYPES = {
    "incoming_call", "outgoing_call", "ringing", "answered", "connected",
    "disconnected", "missed", "rejected", "voicemail", "transfer",
    "ai_session_started", "ai_session_ended", "transcription_update",
    "ai_response_started", "ai_response_completed", "state_changed",
    "provider_disconnected", "error", "emergency_stop", "capability_changed",
}


class EventBus:
    def __init__(self, capacity: int = 500):
        self._subs: list[Callable] = []
        self._lock = threading.Lock()
        self._history: deque = deque(maxlen=capacity)
        self._counter = 0

    def subscribe(self, fn: Callable):
        with self._lock:
            self._subs.append(fn)
            return fn

    def unsubscribe(self, fn: Callable):
        with self._lock:
            if fn in self._subs:
                self._subs.remove(fn)

    def publish(self, event_type: str, **payload):
        if event_type not in EVENT_TYPES:
            event_type = "state_changed"
        ev = {"type": event_type, "ts": time.time(),
              "seq": self._next_seq(), "payload": payload}
        with self._lock:
            self._history.append(ev)
            subs = list(self._subs)
        for s in subs:
            try:
                s(ev)
            except Exception:
                pass
        return ev

    def _next_seq(self):
        self._counter += 1
        return self._counter

    def recent(self, types=None, limit=100):
        out = list(self._history)
        if types:
            out = [e for e in out if e["type"] in types]
        return out[-limit:]
