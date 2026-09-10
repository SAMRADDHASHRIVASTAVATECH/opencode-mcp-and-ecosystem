"""Real ADB telephony backend (optional import of android_control).

Controls the cellular call on a physical Android device over ADB (USB or
wireless pairing). No phone-side app; the supervisor self-heals disconnects.

Capability boundary (honest):
  * dial / reject / answer / hangup / DTMF   -> real, via am start + input keyevent
  * call-state monitoring                    -> real, via dumpsys telephony.registry
  * sim slots                                -> reported from getprop
  * call audio capture / injection, AI session, mute/hold/transfer, sim
    selection                               -> UNSUPPORTED over plain ADB
"""
from __future__ import annotations

import re
import time
from typing import Any

from ..errors import CallFailed, CapabilityUnsupported, OlcapError
from ..model import DeviceCapabilities
from ..telephony import TelephonyBackend

KEYCODE_CALL = 5
KEYCODE_ENDCALL = 6
_KEYPAD = {"0": 7, "1": 8, "2": 9, "3": 10, "4": 11,
           "5": 12, "6": 13, "7": 14, "8": 15, "9": 16,
           "*": 17, "#": 18}


def normalize_destination(number: str, country_code: str = "+91") -> str:
    num = re.sub(r"[\s\-()./]", "", number or "")
    if num.startswith("00"):
        num = "+" + num[2:]
    if num.isdigit() and len(num) == 10:
        return (country_code or "+91") + num
    if num.isdigit():
        return "+" + num
    return num


class AdbTelephonyBackend(TelephonyBackend):
    name = "adb"

    def __init__(self, supervisor: Any = None, country_code: str = "+91"):
        self.svc = supervisor
        self.country_code = country_code or "+91"
        self._dtmf_gap_s = 0.15
        self._idle_streak = 0
        self._call_active = False

    # ---- presence ------------------------------------------------ //
    def available(self) -> bool:
        return bool(self.svc and self.svc.available())

    # ---- capability report (honest) ------------------------------ //
    def capabilities(self) -> DeviceCapabilities:
        online = self.svc.online() if self.svc else False
        c = DeviceCapabilities(device_attached=online,
                               source="backend:adb")
        c.cellular_call_control = online
        c.call_state_monitoring = online
        c.call_audio_capture = False
        c.call_audio_injection = False
        c.ai_cellular_conversation = False
        c.adb = True
        c.wireless_adb = bool(
            self.svc and self.svc._session
            and getattr(self.svc._session, "connection_type", "")
            and "wifi" in self.svc._session.connection_type.lower())
        c.sim_selection = False
        c.provider_realtime_voice = False
        c.voip_available = False
        c.multi_sim = len(self.sim_slots()) > 1
        return c

    # ---- device info / sim --------------------------------------- //
    def _prop(self, name: str) -> str:
        try:
            return (self.svc.getprop(name) or "").strip()
        except Exception:
            return ""

    def device_status(self) -> dict:
        p = self.svc.profile() if self.svc else {}
        return {**p, "source": self.name,
                "simulated": False, "online": self.svc.online() if self.svc else False}

    def device_info(self) -> dict:
        p = self.device_status()
        p["getprop"] = {
            "ro.product.model": self._prop("ro.product.model"),
            "ro.product.manufacturer": self._prop("ro.product.manufacturer"),
            "ro.build.version.release": self._prop("ro.build.version.release"),
        }
        return p

    def sim_slots(self) -> list:
        mode = self._prop("persist.radio.multisim.config").lower()
        count = 2 if mode in ("dsds", "dsda", "tsts") else 1
        slots = []
        for i in range(count):
            state = self._prop(f"gsm.sim.state.{i}") or self._prop(f"gsm.sim.state{i}")
            alpha = self._prop(f"gsm.sim.operator.alpha.{i}") or \
                    self._prop("gsm.sim.operator.alpha")
            slots.append({
                "slot": f"SIM{i + 1}", "index": i,
                "subscription_id": i + 1,
                "carrier": alpha, "operator": alpha,
                "state": state,
                "ready": bool(state and "ready" in state.lower()),
                "active": bool(state),
                "default": i == 0,
            })
        return slots

    def network_status(self) -> dict:
        if not (self.svc and self.svc.online()):
            return {"source": self.name, "online": False, "reason": "device offline",
                    "network_type": "", "signal": None}
        try:
            phone = self.svc.dumpsys("phone") or ""
            m = (re.search(r"dataNetworkType=\w+:\s*(\w+)", phone)
                 or re.search(r"(\w+)\s*networkType", phone))
            return {"source": self.name, "online": True,
                    "network_type": m.group(1) if m else "",
                    "signal": None, "device": self.svc.serial()}
        except Exception as e:
            return {"source": self.name, "online": True,
                    "network_type": "", "signal": None, "error": str(e)}

    # ---- dial / answer / hangup / dtmf --------------------------- //
    def dial(self, destination: str, sim: str = "", call_id: str = "") -> dict:
        if not (self.svc and self.svc.online()):
            raise CallFailed("no ADB device attached (supervisor retrying)",
                             code="ADB_DEVICE_OFFLINE")
        num = normalize_destination(destination, self.country_code)
        try:
            out = self.svc.am_call(num) or ""
        except OlcapError as e:
            raise CallFailed(str(e), code="ADB_CALL_INTENT_FAILED") from e
        if re.search(r"\b(Error|Warning|Exception)\b", out, re.I):
            raise CallFailed(f"dial intent failed: {out.strip()}",
                             code="ADB_CALL_INTENT_FAILED")
        self._call_active = True
        self._idle_streak = 0
        return {"dialing": True, "destination": num, "sim": sim or "default",
                "device": self.svc.serial(), "raw": out.strip()[-200:]}

    def answer(self, call_id: str) -> dict:
        self.svc.keyevent(KEYCODE_CALL)
        self._call_active = True
        self._idle_streak = 0
        return {"answered": True}

    def reject(self, call_id: str) -> dict:
        self.svc.keyevent(KEYCODE_ENDCALL)
        return {"rejected": True}

    def hangup(self, call_id: str) -> dict:
        self.svc.keyevent(KEYCODE_ENDCALL)
        self._call_active = False
        self._idle_streak = 0
        return {"hungup": True}

    def send_dtmf(self, call_id: str, digits: str) -> dict:
        sent = []
        for d in str(digits or ""):
            if d not in _KEYPAD:
                raise OlcapError(f"unsupported DTMF digit {d!r}")
            self.svc.keyevent(_KEYPAD[d])
            time.sleep(self._dtmf_gap_s)
            sent.append(d)
        return {"sent": "".join(sent)}

    def hold(self, call_id: str) -> dict:
        raise CapabilityUnsupported(
            f"{self.name}.hold: no in-call audio control over plain ADB",
            capability="hold", backend=self.name)
    def resume(self, call_id: str) -> dict:
        raise CapabilityUnsupported("resume unsupported over ADB",
                                    capability="resume", backend=self.name)
    def mute(self, call_id: str) -> dict:
        raise CapabilityUnsupported(
            "mute unsupported over plain ADB (no audio path)",
            capability="mute", backend=self.name)
    def unmute(self, call_id: str) -> dict:
        raise CapabilityUnsupported("unmute unsupported over ADB",
                                    capability="unmute", backend=self.name)
    def transfer(self, call_id: str, destination: str) -> dict:
        raise CapabilityUnsupported("transfer unsupported over ADB",
                                    capability="transfer", backend=self.name)
    def start_audio(self, call_id: str) -> dict:
        raise CapabilityUnsupported(
            "start_audio: no in-call audio capture over plain ADB",
            capability="start_audio", backend=self.name)
    def stop_audio(self, call_id: str) -> dict:
        raise CapabilityUnsupported("stop_audio unsupported over ADB",
                                    capability="stop_audio", backend=self.name)

    # ---- state ------------------------------------------------ //
    def get_state(self, call_id: str) -> dict:
        if call_id and False:
            pass
        return self.poll(call_id)

    def poll(self, call_id: str = "") -> dict:
        """Live call state: idle|ringing|offhook + honest extras."""
        if not (self.svc and self.svc.online()):
            return {"state": "unknown", "error": "device offline",
                    "online": False}
        try:
            mstate, number = self.svc.call_state()
        except OlcapError as e:
            return {"state": "unknown", "error": str(e)}
        if mstate == 2:
            self._idle_streak = 0
            return {"state": "offhook", "number": number, "active": True}
        if mstate == 1:
            self._idle_streak = 0
            return {"state": "ringing", "number": number, "incoming": True}
        # idle
        if self._call_active:
            self._idle_streak += 1
        active = self._call_active and self._idle_streak < 2
        return {"state": "idle", "idle_streak": self._idle_streak,
                "active": active}

    # ---- inbound registration ---------------------------------- //
    def attach_call(self, number: str, direction: str, sim: str, call_id: str) -> dict:
        return {"ref": call_id, "backend": self.name}

    def subscribe(self) -> None:
        pass

    def shutdown(self) -> None:
        if self.svc:
            self.svc.shutdown()