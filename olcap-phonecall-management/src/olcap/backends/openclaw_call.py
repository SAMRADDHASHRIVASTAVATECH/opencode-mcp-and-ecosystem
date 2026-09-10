"""OpenClaw voice-call fallback backend.

Thin, honest fallback used only when the ADB backend cannot reach a device.
`available()` requires a real ``openclaw`` CLI on PATH; everything beyond
placing a call is reported as unsupported -- we never fake call-state or audio.
"""
from __future__ import annotations

import shutil
import subprocess

from ..errors import CallFailed, CapabilityUnsupported
from ..model import DeviceCapabilities
from ..telephony import TelephonyBackend


class OpenClawCallBackend(TelephonyBackend):
    name = "openclaw_voice"

    def __init__(self, executable: str = ""):
        self.executable = executable or shutil.which("openclaw") or ""

    # ---- presence ------------------------------------------------ //
    def available(self) -> bool:
        if not self.executable:
            return False
        try:
            r = subprocess.run([self.executable, "--version"],
                               capture_output=True, text=True, timeout=15)
            return r.returncode == 0
        except Exception:
            return False

    def capabilities(self) -> DeviceCapabilities:
        avail = self.available()
        c = DeviceCapabilities(device_attached=False, source="backend:openclaw_voice")
        c.cellular_call_control = False
        c.call_state_monitoring = False
        c.call_audio_capture = False
        c.call_audio_injection = False
        c.ai_cellular_conversation = False
        c.adb = False
        c.wireless_adb = False
        c.sim_selection = False
        c.provider_realtime_voice = avail
        c.voip_available = avail
        return c

    # ---- device info / sim --------------------------------------- //
    def device_status(self) -> dict:
        return {"source": self.name, "provider": self.name,
                "executable": self.executable, "attached": False,
                "online": self.available(), "simulated": False}

    def sim_slots(self) -> list:
        return []

    def network_status(self) -> dict:
        return {"source": self.name, "online": self.available(),
                "provider": self.name, "network_type": "openclaw", "signal": None}

    # ---- dial (the only real op) --------------------------------- //
    def dial(self, destination: str, sim: str = "", call_id: str = "") -> dict:
        if not self.available():
            raise CallFailed("openclaw CLI not found (cannot dial via provider)",
                             code="PROVIDER_UNAVAILABLE")
        try:
            r = subprocess.run([self.executable, "voice", "call", "--to", destination],
                               capture_output=True, text=True, timeout=180)
        except Exception as e:
            raise CallFailed(f"openclaw voice call failed to start: {e}",
                             code="PROVIDER_CALL_FAILED") from e
        if r.returncode != 0:
            raise CallFailed(r.stderr.strip() or r.stdout.strip()
                             or "openclaw voice call failed",
                             code="PROVIDER_CALL_FAILED")
        return {"dialing": True, "destination": destination, "provider": self.name,
                "raw": r.stdout.strip()[-200:]}

    # ---- unsupported (honest) ------------------------------------ //
    def answer(self, call_id: str) -> dict:
        raise CapabilityUnsupported("answer unsupported via openclaw_voice fallback",
                                    capability="answer", backend=self.name)
    def reject(self, call_id: str) -> dict:
        raise CapabilityUnsupported("reject unsupported via openclaw_voice fallback",
                                    capability="reject", backend=self.name)
    def hangup(self, call_id: str) -> dict:
        raise CapabilityUnsupported("hangup unsupported via openclaw_voice fallback",
                                    capability="hangup", backend=self.name)
    def hold(self, call_id: str) -> dict:
        raise CapabilityUnsupported("hold unsupported", capability="hold",
                                    backend=self.name)
    def resume(self, call_id: str) -> dict:
        raise CapabilityUnsupported("resume unsupported", capability="resume",
                                    backend=self.name)
    def mute(self, call_id: str) -> dict:
        raise CapabilityUnsupported("mute unsupported", capability="mute",
                                    backend=self.name)
    def unmute(self, call_id: str) -> dict:
        raise CapabilityUnsupported("unmute unsupported", capability="unmute",
                                    backend=self.name)
    def transfer(self, call_id: str, destination: str) -> dict:
        raise CapabilityUnsupported("transfer unsupported", capability="transfer",
                                    backend=self.name)
    def send_dtmf(self, call_id: str, digits: str) -> dict:
        raise CapabilityUnsupported("DTMF unsupported via openclaw_voice fallback",
                                    capability="send_dtmf", backend=self.name)

    def get_state(self, call_id: str) -> dict:
        return {"state": "unknown", "provider": self.name,
                "note": "openclaw_voice is call-place only; no call-state"}
    def attach_call(self, number: str, direction: str, sim: str, call_id: str) -> dict:
        return {"ref": call_id, "backend": self.name}
    def subscribe(self) -> None:
        pass
    def shutdown(self) -> None:
        pass