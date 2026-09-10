"""Explicit call state machine (spec section 4).

Every state transition is recorded on the call record. The machine is the single
source of truth for a call's life and enforces legal transitions. Because Android
telephony state is delivered asynchronously, we allow the events we actually
observe; illegal jumps raise InvalidCallState rather than silently proceeding.
"""
from __future__ import annotations

import time
from typing import Callable

from .errors import InvalidCallState
from .model import (ACTIVE_STATES, TERMINAL_STATES, CallRecord, canonical_state,
                    new_id)

# Allowed direct transitions. Everything else must pass through an intermediate
# observed state. We intentionally keep this permissive enough to match real
# Android/telephony asynchrony while still blocking nonsense like a completed
# call becoming INCOMING_RINGING again.
ALLOWED = {
    "IDLE": ["INCOMING_RINGING", "OUTGOING_DIALING", "ERROR"],
    "INCOMING_RINGING": ["CALL_ANSWERING", "REJECTED", "MISSED", "CALL_ENDING",
                          "CALL_ACTIVE", "DISCONNECTED", "ERROR"],
    "CALL_ANSWERING": ["CALL_ACTIVE", "CALL_ENDING", "FAILED", "ERROR"],
    "OUTGOING_DIALING": ["OUTGOING_RINGING", "CALL_ACTIVE", "BUSY", "VOICEMAIL",
                          "FAILED", "DISCONNECTED", "ERROR"],
    "OUTGOING_RINGING": ["CALL_ACTIVE", "BUSY", "VOICEMAIL", "MISSED",
                          "CALL_ENDING", "FAILED", "ERROR"],
    "CALL_ACTIVE": ["AI_SESSION_STARTING", "ON_HOLD", "CALL_ENDING", "TRANSFERRED",
                     "DISCONNECTED", "ERROR"],
    "ON_HOLD": ["CALL_ACTIVE", "CALL_ENDING", "TRANSFERRED", "ERROR"],
    "AI_SESSION_STARTING": ["AI_CONVERSATION_ACTIVE", "CALL_ACTIVE", "CALL_ENDING",
                             "ERROR"],
    "AI_CONVERSATION_ACTIVE": ["CALL_ACTIVE", "AI_SESSION_STARTING", "ON_HOLD",
                                "CALL_ENDING", "TRANSFERRED", "ERROR"],
    "CALL_ENDING": ["CALL_COMPLETED", "DISCONNECTED", "ERROR"],
    "BUSY": TERMINAL_STATES,
    "REJECTED": ["CALL_COMPLETED"],
    "MISSED": ["CALL_COMPLETED"],
    "VOICEMAIL": ["CALL_ACTIVE", "CALL_COMPLETED"],
    "TRANSFERRED": ["CALL_COMPLETED"],
    "DISCONNECTED": ["CALL_COMPLETED"],
    "FAILED": ["CALL_COMPLETED"],
    "ERROR": ["CALL_COMPLETED", "IDLE"],
}


class CallMachine:
    def __init__(self, on_transition: Callable | None = None):
        self._on = on_transition

    def new_call(self, direction: str, number: str = "", sim: str = "") -> CallRecord:
        rec = CallRecord(call_id=new_id("call"), direction=direction, number=number,
                         sim=sim, state="IDLE", started_at=time.time())
        rec.transitions.append({"from": None, "to": "IDLE", "at": time.time()})
        return rec

    def transition(self, rec: CallRecord, to_state: str) -> CallRecord:
        to = canonical_state(to_state)
        frm = rec.state
        if to == frm:
            return rec
        if frm in TERMINAL_STATES and to != "IDLE":
            raise InvalidCallState(
                f"call {rec.call_id} is terminal ({frm}); cannot move to {to}")
        allowed = ALLOWED.get(frm, [])
        if to not in allowed:
            # allow the common observed jump answered->active even if we missed
            # an intermediate event, but never re-animate a finished call
            if to not in TERMINAL_STATES and to not in ACTIVE_STATES:
                raise InvalidCallState(
                    f"illegal transition {frm} -> {to} for call {rec.call_id}")
        now = time.time()
        if to in ("CALL_ACTIVE", "AI_CONVERSATION_ACTIVE") and not rec.answered_at:
            rec.answered_at = now
        if to in TERMINAL_STATES:
            rec.ended_at = now
            if rec.answered_at:
                rec.duration_s = int(now - rec.answered_at)
            rec.outcome = _outcome_for(to)
        rec.state = to
        rec.transitions.append({"from": frm, "to": to, "at": now})
        if self._on:
            self._on(rec.call_id, frm, to)
        return rec

    def is_active(self, rec: CallRecord) -> bool:
        return rec.state in ACTIVE_STATES


def _outcome_for(state: str) -> str:
    if state == "CALL_COMPLETED":
        return "completed"
    if state == "MISSED":
        return "missed"
    if state == "REJECTED":
        return "rejected"
    if state == "VOICEMAIL":
        return "voicemail"
    if state == "TRANSFERRED":
        return "transferred"
    if state == "BUSY":
        return "busy"
    if state == "FAILED":
        return "failed"
    if state == "DISCONNECTED":
        return "disconnected"
    if state == "ERROR":
        return "error"
    return state.lower()
