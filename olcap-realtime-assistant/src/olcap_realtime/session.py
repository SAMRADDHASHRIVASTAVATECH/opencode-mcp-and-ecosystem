"""Persistent session manager (spec sections 24, 46).

A session bundles one mode's state: transcript, summary, actions, events and
provenance (audio/screen/stt/reasoning/tts providers). Survives restarts.
Retention is configurable; session.delete/export provided.
"""
from __future__ import annotations

import json
import threading
import time

from .context import ContextEngine
from .events import EventBus
from .store import Store


def new_id(prefix="sess"):
    return f"{prefix}_{int(time.time()*1000)}_{id(object()) & 0xFFFF}"


class SessionManager:
    def __init__(self, config, store: Store, ctx: ContextEngine, bus: EventBus):
        self.cfg = config
        self.store = store
        self.ctx = ctx
        self.bus = bus
        self._lock = threading.Lock()
        self._active: dict[str, dict] = {}   # session_id -> live record

    # ---- lifecycle ---- #
    def create(self, mode: str, provenance=None) -> dict:
        sid = new_id()
        now = time.time()
        rec = {
            "session_id": sid, "mode": mode, "start_time": now, "end_time": None,
            "status": "active",
            "provenance": provenance or {},
            "transcript": [], "summary": "", "actions": [], "evaluation": None,
        }
        self.store.put_session(rec)
        with self._lock:
            self._active[sid] = rec
        cs = self.ctx.new(sid, mode)
        cs.mode = mode
        self.bus.publish("session.started", {"session_id": sid, "mode": mode})
        return self.get(sid)

    def get(self, session_id: str) -> dict | None:
        with self._lock:
            rec = self._active.get(session_id)
        if rec:
            return {**rec, "transcript": rec["transcript"],
                    "summary": rec.get("summary", "")}
        return self.store.get_session(session_id)

    def _touch(self, session_id, **fields):
        with self._lock:
            rec = self._active.get(session_id)
        if rec:
            rec.update(fields)
            self.store.put_session(rec)
        else:
            stored = self.store.get_session(session_id)
            if stored:
                stored.update(fields)
                self.store.put_session(stored)

    def pause(self, session_id: str):
        rec = self.get(session_id)
        if not rec:
            raise KeyError(f"no session {session_id}")
        rec = dict(rec); rec["status"] = "paused"
        self._touch(session_id, **{"status": "paused"})
        self.bus.publish("session.paused", {"session_id": session_id})
        return self.get(session_id)

    def resume(self, session_id: str):
        rec = self.get(session_id)
        if not rec:
            raise KeyError(f"no session {session_id}")
        self._touch(session_id, **{"status": "active"})
        self.bus.publish("session.resumed", {"session_id": session_id})
        return self.get(session_id)

    def end(self, session_id: str, summary: str = "", evaluation=None):
        rec = self.get(session_id)
        if not rec:
            raise KeyError(f"no session {session_id}")
        now = time.time()
        self._touch(session_id, end_time=now, status="ended", summary=summary or
                    rec.get("summary", ""), evaluation=evaluation)
        self.ctx.drop(session_id)
        self.bus.publish("session.ended", {"session_id": session_id})
        return self.get(session_id)

    def summarize(self, session_id: str, text: str):
        rec = self.get(session_id)
        if not rec:
            raise KeyError(f"no session {session_id}")
        self._touch(session_id, summary=text)
        self.ctx.add_summary_turn(session_id, text)
        return text

    def delete(self, session_id: str):
        self.ctx.drop(session_id)
        with self._lock:
            self._active.pop(session_id, None)
        return {"deleted": self.store.delete_session(session_id), "session_id": session_id}

    def export(self, session_id: str) -> dict:
        rec = self.get(session_id)
        if not rec:
            raise KeyError(f"no session {session_id}")
        return {"session": rec,
                "events": self.store.session_events(session_id),
                "context": self.ctx.rolling_context(session_id)}

    # ---- append transcript / action / event ---- #
    def add_transcript(self, session_id: str, text: str, final=True, speaker="user"):
        rec = self.get(session_id)
        if not rec:
            raise KeyError(f"no session {session_id}")
        entry = {"ts": time.time(), "text": text, "final": final, "speaker": speaker}
        with self._lock:
            cur = self._active.get(session_id)
            if cur is not None:
                cur["transcript"].append(entry)
                # bound the in-memory transcript (spec 28: no unbounded growth)
                if len(cur["transcript"]) > 2000:
                    cur["transcript"] = cur["transcript"][-2000:]
                self.store.put_session(cur)
        self.ctx.add_utterance(session_id, text, final=final, speaker=speaker)
        self.store.append_event(session_id, {"type": "transcript.final" if final else
                                             "transcript.partial", "ts": time.time(),
                                             "payload": entry})
        return entry

    def record_action(self, session_id: str, action: dict):
        rec = self.get(session_id)
        if not rec:
            raise KeyError(f"no session {session_id}")
        with self._lock:
            cur = self._active.get(session_id)
            if cur is not None:
                cur["actions"].append(action)
        self.store.append_event(session_id, {"type": action.get("type", "tool.completed"),
                                             "ts": time.time(), "payload": action})

    def list(self, limit=100):
        return self.store.list_sessions(limit)
