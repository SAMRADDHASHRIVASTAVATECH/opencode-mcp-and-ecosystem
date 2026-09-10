"""AndroidBridge telephony backend (spec section 9, phase 1/5).

Connects the control plane to the real Android phone app over a secure bridge
(the phone app is the AUTHORITATIVE device source). This backend only reports
capabilities it learns from the device probe - it never fabricates SIM audio,
call control or AI-cellular capabilities. The Android phone app ships in the
android/ module and must be running + reachable for this to be live.

When no bridge is configured/reachable, operations raise structured errors
(NotConfigured / NetworkUnavailable / UnsupportedOnThisDevice) rather than
pretending. Use OLCAP_ANDROID_BRIDGE_URL to point at the phone's bridge.
"""
from __future__ import annotations

from ..model import DeviceCapabilities
from ..telephony import TelephonyBackend
from ..errors import NetworkUnavailable


class NotConfigured(Exception):
    code = "NOT_CONFIGURED"
    def __init__(self, message="", **ctx):
        super().__init__(message or "android bridge not configured")
        self.ctx = ctx


class AndroidBridgeBackend(TelephonyBackend):
    name = "android_bridge"

    def __init__(self, config=None):
        self.cfg = config
        self.url = (config.android_bridge_url if config else "").rstrip("/")
        self._caps_cache = None

    def configured(self) -> bool:
        return bool(self.url)

    def _client(self):
        if not self.configured():
            raise NotConfigured(
                "android bridge not configured: set OLCAP_ANDROID_BRIDGE_URL to the "
                "phone's OLCAP bridge endpoint")
        try:
            import httpx
        except ImportError as e:  # pragma: no cover
            raise NotConfigured("httpx is required for the android bridge backend") from e
        return httpx.Client(base_url=self.url, timeout=10)

    def _get(self, path: str):
        try:
            r = self._client().get(path)
        except Exception as e:
            raise NetworkUnavailable(f"android bridge unreachable at {self.url}: {e}")
        if r.status_code >= 400:
            raise NetworkUnavailable(f"android bridge -> HTTP {r.status_code}")
        return r.json()

    # ---- capabilities: honest probe or explicit not-live -------------- #
    def capabilities(self) -> DeviceCapabilities:
        if not self.configured():
            # Return a truthful, not-connected report.
            return DeviceCapabilities(device_attached=False,
                                      source="android_bridge(not-connected)")
        try:
            data = self._get("/v1/capabilities")
        except NetworkUnavailable:
            return DeviceCapabilities(device_attached=False,
                                      source="android_bridge(unreachable)")
        # Only copy booleans the device actually reported.
        c = DeviceCapabilities(device_attached=True, source="android_bridge")
        for k in ("call_state_monitoring", "cellular_call_control",
                  "call_audio_capture", "call_audio_injection",
                  "ai_cellular_conversation", "provider_realtime_voice",
                  "voip_available", "local_ai_pipeline", "foreground_service",
                  "accessibility_control", "telecom_integration", "multi_sim",
                  "bluetooth_call_audio", "default_phone_app"):
            if k in data:
                setattr(c, k, bool(data[k]))
        return c

    def device_status(self) -> dict:
        if not self.configured():
            return {"source": self.name, "online": False,
                    "note": "bridge not configured"}
        return self._get("/v1/device")

    def network_status(self) -> dict:
        if not self.configured():
            return {"source": self.name, "online": False}
        return self._get("/v1/network")

    def sim_slots(self) -> list:
        if not self.configured():
            return []
        data = self._get("/v1/sims")
        return data if isinstance(data, list) else data.get("sim_slots", [])

    # ---- call control: proxy to device, honest on unsupported ---------- #
    def dial(self, destination, sim="", call_id=""):
        d = self._post("/v1/call/dial",
                       {"destination": destination, "sim": sim, "call_id": call_id})
        return d

    def answer(self, call_id): return self._post("/v1/call/answer", {"call_id": call_id})
    def reject(self, call_id): return self._post("/v1/call/reject", {"call_id": call_id})
    def hangup(self, call_id): return self._post("/v1/call/hangup", {"call_id": call_id})
    def hold(self, call_id): return self._post("/v1/call/hold", {"call_id": call_id})
    def resume(self, call_id): return self._post("/v1/call/resume", {"call_id": call_id})
    def mute(self, call_id): return self._post("/v1/call/mute", {"call_id": call_id})
    def unmute(self, call_id): return self._post("/v1/call/unmute", {"call_id": call_id})
    def transfer(self, call_id, destination):
        return self._post("/v1/call/transfer",
                          {"call_id": call_id, "destination": destination})
    def send_dtmf(self, call_id, digits):
        return self._post("/v1/call/dtmf", {"call_id": call_id, "digits": digits})

    def _post(self, path, body):
        if not self.configured():
            raise NotConfigured("android bridge not configured")
        try:
            r = self._client().post(path, json=body)
        except Exception as e:
            raise NetworkUnavailable(f"android bridge unreachable: {e}")
        if r.status_code == 501:
            from ..errors import UnsupportedOnThisDevice
            raise UnsupportedOnThisDevice("the device reported this operation "
                                          "unsupported", operation=path)
        if r.status_code >= 400:
            from ..errors import CallFailed
            raise CallFailed(f"android bridge -> HTTP {r.status_code}: {r.text[:200]}")
        return r.json()

    def attach_call(self, number, direction, sim, call_id):
        return {"ref": call_id}
