"""MCP server exposing the OLCAP phone control plane (spec section 3).

Exposes structured `phone.*` tools. NO unrestricted shell execution. Every
handler wraps the PhoneManager and maps structured errors to a stable code.
Secrets are never returned.
"""
from __future__ import annotations

import functools
import json
from typing import Annotated, Any, Optional

from mcp.server.fastmcp import FastMCP
from pydantic import Field

from . import __version__
from .errors import OlcapError
from .manager import PhoneManager

DESCRIPTION = (
    "OLCAP Phone Call Management - unified phone-call control plane. "
    "Structured phone.* tools for device status, call state/lifecycle, caller "
    "information, AI-voice sessions, call policies and system health. "
    "Capabilities are reported honestly; operations the device cannot perform "
    "return UNSUPPORTED_ON_THIS_DEVICE / CAPABILITY_UNSUPPORTED. Autonomous "
    "calling requires explicit authorization or an authorizing policy."
)

Str = Optional[str]
Int = Optional[int]
Bool = Optional[bool]


def _err(e) -> str:
    if isinstance(e, OlcapError):
        return json.dumps({"ok": False, "code": e.code, "error": e.message})
    return json.dumps({"ok": False, "code": "OLCAP_ERROR", "error": str(e)})


def _ok(d) -> str:
    return json.dumps({"ok": True, **d}, default=str)


class OlcapServer:
    def __init__(self, manager: PhoneManager):
        self.pm = manager
        self.mcp = FastMCP(name="olcap-phonecall-management",
                           instructions=DESCRIPTION)
        self._register_all()

    async def list_tools(self):
        return await self.mcp.list_tools()

    async def run_stdio_async(self):
        return await self.mcp.run_stdio_async()

    def tool(self, *a, **k):
        orig = self.mcp.tool(*a, **k)

        def _g(fn):
            @functools.wraps(fn)
            def w(*args, **kw):
                try:
                    r = fn(*args, **kw)
                except OlcapError as e:
                    return _err(e)
                except Exception as e:  # noqa: BLE001
                    return _err(e)
                return r if isinstance(r, str) else _ok(r)
            return orig(w)
        return _g

    def _reg(self, name, desc):
        """Decorator that registers a function under a dotted MCP tool name."""
        return self.tool(name=name, description=desc)

    def _register_all(self):
        pm = self.pm

        @self._reg("phone.get_status", "Overall phone/device status + active calls.")
        def phone_get_status():
            return pm.status()

        @self._reg("phone.get_capabilities", "Honest capability assessment.")
        def phone_get_capabilities():
            return pm._report()

        @self._reg("phone.get_network_status", "Network/connectivity status.")
        def phone_get_network_status():
            return pm.network_status()

        @self._reg("phone.get_sim_status", "SIM status summary.")
        def phone_get_sim_status():
            return {"sim_slots": pm.sim_slots(), "default_sim": pm.get_default_sim()}

        @self._reg("phone.get_default_sim", "Default voice SIM slot.")
        def phone_get_default_sim():
            return {"default_sim": pm.get_default_sim()}

        @self._reg("phone.list_sim_slots", "List SIM slots/subscriptions.")
        def phone_list_sim_slots():
            return {"sim_slots": pm.sim_slots()}

        # ---- Calls ---- #
        @self._reg("phone.get_active_calls", "List currently active calls.")
        def phone_get_active_calls():
            return {"calls": pm.active_calls()}

        @self._reg("phone.get_call_status",
                   "Get status of one call (call_id) or all if empty.")
        def phone_get_call_status(call_id: Str = ""):
            return pm.call_status(call_id or None)

        @self._reg("phone.get_call_history", "Return persisted call history.")
        def phone_get_call_history(limit: Int = 100):
            return {"calls": pm.call_history(limit or 100)}

        @self._reg("phone.place_call",
                   "Place an outbound call. Requires authorized=true unless a "
                   "policy authorises it. Optional sim, objective.")
        def phone_place_call(destination: str, sim: Str = "",
                             authorized: Bool = False, objective: Str = ""):
            return pm.place_call(destination, sim=sim or "",
                                 authorized=bool(authorized))

        @self._reg("phone.answer_call", "Answer an incoming call.")
        def phone_answer_call(call_id: str):
            return pm.answer_call(call_id)

        @self._reg("phone.reject_call", "Reject an incoming call.")
        def phone_reject_call(call_id: str):
            return pm.reject_call(call_id)

        @self._reg("phone.hangup_call", "Hang up an active call.")
        def phone_hangup_call(call_id: str):
            return pm.hangup_call(call_id)

        @self._reg("phone.hold_call", "Hold an active call.")
        def phone_hold_call(call_id: str):
            return pm.hold_call(call_id)

        @self._reg("phone.resume_call", "Resume a held call.")
        def phone_resume_call(call_id: str):
            return pm.resume_call(call_id)

        @self._reg("phone.mute_call", "Mute the active call microphone.")
        def phone_mute_call(call_id: str):
            return pm.mute_call(call_id)

        @self._reg("phone.unmute_call", "Unmute the active call.")
        def phone_unmute_call(call_id: str):
            return pm.unmute_call(call_id)

        @self._reg("phone.send_dtmf", "Send DTMF tones on an active call.")
        def phone_send_dtmf(call_id: str, digits: str):
            return pm.send_dtmf(call_id, digits)

        # ---- Caller information ---- #
        @self._reg("phone.identify_caller", "Identify a caller from a number.")
        def phone_identify_caller(number: str):
            return {"contact": pm.contacts.identify_caller(number)}

        @self._reg("phone.lookup_contact",
                   "Look up a contact by name/number; ambiguous names require "
                   "explicit confirmation.")
        def phone_lookup_contact(query: str):
            return {"contact": pm.contacts.lookup_contact(query)}

        @self._reg("phone.get_contact_context", "Context (notes/org) for a contact.")
        def phone_get_contact_context(query: str):
            return pm.contacts.context(query)

        # ---- AI voice ---- #
        @self._reg("phone.start_ai_voice_session",
                   "Start an AI voice session on an active call (requires a "
                   "configured realtime voice provider). style selects the "
                   "speaking register (india_* / global_*). language is an ISO "
                   "639 code (hi, ta, te, bn, mr, gu, kn, ml, pa, ur, or, as, "
                   "en, es, fr, de, ...); accent is a plain hint. If language is "
                   "omitted it is auto-detected from the destination number.")
        def phone_start_ai_voice_session(call_id: str, objective: Str = "",
                                         max_duration_seconds: Int = 0,
                                         style: Str = "", language: Str = "",
                                         accent: Str = ""):
            return pm.start_ai_session(call_id, objective=objective or "",
                                       max_duration_seconds=max_duration_seconds or 0,
                                       style=style or None,
                                       language=language or "", accent=accent or "")

        @self._reg("phone.stop_ai_voice_session", "Stop an AI voice session.")
        def phone_stop_ai_voice_session(session_id: str):
            return pm.stop_ai_session(session_id)

        @self._reg("phone.get_ai_voice_session",
                   "Get AI session by session_id or call_id.")
        def phone_get_ai_voice_session(session_id: Str = "", call_id: Str = ""):
            return pm.get_ai_session(session_id or None, call_id or None)

        @self._reg("phone.set_call_objective", "Set objective for a call.")
        def phone_set_call_objective(call_id: str, objective: str,
                                     max_duration_seconds: Int = 0):
            return pm.set_call_objective(call_id, objective,
                                         max_duration_seconds=max_duration_seconds or 0)

        @self._reg("phone.get_live_transcript",
                   "Live transcript of an AI session (session_id or call_id).")
        def phone_get_live_transcript(session_id: Str = "", call_id: Str = ""):
            return pm.live_transcript(session_id or None, call_id or None)

        @self._reg("phone.start_ai_call",
                   "Start an AI voice session on an active call. Alias of "
                   "phone.start_ai_voice_session that also attempts to dial the "
                   "destination first if no active call is given.")
        def phone_start_ai_call(destination: Str = "", call_id: Str = "",
                                objective: Str = "", style: Str = "",
                                language: Str = "", accent: Str = ""):
            if not (call_id or ""):
                placed = pm.place_call(destination or "", sim="",
                                       authorized=False)
                call_id = placed.get("call_id", "")
                return {"ok": True, "placed": placed, "session": None,
                        "note": "call placed; AI session not started - use "
                                "phone.start_ai_voice_session on the active call"}
            return {"ok": True, "session": pm.start_ai_session(
                call_id, objective=objective or "", style=style or None,
                language=language or "", accent=accent or "")}

        @self._reg("phone.stop_ai_call", "Stop an AI voice session. Alias of "
                   "phone.stop_ai_voice_session.")
        def phone_stop_ai_call(session_id: str = ""):
            return pm.stop_ai_session(session_id)

        @self._reg("phone.get_backend",
                   "Report which backend is active and why it was selected.")
        def phone_get_backend():
            return pm.get_backend()

        @self._reg("phone.poll_health", "Force a backend poll + health check.")
        def phone_poll_health():
            try:
                pm.poll_backend()
            except Exception:
                pass
            return pm.health()

        @self._reg("phone.get_call_transcript", "Stored transcript for a call.")
        def phone_get_call_transcript(call_id: str):
            return pm.call_transcript(call_id)

        @self._reg("phone.get_call_summary", "Generate/retrieve call summary.")
        def phone_get_call_summary(call_id: str):
            return pm.call_summary(call_id)

        @self._reg("phone.list_speaking_styles",
                   "List available speaking styles/registers (india_*, global_*).")
        def phone_list_speaking_styles():
            return {"styles": pm.list_styles()}

        @self._reg("phone.get_call_conduct",
                   "Return the speaking-style conduct brief for a call - the "
                   "behaviour instructions that steer the AI voice backend.")
        def phone_get_call_conduct(call_id: str):
            return pm.conversation_brief(call_id)

        @self._reg("phone.list_languages",
                   "List supported spoken languages. India's 22 scheduled "
                   "languages + major world languages (ISO 639 codes). "
                   "india_only=true returns just India's.")
        def phone_list_languages(india_only: Bool = False):
            return {"languages": pm.list_languages(india_only=bool(india_only))}

        @self._reg("phone.detect_language",
                   "Auto-detect the best language + accent for a phone number "
                   "(e.g. an Indian number -> Hindi/Hinglish/regional; +1 -> "
                   "English; +81 -> Japanese). Returns country + candidates.")
        def phone_detect_language(number: str):
            return pm.detect_language_for_call(number)

        # ---- Call policies ---- #
        @self._reg("phone.list_call_policies", "List call policies.")
        def phone_list_call_policies():
            return {"policies": pm.list_policies()}

        @self._reg("phone.create_call_policy", "Create an incoming-call policy.")
        def phone_create_call_policy(name: str, policy: Any):
            return pm.create_policy(name, policy if isinstance(policy, dict)
                                    else json.loads(policy))

        @self._reg("phone.update_call_policy", "Update an incoming-call policy.")
        def phone_update_call_policy(name: str, policy: Any):
            return pm.update_policy(name, policy if isinstance(policy, dict)
                                    else json.loads(policy))

        @self._reg("phone.delete_call_policy", "Delete an incoming-call policy.")
        def phone_delete_call_policy(name: str):
            return pm.delete_policy(name)

        @self._reg("phone.enable_auto_answer",
                   "Enable autonomous answering (policies still gate which calls).")
        def phone_enable_auto_answer():
            return pm.enable_auto_answer()

        @self._reg("phone.disable_auto_answer", "Disable autonomous answering.")
        def phone_disable_auto_answer():
            return pm.disable_auto_answer()

        # ---- System ---- #
        @self._reg("phone.health", "Health check.")
        def phone_health():
            return pm.health()

        @self._reg("phone.version", "Version info.")
        def phone_version():
            return pm.version()

        @self._reg("phone.reconnect", "Request transport reconnect.")
        def phone_reconnect():
            return pm.reconnect()

        @self._reg("phone.get_logs", "Retrieve audit logs.")
        def phone_get_logs(limit: Int = 100):
            return {"logs": pm.get_logs(limit or 100)}

        @self._reg("phone.emergency_stop", "EMERGENCY STOP - halt all AI calling.")
        def phone_emergency_stop():
            return pm.emergency_stop()
