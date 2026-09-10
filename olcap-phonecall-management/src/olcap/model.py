"""Data model: capability descriptors, call-state vocabulary, call records.

Pure data + helpers with no I/O so the state machine and tests stay simple and
portable across the Python control plane and (conceptually) the Android side.
"""
from __future__ import annotations

import time
from dataclasses import dataclass, field, asdict
from typing import Optional


def new_id(prefix: str = "call") -> str:
    return f"{prefix}_{int(time.time()*1000)}_{id(object()) & 0xFFFF}"


# ---- Call state vocabulary (spec section 4) ------------------------- #
CALL_STATES = [
    "IDLE",
    "INCOMING_RINGING",
    "OUTGOING_DIALING",
    "OUTGOING_RINGING",
    "CALL_ANSWERING",
    "CALL_ACTIVE",
    "AI_SESSION_STARTING",
    "AI_CONVERSATION_ACTIVE",
    "ON_HOLD",
    "BUSY",
    "REJECTED",
    "MISSED",
    "VOICEMAIL",
    "TRANSFERRED",
    "CALL_ENDING",
    "CALL_COMPLETED",
    "DISCONNECTED",
    "FAILED",
    "ERROR",
]

# Terminal states.
TERMINAL_STATES = {"CALL_COMPLETED", "REJECTED", "MISSED", "VOICEMAIL",
                   "TRANSFERRED", "DISCONNECTED", "FAILED", "ERROR"}

# States where an active audio path (if supported) is live.
ACTIVE_STATES = {"CALL_ACTIVE", "AI_CONVERSATION_ACTIVE", "ON_HOLD"}


def canonical_state(s: str) -> str:
    return s.strip().upper().replace(" ", "_")


@dataclass
class CallRecord:
    call_id: str
    direction: str                # incoming | outgoing
    number: str = ""
    contact: str = ""             # resolved identity, may be empty
    contact_id: str = ""
    sim: str = ""                 # SIM slot / subscription as reported by device
    subscription_id: Optional[int] = None
    backend: str = ""             # which TelephonyBackend handled the call
    state: str = "IDLE"
    started_at: Optional[float] = None
    answered_at: Optional[float] = None
    ended_at: Optional[float] = None
    duration_s: int = 0
    ai_session_id: str = ""
    objective: str = ""
    objective_constraints: list = field(default_factory=list)
    max_duration_seconds: int = 0
    transcript_ref: str = ""      # reference, never raw audio bytes
    summary: str = ""
    actions: list = field(default_factory=list)
    errors: list = field(default_factory=list)
    policy_used: str = ""
    outcome: str = ""
    transitions: list = field(default_factory=list)
    style_profile: dict = field(default_factory=dict)  # speaking-style/register

    def dict(self):
        return asdict(self)


@dataclass
class SimInfo:
    slot: str
    carrier: str = ""
    subscription_id: Optional[int] = None
    active: bool = True
    default: bool = False

    def dict(self):
        return asdict(self)


@dataclass
class DeviceCapabilities:
    """Honest capability assessment (spec sections 8 & 31).

    Defaults are the *least* capability. Real capability is filled in by an
    Android capability probe / the active backend. Never fabricated.
    """
    device_attached: bool = False
    source: str = "none"          # none | android-probe | backend:<name>
    call_state_monitoring: bool = False
    cellular_call_control: bool = False     # dial/answer/reject/hangup on SIM
    call_audio_capture: bool = False        # capture of cellular call audio
    call_audio_injection: bool = False      # injecting audio into the call
    ai_cellular_conversation: bool = False
    adb: bool = False                       # ADB transport to a real device
    wireless_adb: bool = False              # device reachable over wireless ADB
    sim_selection: bool = False             # can pick a specific SIM slot
    provider_realtime_voice: bool = False
    voip_available: bool = False
    local_ai_pipeline: bool = False
    foreground_service: bool = False
    accessibility_control: bool = False
    telecom_integration: bool = False
    multi_sim: bool = False
    bluetooth_call_audio: bool = False
    default_phone_app: bool = False

    def dict(self) -> dict:
        d = asdict(self)
        # top-level convenience booleans for the spec's example shape
        d["cellular_call_control"] = self.cellular_call_control
        d["call_audio_capture"] = self.call_audio_capture
        d["call_audio_injection"] = self.call_audio_injection
        d["ai_cellular_conversation"] = self.ai_cellular_conversation
        d["full_duplex_cellular_ai"] = self.ai_cellular_conversation
        d["provider_realtime_voice"] = self.provider_realtime_voice
        return d

    def merge(self, other: "DeviceCapabilities"):
        for k in asdict(other):
            setattr(self, k, getattr(other, k))
        return self

    def summary(self) -> dict:
        return {
            "device_attached": self.device_attached,
            "cellular_call_control": self.cellular_call_control,
            "call_audio_capture": self.call_audio_capture,
            "call_audio_injection": self.call_audio_injection,
            "ai_cellular_conversation": self.ai_cellular_conversation,
            "full_duplex_cellular_ai": self.ai_cellular_conversation,
            "adb": self.adb,
            "wireless_adb": self.wireless_adb,
            "sim_selection": self.sim_selection,
            "provider_realtime_voice": self.provider_realtime_voice,
            "voip_available": self.voip_available,
            "source": self.source,
        }
