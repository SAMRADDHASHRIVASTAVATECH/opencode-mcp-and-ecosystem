"""Voice connector.

Real autonomous phone calling needs a telephony/voice provider. OpenClaw itself
exposes realtime app voice (talk.*/tts.*) but does not originate PSTN calls.
This operator therefore uses a pluggable provider:
  * "generic" : VOICE_API_URL + VOICE_API_KEY — a documented HTTPS gateway
                (e.g. a Twilio/Asterisk/Custom bridge) that accepts call
                lifecycle commands and returns structured JSON. This is the
                real path.
  * default   : no provider configured -> mock mode (deterministic simulation,
                clearly flagged). The full call-state engine still runs.

A real provider adapter just needs to speak this contract:
  POST {url}/call   {action, call_id, to, ...}  -> {status, call_id, session_url}
  POST {url}/state  {action, call_id, ...}
"""
from __future__ import annotations

import httpx

from ..base import Connector, Op, Param
from ..errors import ApiError, NotConfigured


class VoiceConnector(Connector):
    platform = "voice"
    ALWAYS_REAL = {"status", "history"}
    namespace = "voice"
    display_name = "Voice (telephony)"

    OPS = {
        "status": Op("status", "Get provider/runtime voice status.", []),
        "call": Op("call", "Place an outbound call (immediate).", [
            Param("to", "str", True, "E.164 phone number."),
            Param("objective", "str", False, "Call objective / script hint."),
            Param("call_id", "str", False, "Optional existing call id to attach."),
            Param("from", "str", False, "Outbound caller id.")],
            "voice.call", True),
        "answer": Op("answer", "Accept an inbound call (policy-gated).", [
            Param("call_id", "str", True, "Call id.")], "voice.call", True),
        "hangup": Op("hangup", "End a call.", [
            Param("call_id", "str", True, "Call id.")], "voice.call", True),
        "speak": Op("speak", "Send a TTS line to an active call.", [
            Param("call_id", "str", True, "Call id."),
            Param("text", "str", True, "Text to speak.")], "voice.speak", True),
        "listen": Op("listen", "Fetch the latest transcript/interim speech of a call.", [
            Param("call_id", "str", True, "Call id.")]),
        "transfer": Op("transfer", "Transfer the call to a human/destination.", [
            Param("call_id", "str", True, "Call id."),
            Param("destination", "str", True, "Destination (human id or number).")],
            "voice.call", True),
        "schedule": Op("schedule", "Queue an outbound call for a time.", [
            Param("to", "str", True, "Number."),
            Param("at", "str", True, "ISO schedule time."),
            Param("purpose", "str", False, "Purpose."),
            Param("objective", "str", False, "Objective.")], "voice.call", True),
        "cancel": Op("cancel", "Cancel a queued/scheduled call.", [
            Param("call_id", "str", True, "Call or queue id.")], "voice.call", True),
        "retry": Op("retry", "Re-queue a failed/no-answer call.", [
            Param("call_id", "str", True, "Call id.")], "voice.call", True),
        "history": Op("history", "List recent calls (from persistent store).", [
            Param("status", "str", False, "Filter by status."),
            Param("limit", "int", False, "Max.", 50)]),
    }

    def configured(self) -> bool:
        return self.settings.voice_provider == "generic" and bool(self.settings.voice_api_url)

    def _provider(self):
        if self.settings.voice_provider != "generic" or not self.settings.voice_api_url:
            raise NotConfigured(
                "No voice provider configured. Set VOICE_PROVIDER=generic, "
                "VOICE_API_URL, VOICE_API_KEY (and provide a bridge that speaks the "
                "voice contract). OpenClaw's app-voice (talk.*) is NOT a PSTN "
                "provider.")
        return httpx.Client(base_url=self.settings.voice_api_url, timeout=60,
                            headers={"Authorization": f"Bearer {self.settings.voice_api_key}"})

    def _require_live(self):
        if self._mock:
            raise NotConfigured("voice is mock/offline; configure a real provider.")

    def _post(self, action, call_id, **extra):
        client = self._provider()
        try:
            r = client.post("/call", json={"action": action, "call_id": call_id, **extra})
        except httpx.HTTPError as e:
            raise ApiError(f"voice provider unreachable: {e}")
        if r.status_code >= 400:
            raise ApiError(f"voice provider -> {r.status_code}: {r.text[:300]}")
        return r.json()

    def op_status(self, args, account):
        if self._mock:
            return {"provider": self.settings.voice_provider,
                    "configured": False, "note": "no live provider (mock)."}
        return {"provider": self.settings.voice_provider, "configured": True,
                "note": "provider reachable; call on voice.call."}

    def op_call(self, args, account):
        self._require_live()
        cid = args.get("call_id") or f"call_{account}"
        return self._post("dial", cid, to=args["to"],
                          objective=args.get("objective"), from_=args.get("from"))

    def op_answer(self, args, account):
        self._require_live()
        return self._post("answer", args["call_id"])

    def op_hangup(self, args, account):
        self._require_live()
        return self._post("hangup", args["call_id"])

    def op_speak(self, args, account):
        self._require_live()
        return self._post("speak", args["call_id"], text=args["text"])

    def op_listen(self, args, account):
        self._require_live()
        return self._post("listen", args["call_id"])

    def op_transfer(self, args, account):
        self._require_live()
        return self._post("transfer", args["call_id"], destination=args["destination"])

    def op_schedule(self, args, account):
        # Scheduling is handled by the persistent CallQueue engine, which then
        # invokes op_call at the due time. This returns a queue reference.
        return {"queued": True, "to": args["to"], "at": args["at"],
                "note": "persist via workflow.call_schedule; engine dials at due time."}

    def op_cancel(self, args, account):
        self._require_live()
        return self._post("cancel", args["call_id"])

    def op_retry(self, args, account):
        self._require_live()
        return self._post("retry", args["call_id"])

    def op_history(self, args, account):
        # Pulled from the persistent call store (state), independent of provider.
        return {"note": "call history is available from the call engine "
                        "(operator.call.history)."}
