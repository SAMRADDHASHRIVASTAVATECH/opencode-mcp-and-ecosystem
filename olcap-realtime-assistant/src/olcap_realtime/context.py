"""Context engine - persistent but bounded rolling memory (spec section 11, 28).

Maintains: current task, recent screen observations, recent transcript, current
conversation, detected entities, active application, relevant files, recent tool
operations and AI decisions. Uses rolling windows + incremental summaries so
unbounded history never accumulates and realtime requests stay small.
"""
from __future__ import annotations

import threading
from collections import deque
from dataclasses import dataclass, field, asdict


@dataclass
class ScreenObs:
    ts: float = 0.0
    app: str = ""
    window: str = ""
    region: str = ""
    summary: str = ""           # vision/OCR summary, not raw image
    changed: bool = False


@dataclass
class Utterance:
    ts: float = 0.0
    text: str = ""
    final: bool = True
    speaker: str = "user"


@dataclass
class ContextState:
    session_id: str = ""
    mode: str = "off"
    current_task: str = ""
    active_app: str = ""
    active_window: str = ""
    language: str = ""
    transcript_window: deque = field(default_factory=lambda: deque(maxlen=30))
    screen_window: deque = field(default_factory=lambda: deque(maxlen=8))
    tool_log: deque = field(default_factory=lambda: deque(maxlen=20))
    decisions: deque = field(default_factory=lambda: deque(maxlen=15))
    entities: set = field(default_factory=set)
    relevant_files: list = field(default_factory=list)
    rolling_summary: str = ""

    def to_dict(self):
        d = asdict(self)
        d["entities"] = sorted(self.entities)
        d["transcript_window"] = [u.__dict__ if hasattr(u, "__dict__") else u
                                  for u in self.transcript_window]
        d["screen_window"] = [u.__dict__ if hasattr(u, "__dict__") else u
                              for u in self.screen_window]
        d["tool_log"] = list(self.tool_log)
        d["decisions"] = list(self.decisions)
        return d


class ContextEngine:
    def __init__(self):
        self._lock = threading.Lock()
        self._sessions: dict[str, ContextState] = {}

    def new(self, session_id: str, mode: str = "off") -> ContextState:
        cs = ContextState(session_id=session_id, mode=mode)
        with self._lock:
            self._sessions[session_id] = cs
        return cs

    def get(self, session_id: str) -> ContextState | None:
        with self._lock:
            return self._sessions.get(session_id)

    def require(self, session_id: str) -> ContextState:
        cs = self.get(session_id)
        if cs is None:
            raise KeyError(f"no session {session_id}")
        return cs

    def drop(self, session_id: str):
        with self._lock:
            self._sessions.pop(session_id, None)

    def set_task(self, session_id, task: str):
        cs = self.require(session_id)
        cs.current_task = task
        return task

    def add_utterance(self, session_id, text: str, final: bool = True, speaker="user"):
        cs = self.require(session_id)
        cs.transcript_window.append(Utterance(text=text, final=final, speaker=speaker))
        if speaker == "user":
            _extract_entities(cs, text)
        return cs.to_dict()

    def add_screen(self, session_id, app="", window="", summary="", region="",
                   changed=False):
        cs = self.require(session_id)
        cs.screen_window.append(ScreenObs(app=app, window=window, summary=summary,
                                          region=region, changed=changed))
        if app:
            cs.active_app = app
        if window:
            cs.active_window = window
        return cs.to_dict()

    def add_tool(self, session_id, name: str, status: str, detail=None):
        cs = self.require(session_id)
        cs.tool_log.append({"tool": name, "status": status, "detail": detail})
        return cs.to_dict()

    def add_decision(self, session_id, summary: str):
        cs = self.require(session_id)
        cs.decisions.append(summary)
        return cs.to_dict()

    # ---- bounded summary of a session for a reasoning request ---- #
    def rolling_context(self, session_id: str, max_transcript=12) -> dict:
        """Compact, bounded view used as the prompt context - never the whole
        raw history (low-latency strategy)."""
        cs = self.require(session_id)
        transcript = [f"{u.speaker}: {u.text}" for u in
                      list(cs.transcript_window)[-max_transcript:]]
        screens = []
        for o in list(cs.screen_window):
            if o.changed and o.summary:
                screens.append(o.summary)
        return {
            "session_id": session_id,
            "mode": cs.mode,
            "task": cs.current_task,
            "active_app": cs.active_app,
            "active_window": cs.active_window,
            "recent_transcript": transcript,
            "recent_screen": screens[-4:],
            "recent_tools": list(cs.tool_log)[-8:],
            "rolling_summary": cs.rolling_summary,
            "entities": sorted(cs.entities),
            "relevant_files": cs.relevant_files,
        }

    def add_summary_turn(self, session_id, text: str):
        cs = self.require(session_id)
        # keep a compact incremental summary (append truncated)
        cs.rolling_summary = (cs.rolling_summary + "\n" + text).strip()
        if len(cs.rolling_summary) > 2000:
            cs.rolling_summary = cs.rolling_summary[-2000:]
        return cs.rolling_summary


def _extract_entities(cs: ContextState, text: str):
    import re
    # crude but useful entity candidates: capitalized words / file-like tokens
    for tok in re.findall(r"[A-Z][a-z]{2,}", text):
        cs.entities.add(tok)
    for tok in re.findall(r"[\w./-]+\.(py|ts|tsx|js|jsx|java|kt|md|json|txt|go|rs)",
                          text):
        cs.entities.add(tok)
