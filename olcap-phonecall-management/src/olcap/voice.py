"""Realtime AI voice provider abstraction (spec sections 7, 21) + call
objectives/summaries/transcripts.

Design notes for honest capability:
  * A real cellular-call audio path is NOT assumed. Real-time AI conversation is
    only possible through a backend that genuinely provides an audio path
    (provider realtime voice / VoIP / OpenClaw voice / a local pipeline).
  * The portable core therefore models the AI *session state machine* and holds
    objectives/constraints/summaries. Whether live audio flows is the decision of
    the connected RealtimeVoiceProvider. If none is configured/reachable, session
    creation raises AiProviderUnavailable rather than faking.
  * A LocalVoicePipeline / openclaw / provider implementations plug in behind the
    same interface (provider-agnostic).

This module also provides the deterministic transcript + summary model used by the
simulated provider so tests can exercise the full AI lifecycle offline.
"""
from __future__ import annotations

import abc
import time

from .errors import AiProviderUnavailable, CallNotActive, InvalidCallState
from .model import CALL_STATES

AI_SESSION_STATES = ["AI_SESSION_STARTING", "AI_CONVERSATION_ACTIVE", "CALL_ACTIVE",
                     "CALL_ENDING"]


class RealtimeVoiceProvider(abc.ABC):
    name = "abstract"

    @abc.abstractmethod
    def available(self) -> bool:
        ...

    def create_session(self, call_id: str, objective: str = "", constraints=None,
                       max_duration_seconds: int = 0, language: str = "",
                       accent: str = "") -> dict:
        raise AiProviderUnavailable(f"provider {self.name} not available")

    def send_transcript_chunk(self, session_id: str, text: str) -> dict:
        raise AiProviderUnavailable(f"provider {self.name} has no audio path")

    def get_transcript(self, session_id: str) -> dict:
        return {"session_id": session_id, "transcript": [], "simulated": True}

    def stop(self, session_id: str) -> dict:
        return {"session_id": session_id, "stopped": True}

    def capabilities(self) -> dict:
        return {"name": self.name, "available": self.available()}


class SimulatedRealtimeVoiceProvider(RealtimeVoiceProvider):
    """Deterministic provider used when no real provider is configured. Clearly
    labelled; models the AI session + streaming transcript but produces no real
    audio (there is no real call audio path on this host)."""
    name = "simulated"

    def __init__(self):
        self._sessions = {}

    def available(self) -> bool:
        return True

    def create_session(self, call_id, objective="", constraints=None,
                       max_duration_seconds=0, language="", accent="") -> dict:
        sid = f"ai_{int(time.time()*1000)}"
        self._sessions[sid] = {
            "session_id": sid, "call_id": call_id, "objective": objective,
            "constraints": constraints or [], "max_duration_seconds": max_duration_seconds,
            "language": language or "en", "accent": accent or "",
            "transcript": [], "created": time.time(),
        }
        return {"session_id": sid, "call_id": call_id, "state": "AI_SESSION_STARTING",
                "language": language or "en", "accent": accent or "", "simulated": True}

    def send_transcript_chunk(self, session_id, text):
        if session_id not in self._sessions:
            raise CallNotActive(f"no AI session {session_id}")
        self._sessions[session_id]["transcript"].append(
            {"ts": time.time(), "text": text})
        return {"session_id": session_id, "received": True, "simulated": True}

    def get_transcript(self, session_id):
        if session_id not in self._sessions:
            raise CallNotActive(f"no AI session {session_id}")
        return {"session_id": session_id,
                "transcript": self._sessions[session_id]["transcript"],
                "simulated": True}

    def stop(self, session_id):
        if session_id not in self._sessions:
            raise CallNotActive(f"no AI session {session_id}")
        del self._sessions[session_id]
        return {"session_id": session_id, "stopped": True, "simulated": True}


# ---- objective & summary helpers ----------------------------------- #
def summarize(call: dict, transcript: list) -> str:
    """Deterministic summary used when no generative model is available. Concise
    and factual - never fabricates content the transcript didn't contain."""
    lines = []
    for t in transcript:
        text = (t.get("text") or "").strip()
        if text:
            lines.append(text)
    n = len(lines)
    head = "AI-managed call"
    if n:
        head = "Call transcript: " + " | ".join(lines[:8])
    outcome = call.get("outcome") or call.get("state", "").lower()
    return (f"{head} (lines={n}, outcome={outcome}). "
            f"Objective: {call.get('objective') or 'none set'}.")
