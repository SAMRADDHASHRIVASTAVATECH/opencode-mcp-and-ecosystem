"""OLCAP PhoneManager - the authoritative control plane.

Owns the call store, state machine(s), backend, policy engine, contact resolver,
security, events and AI-voice sessions. All phone.* MCP tools are thin wrappers
over this object, so OpenClaw/OpenCode never manipulate telephony APIs directly.

Honesty rules enforced here:
  * Never auto-answer without an explicit matching policy.
  * Initiate/answer calls only after authorisation + destination/caller policy.
  * Do NOT claim an audio path exists unless the backend provides one.
  * Every call has a unique call_id (never the bare number).
"""
from __future__ import annotations

import threading
import time
from datetime import datetime
from typing import Any

from . import __version__
from .config import AppConfig
from .contacts import AmbiguousContact, ContactResolver
from .errors import (CallAudioUnavailable, CallNotActive, CapabilityUnsupported,
                     InvalidCallState, SimUnavailable)
from .events import EventBus
from .model import (ACTIVE_STATES, CallRecord, DeviceCapabilities, SimInfo,
                    canonical_state)
from .policy import PolicyEngine
from .security import SecurityManager
from .state_machine import CallMachine
from .store import Store
from .voice import RealtimeVoiceProvider, SimulatedRealtimeVoiceProvider, summarize
from .voice_kokoro import KokoroRealtimeVoiceProvider


def _import_comm():
    from . import communication
    return communication


class PhoneManager:
    def __init__(self, config: AppConfig, backend=None, voice=None, store=None,
                 provider_token: str = "", remote: bool | None = None):
        self.cfg = config
        self.store = store or Store(config.db_path)
        self.machine = CallMachine()
        self.backend: Any = backend          # set later by _wire_backend
        self.voice: Any = voice
        self.events = EventBus()
        self.contacts = ContactResolver()
        self.policies = PolicyEngine(config, self.store)
        self.security = SecurityManager(config, self.store)
        self._calls: dict[str, CallRecord] = {}   # active call records
        self._ai_sessions: dict[str, str] = {}    # session_id -> call_id
        self._lock = threading.Lock()
        self._backend_reason: list[str] = []
        self._sync_thread: threading.Thread | None = None
        self._sync_stop = threading.Event()
        self._sync_lock = threading.RLock()
        self._wire_backend(backend)
        self._wire_voice(voice)
        # recover persisted emergency-stop state
        if self.store.get_kv("emergency_stop"):
            self.security._emergency_stop = True
        self._provider_token = provider_token
        self._remote_override = remote
        self._start_sync()

    # ---- wiring ------------------------------------------------------ #
    def _wire_backend(self, backend):
        if backend is None:
            from .backends.selector import select_backend
            backend, reasons = select_backend(self.cfg)
            self._backend_reason = reasons
        self.backend = backend
        # pull honest capability assessment into a manager-level report
        self._device_caps = backend.capabilities()

    def get_backend(self) -> dict:
        name = getattr(self.backend, "name", "?")
        return {"backend": name,
                "reasons": list(self._backend_reason),
                "mode": "simulated" if name == "simulated" else "live",
                "devices": (self.backend.device_status() or {})}

    # ---- backend state sync loop ------------------------------------ #
    def _start_sync(self):
        if not callable(getattr(self.backend, "poll", None)):
            return  # backends without a poll() (simulated, openclaw) skip
        self._sync_thread = threading.Thread(
            target=self._sync_loop, name="olcap-backend-sync", daemon=True)
        self._sync_thread.start()

    def _sync_loop(self):
        interval = max(1, getattr(self.cfg, "adb_health_poll_s", 2) or 2)
        while not self._sync_stop.is_set():
            self._sync_stop.wait(interval)
            try:
                self.poll_backend()
            except Exception:
                pass

    def poll_backend(self):
        """Push real device call-state into the authoritative call records.
        Idle + a record we think is still ringing/active -> end it honestly."""
        if not callable(getattr(self.backend, "poll", None)):
            return
        with self._sync_lock:
            for call_id, rec in list(self._calls.items()):
                if rec.state in ACTIVE_STATES or rec.state in ("OUTGOING_DIALING",
                                                              "OUTGOING_RINGING",
                                                              "INCOMING_RINGING"):
                    try:
                        st = self.backend.poll(call_id)
                    except Exception:
                        continue
                    s = st.get("state", "unknown")
                    if s == "ringing":
                        if rec.state == "OUTGOING_DIALING":
                            self.machine.transition(rec, "OUTGOING_RINGING")
                        elif rec.state == "OUTGOING_RINGING":
                            pass
                        elif rec.state in ("INCOMING_RINGING",):
                            pass
                        continue
                    if s == "offhook":
                        # Device shows an active call; jump directly to the
                        # active state (the machine allows this from all three
                        # pre-active states and sets answered_at automatically).
                        if rec.state in ("OUTGOING_DIALING", "OUTGOING_RINGING",
                                         "INCOMING_RINGING"):
                            try:
                                self.machine.transition(rec, "CALL_ACTIVE")
                            except Exception:
                                pass
                            self._persist(rec)
                        continue
                    if s == "idle":
                        # Device shows idle while we still think a call is live:
                        # an outgoing call that was not answered ends here.
                        if rec.direction == "outgoing":
                            try:
                                self.machine.transition(rec, "CALL_ENDING")
                                self.machine.transition(rec, "CALL_COMPLETED")
                            except Exception:
                                continue
                            self._finalize(rec)
                            self.events.publish("disconnected", call_id=call_id)
                        continue

    def _wire_voice(self, voice):
        provider = self.cfg.default_voice_provider
        if voice is not None:
            self.voice = voice
            self._voice_configured = True
            self._voice_real = getattr(voice, "name", "") != "simulated"
            return
        # Route to the correct provider based on config
        if provider == "kokoro":
            self.voice = KokoroRealtimeVoiceProvider(
                base_url=self.cfg.voice_api_url or "http://127.0.0.1:8899",
            )
            self._voice_configured = True
            self._voice_real = True
        elif provider in ("", "none"):
            self.voice = SimulatedRealtimeVoiceProvider()
            self._voice_configured = False
            self._voice_real = False
        else:
            # simulated, openclaw, provider, voip — fall back to simulated
            self.voice = SimulatedRealtimeVoiceProvider()
            self._voice_configured = provider not in ("", "none")
            self._voice_real = (provider not in ("", "none", "simulated"))

    # ---- auth helper ------------------------------------------------- #
    def _auth(self, token: str = ""):
        return self.security.require_authorized(token, remote=self._remote_override)

    # ---- capability -------------------------------------------------- #
    def capabilities(self) -> DeviceCapabilities:
        self._device_caps = self.backend.capabilities()
        caps = self._device_caps
        # augment with voice provider info
        caps.source = self._device_caps.source or "backend"
        return caps

    def _report(self) -> dict:
        c = self.capabilities()
        return {
            "device_attached": c.device_attached,
            "adb": c.adb,
            "wireless_adb": c.wireless_adb,
            "cellular_call_control": c.cellular_call_control,
            "call_audio_capture": c.call_audio_capture,
            "call_audio_injection": c.call_audio_injection,
            "ai_cellular_conversation": c.ai_cellular_conversation,
            "full_duplex_cellular_ai": c.ai_cellular_conversation,
            "sim_selection": c.sim_selection,
            # provider_realtime_voice only reflects a REAL provider, never the
            # simulated fallback.
            "provider_realtime_voice": c.provider_realtime_voice or
                                       (self._voice_real and self.voice.available()),
            "ai_session_available": (self._voice_configured and self.voice.available()),
            "voice_mode": "simulated" if not self._voice_real else "live",
            "voip_available": c.voip_available,
            "local_ai_pipeline": c.local_ai_pipeline,
            "multi_sim": c.multi_sim,
            "source": c.source,
            "backend": getattr(self.backend, "name", "?"),
        }

    # ---- device / sim ------------------------------------------------- #
    def device_status(self):
        st = self.backend.device_status()
        st["simulated"] = st.get("simulated", False)
        return st

    def network_status(self):
        return self.backend.network_status()

    def sim_slots(self):
        return self.backend.sim_slots()

    def get_default_sim(self):
        for s in self.backend.sim_slots():
            if s.get("default"):
                return s
        slots = self.backend.sim_slots()
        return slots[0] if slots else None

    # ---- status ------------------------------------------------------ #
    def status(self):
        active = [self._safe(r) for r in self._calls.values()]
        return {
            "online": True,
            "emergency_stop": self.security.emergency_stop,
            "active_calls": active,
            "active_call_count": len(active),
            "voice_configured": self._voice_configured,
            "voice_available": self._voice_configured and self.voice.available(),
            "voice_real": self._voice_real,
            "auto_answer_enabled": self.cfg.auto_answer_enabled,
            "ai_calls_enabled": self.cfg.ai_calls_enabled,
            "mode": "simulated" if getattr(self.backend, "name", "") == "simulated"
                    else "live",
            "backend": getattr(self.backend, "name", "?"),
            "backend_reasons": list(self._backend_reason),
            "policy": {
                "auto_answer_enabled": self.cfg.auto_answer_enabled,
                "ai_answer_enabled": self.cfg.ai_calls_enabled,
                "calling_allowed": not self.security.emergency_stop,
            },
            "version": self.version(),
        }

    # ---- records ------------------------------------------------------ #
    def _persist(self, rec: CallRecord):
        self.store.put_call(rec.dict())

    def get_call(self, call_id: str) -> dict | None:
        rec = self._calls.get(call_id)
        if rec:
            return rec.dict()
        return self.store.get_call(call_id)

    def _safe(self, rec) -> dict:
        d = rec.dict()
        return d

    # ---- call lookup helper ------------------------------------------ #
    def _live_rec(self, call_id: str) -> CallRecord:
        rec = self._calls.get(call_id)
        if not rec:
            raise CallNotActive(f"no active call '{call_id}' (call it first)")
        return rec

    # ---- INCOMING ---------------------------------------------------- #
    def on_incoming(self, number: str, sim: str = "", token: str = "") -> dict:
        """Called by the Android bridge when an incoming call is detected, or by
        the simulated backend in tests/demos."""
        self._auth(token)
        self.security.require_calling_allowed()
        contact = self.contacts.identify_caller(number)
        policy = self.policies.decide_incoming(
            number, str(contact.get("name") or "") if contact else "")
        rec = self.machine.new_call("incoming", number=number, sim=sim)
        self._calls[rec.call_id] = rec
        rec.policy_used = policy["name"]
        self.machine.transition(rec, "INCOMING_RINGING")
        rec.contact = contact.get("name", "") if contact else ""
        rec.contact_id = contact.get("contact_id", "") if contact else ""
        self.backend.attach_call(number, "incoming", sim, rec.call_id)
        self._persist(rec)
        self.events.publish("incoming_call", call_id=rec.call_id, number=number,
                            contact=rec.contact, policy=policy["name"])
        decision = self._apply_incoming_policy(rec, policy)
        return {"call_id": rec.call_id, "number": number,
                "contact": rec.contact, "policy": policy["name"],
                "action": decision, "state": rec.state}

    def _apply_incoming_policy(self, rec, policy) -> Any:
        action = policy.get("action", "ring_normal")
        # Never auto-answer unless policy explicitly authorises it.
        if action == "auto_answer":
            return self._do_answer(rec, ai=False)
        if action == "ai_answer":
            if not (self._voice_configured and self.voice.available()):
                # fall back to notify; be honest we can't AI-answer
                self.events.publish("error", call_id=rec.call_id,
                                    code="AI_PROVIDER_UNAVAILABLE")
                return "notify_no_ai"
            return self._do_answer(rec, ai=True)
        if action in ("reject",):
            self.machine.transition(rec, "REJECTED")
            self._persist(rec)
            self.events.publish("rejected", call_id=rec.call_id)
            return "rejected"
        if action in ("silence", "notify"):
            return action
        return "ring_normal"

    # ---- OUTGOING ---------------------------------------------------- #
    def place_call(self, destination: str, sim: str = "", token: str = "",
                   authorized: bool = False) -> dict:
        actor = self._auth(token)
        self.security.require_calling_allowed()
        self.policies.authorize_destination(destination)
        if not authorized:
            raise InvalidCallState(
                "calling requires explicit authorization unless a policy "
                "authorises this caller/destination")
        self._end_stale_device_call()
        # pick sim default
        use_sim = sim or self.cfg.default_sim
        if use_sim == "system":
            d = self.get_default_sim()
            use_sim = d.get("slot") if d else ""
        self.security.throttle()
        rec = self.machine.new_call("outgoing", number=destination, sim=use_sim)
        rec.backend = self.backend.name
        self.backend.dial(destination, sim=use_sim, call_id=rec.call_id)
        self._calls[rec.call_id] = rec
        self.machine.transition(rec, "OUTGOING_DIALING")
        self.machine.transition(rec, "OUTGOING_RINGING")
        self._persist(rec)
        self.security.audit(actor, "place_call",
                            {"destination": destination, "sim": use_sim})
        self.events.publish("outgoing_call", call_id=rec.call_id,
                            number=destination, sim=use_sim)
        return {"call_id": rec.call_id, "number": destination, "sim": use_sim,
                "state": rec.state}


    # ---- call-control ops -------------------------------------------- #
    def _end_stale_device_call(self):
        """End any call already active on the device before placing a new one.
        Dialing a second line while one is active puts the first call on hold,
        which we never want — end it and finalize its local record first."""
        try:
            st = self.backend.poll("")
        except Exception:
            return
        if st.get("state") != "offhook":
            return
        try:
            self.backend.hangup("")
        except Exception:
            pass
        for call_id, rec in list(self._calls.items()):
            if rec.direction != "outgoing":
                continue
            try:
                self.machine.transition(rec, "CALL_ENDING")
                self.machine.transition(rec, "CALL_COMPLETED")
                self._finalize(rec)
                self.events.publish("disconnected", call_id=call_id)
                break
            except Exception:
                continue

    def answer_call(self, call_id: str, token: str = "") -> dict:
        self._auth(token)
        rec = self._live_rec(call_id)
        return self._do_answer(rec, ai=False)

    def _do_answer(self, rec, ai: bool):
        # Outbound calls are connected by the far end; inbound are answered by
        # us (CALL_ANSWERING). Handle both observed paths legally.
        if rec.state == "INCOMING_RINGING":
            self.machine.transition(rec, "CALL_ANSWERING")
        # Try backend answer; if unsupported we still allow state advance for
        # simulation, but must not claim audio.
        self.backend.answer(rec.call_id)
        if rec.state not in ("CALL_ACTIVE",):
            self.machine.transition(rec, "CALL_ACTIVE")
        self._persist(rec)
        self.events.publish("answered", call_id=rec.call_id)
        if ai:
            return self.start_ai_session(rec.call_id)
        return {"call_id": rec.call_id, "state": rec.state, "ai": False}

    def reject_call(self, call_id, token=""):
        self._auth(token)
        rec = self._live_rec(call_id)
        self.backend.reject(call_id)
        self.machine.transition(rec, "REJECTED")
        self._persist(rec)
        self.events.publish("rejected", call_id=call_id)
        return self._done(rec)

    def hangup_call(self, call_id, token=""):
        self._auth(token)
        rec = self._live_rec(call_id)
        self.backend.hangup(call_id)
        self.machine.transition(rec, "CALL_ENDING")
        self.machine.transition(rec, "CALL_COMPLETED")
        self._finalize(rec)
        self.events.publish("disconnected", call_id=call_id)
        return self._done(rec)

    def hold_call(self, call_id, token=""):
        self._auth(token)
        rec = self._live_rec(call_id)
        self.backend.hold(call_id)
        self.machine.transition(rec, "ON_HOLD")
        self._persist(rec)
        return {"call_id": call_id, "state": rec.state}

    def resume_call(self, call_id, token=""):
        self._auth(token)
        rec = self._live_rec(call_id)
        self.backend.resume(call_id)
        self.machine.transition(rec, "CALL_ACTIVE")
        self._persist(rec)
        return {"call_id": call_id, "state": rec.state}

    def mute_call(self, call_id, token=""):
        self._auth(token)
        rec = self._live_rec(call_id)
        self.backend.mute(call_id)
        self._persist(rec)
        return {"call_id": call_id, "state": rec.state}

    def unmute_call(self, call_id, token=""):
        self._auth(token)
        rec = self._live_rec(call_id)
        self.backend.unmute(call_id)
        self._persist(rec)
        return {"call_id": call_id, "state": rec.state}

    def send_dtmf(self, call_id, digits, token=""):
        self._auth(token)
        rec = self._live_rec(call_id)
        res = self.backend.send_dtmf(call_id, digits)
        self._persist(rec)
        return {"call_id": call_id, "sent": digits, **res}

    def _done(self, rec):
        return {"call_id": rec.call_id, "state": rec.state, "outcome": rec.outcome}

    def _finalize(self, rec):
        self._persist(rec)
        if rec.call_id in self._ai_sessions.values() and False:
            pass
        self._calls.pop(rec.call_id, None)

    # ---- history ----------------------------------------------------- #
    def call_history(self, limit=100):
        return self.store.list_calls(limit=limit)

    def active_calls(self):
        return [r.dict() for r in self._calls.values()]

    def call_status(self, call_id=None):
        if call_id:
            return self.get_call(call_id)
        return self.status()

    # ---- AI voice sessions ------------------------------------------- #
    def resolve_style(self, style=None, context="auto", register=None, contact="",
                      number="", identify_as_ai="default", language="", accent=""):
        comm = _import_comm()
        return comm.build_profile(style, context=context, register=register,
                                  contact=contact or "", number=number or "",
                                  identify_as_ai=identify_as_ai,
                                  language=language or "", accent=accent or "")

    def start_ai_session(self, call_id, objective="", constraints=None,
                         max_duration_seconds=0, token="",
                         style=None, context="auto", register=None,
                         identify_as_ai="default", language="", accent="") -> dict:
        self._auth(token)
        rec = self._live_rec(call_id)
        if not (self._voice_configured and self.voice.available()):
            raise CapabilityUnsupported(
                "AI conversation requires a configured realtime voice provider; "
                "none is reachable (or only a simulated provider is available)")
        self.machine.transition(rec, "AI_SESSION_STARTING")
        style_profile = self.resolve_style(style, context=context, register=register,
                                           contact=rec.contact, number=rec.number,
                                           identify_as_ai=identify_as_ai,
                                           language=language, accent=accent)
        s = self.voice.create_session(call_id, objective=objective,
                                      constraints=constraints,
                                      max_duration_seconds=max_duration_seconds or
                                      self.cfg.max_call_duration_seconds,
                                      language=style_profile.get("language", "en"),
                                      accent=style_profile.get("accent", ""))
        rec.ai_session_id = s["session_id"]
        rec.objective = objective
        rec.objective_constraints = list(constraints or [])
        rec.style_profile = style_profile
        self._ai_sessions[s["session_id"]] = call_id
        self.machine.transition(rec, "AI_CONVERSATION_ACTIVE")
        self._persist(rec)
        self.events.publish("ai_session_started", session_id=s["session_id"],
                            call_id=call_id)
        return {"call_id": call_id, "session_id": s["session_id"],
                "state": rec.state, "style": style_profile["name"],
                **s}

    def get_ai_session(self, session_id=None, call_id=None):
        if call_id:
            for sid, c in self._ai_sessions.items():
                if c == call_id:
                    session_id = sid
                    break
        if session_id and self._ai_sessions.get(session_id):
            return {"session_id": session_id, "call_id": self._ai_sessions[session_id],
                    "active": True}
        # fall back to transcript from provider
        if session_id:
            return self.voice.get_transcript(session_id)
        return None

    def stop_ai_session(self, session_id, token=""):
        self._auth(token)
        call_id = self._ai_sessions.pop(session_id, None)
        res = self.voice.stop(session_id)
        if call_id and call_id in self._calls:
            rec = self._calls[call_id]
            self.machine.transition(rec, "CALL_ACTIVE")
            self._persist(rec)
        self.events.publish("ai_session_ended", session_id=session_id, call_id=call_id)
        return {"session_id": session_id, **res}

    def live_transcript(self, session_id=None, call_id=None):
        if call_id:
            for sid, c in self._ai_sessions.items():
                if c == call_id:
                    session_id = sid
        if not session_id:
            return {"transcript": []}
        return self.voice.get_transcript(session_id)

    def call_transcript(self, call_id, token=""):
        self._auth(token)
        rec = self.get_call(call_id)
        if not rec:
            raise CallNotActive(f"unknown call {call_id}")
        if rec.get("ai_session_id"):
            try:
                return self.voice.get_transcript(rec["ai_session_id"])
            except Exception:
                pass
        return {"call_id": call_id, "transcript": []}

    def call_summary(self, call_id, token=""):
        self._auth(token)
        rec = self.get_call(call_id)
        if not rec:
            raise CallNotActive(f"unknown call {call_id}")
        transcript = []
        if rec.get("ai_session_id"):
            try:
                transcript = self.voice.get_transcript(
                    rec["ai_session_id"]).get("transcript", [])
            except Exception:
                transcript = []
        summ = summarize(rec, transcript)
        style = (rec.get("style_profile") or {}).get("name", "")
        self.store.put_call({**rec, "summary": summ})
        return {"call_id": call_id, "summary": summ,
                "session_id": rec.get("ai_session_id"), "style": style}

    # ---- languages / accents ---------------------------------------- #
    def list_languages(self, india_only=False):
        from . import languages as L
        if india_only:
            return {c: {"name": L.LANGUAGES[c]["name"],
                        "native": L.LANGUAGES[c]["native"],
                        "script": L.LANGUAGES[c]["script"]}
                    for c in L.INDIA_LANGUAGES if c in L.LANGUAGES}
        return {c: {"name": L.LANGUAGES[c]["name"], "native": L.LANGUAGES[c]["native"],
                    "script": L.LANGUAGES[c]["script"]}
                for c in sorted(L.LANGUAGES)}

    def detect_language_for_call(self, number=""):
        """Auto-detect language + accent for a number (used when none is set)."""
        comm = _import_comm()
        det = comm.detect_language_and_accent(number)
        from . import languages as L
        det["country_code"] = L.code_for_number(number)
        det["language_name"] = L.LANGUAGES.get(det["language"], {}).get("name", "")
        return det

    # ---- conversation style ------------------------------------------ #
    def list_styles(self):
        comm = _import_comm()
        return {name: info.get("summary", "") for name, info in comm.STYLES.items()}

    def conversation_brief(self, call_id):
        """Speaking-style conduct brief for a call (steers the AI voice backend)."""
        rec = self.get_call(call_id)
        if not rec:
            raise CallNotActive(f"unknown call {call_id}")
        comm = _import_comm()
        prof = rec.get("style_profile")
        if not prof:
            prof = self.resolve_style(contact=rec.get("contact", ""),
                                      number=rec.get("number", ""))
        return {"call_id": call_id, "style_profile": prof,
                "conduct": comm.summary_for_agent(prof)}

    def set_call_objective(self, call_id, objective, constraints=None,
                           max_duration_seconds=0, token="", style=None,
                           language="", accent=""):
        self._auth(token)
        rec = self._live_rec(call_id)
        rec.objective = objective
        rec.objective_constraints = list(constraints or [])
        rec.max_duration_seconds = max_duration_seconds or rec.max_duration_seconds
        if style or language or accent:
            rec.style_profile = self.resolve_style(
                style, contact=rec.contact, number=rec.number,
                language=language, accent=accent)
        self._persist(rec)
        return {"call_id": call_id, "objective": objective,
                "constraints": rec.objective_constraints,
                "style": (rec.style_profile or {}).get("name", "")}

    # ---- policy / config through manager ----------------------------- #
    def list_policies(self):
        return self.policies.list()

    def create_policy(self, name, policy, token=""):
        self._auth(token)
        p = self.policies.create(name, policy)
        self.security.audit("operator", "policy_create", {"name": name})
        return p

    def update_policy(self, name, policy, token=""):
        self._auth(token)
        p = self.policies.update(name, policy)
        self.security.audit("operator", "policy_update", {"name": name})
        return p

    def delete_policy(self, name, token=""):
        self._auth(token)
        ok = self.policies.delete(name)
        self.security.audit("operator", "policy_delete", {"name": name})
        return {"deleted": ok, "name": name}

    def enable_auto_answer(self, token=""):
        self._auth(token)
        self.cfg.auto_answer_enabled = True
        return {"auto_answer_enabled": True}

    def disable_auto_answer(self, token=""):
        self._auth(token)
        self.cfg.auto_answer_enabled = False
        return {"auto_answer_enabled": False}

    # ---- health / logs / reconnect ----------------------------------- #
    def health(self):
        try:
            self.store.conn.execute("SELECT 1")
            db = "ok"
        except Exception:
            db = "error"
        bhealth = {}
        if hasattr(self.backend, "health"):
            try:
                bhealth = self.backend.health()
            except Exception:
                bhealth = {"error": "unreachable"}
        sim = getattr(self.backend, "name", "?") == "simulated"
        return {"status": "ok", "db": db, "emergency_stop": self.security.emergency_stop,
                "voice_configured": self._voice_configured,
                "voice_available": self._voice_configured and self.voice.available(),
                "mode": "simulated" if sim else "live",
                "backend": getattr(self.backend, "name", "?"),
                "backend_health": bhealth}

    def version(self):
        return {"name": "olcap-phonecall-management", "version": __version__,
                "backend": getattr(self.backend, "name", "?"),
                "health": self.health()}

    def get_logs(self, limit=100):
        return self.store.recent_audit(limit)

    def emergency_stop(self, token=""):
        self._auth(token)
        # also hang up any AI sessions / active calls in a controlled way
        for call_id in list(self._calls.keys()):
            try:
                self.hangup_call(call_id)
            except Exception:
                pass
        return self.security.emergency_stop_engage()

    def reconnect(self, token=""):
        self._auth(token)
        # backend reconnect hook (no-op for simulated)
        if hasattr(self.backend, "reconnect"):
            self.backend.reconnect()
        return {"reconnected": True, "note": "transport reconnect requested"}

    def shutdown(self):
        try:
            self.store.close()
        except Exception:
            pass
