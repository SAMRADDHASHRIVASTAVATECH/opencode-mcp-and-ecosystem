"""Device information engine (§18): machine-readable profile for every device.
"""
from __future__ import annotations

import re

from ..config import Settings
from .base import EngineBase


class InfoEngine(EngineBase):
    def __init__(self, transport, settings: Settings):
        super().__init__(transport, settings)

    def props(self, serial: str, *props: str) -> dict:
        out = {}
        for p in props:
            out[p] = self.getprop(serial, p)
        return out

    def getprop(self, serial: str, prop: str) -> str:
        res = self._shell(serial, f"getprop {prop}")
        v = res.stdout.strip()
        return v if v and v != "[]" else ""

    def battery(self, serial: str) -> dict:
        out = self._shell(serial, "dumpsys battery")
        return {
            "level": _first_int(r"level:\s*(\d+)", out.stdout),
            "status": _first_int(r"status:\s*(\d+)", out.stdout),
            "charging": _first_int(r"powered:\s*(\d+)", out.stdout),
        }

    def network(self, serial: str) -> dict:
        wifi = self._shell(serial, "dumpsys wifi | grep -E 'Wi-Fi is|SSID' | head -3")
        ip = self._shell(serial, "ip -f inet addr show wlan0 2>/dev/null | grep inet")
        m = re.search(r"inet\s+(\d+\.\d+\.\d+\.\d+)", ip.stdout)
        return {
            "wifi_info": wifi.stdout.strip()[:200],
            "ip": m.group(1) if m else "",
        }

    def storage(self, serial: str) -> dict:
        out = self._shell(serial, "df /sdcard")
        for ln in out.lines():
            parts = ln.split()
            if parts and parts[0].endswith("/sdcard") and len(parts) >= 5:
                return {"blocks": parts[1], "used": parts[2],
                        "avail": parts[3], "capacity": parts[4]}
        return {}

    def display(self, serial: str) -> dict:
        size = self._shell(serial, "wm size")
        dens = self._shell(serial, "wm density")
        return {"size": _first(r"Physical size:\s*(\S+)", size.stdout),
                "density": _first(r"Physical density:\s*(\S+)", dens.stdout)}

    def current_focus(self, serial: str) -> dict:
        out = self._shell(serial, "dumpsys window | grep mCurrentFocus")
        m = re.search(r"mCurrentFocus=Window\{\S+\s+u\d+\s+(\S+)/(\S+)\}", out.stdout)
        if m:
            return {"package": m.group(1), "activity": m.group(2)}
        return {"package": "", "activity": ""}

    def boot_completed(self, serial: str) -> bool:
        res = self._shell(serial, "getprop sys.boot_completed")
        return res.stdout.strip() == "1"

    def profile(self, serial: str) -> dict:
        """Full machine-readable profile (mirrors DeviceSession fields)."""
        manu = self.getprop(serial, "ro.product.manufacturer")
        model = self.getprop(serial, "ro.product.model")
        version = self.getprop(serial, "ro.build.version.release")
        sdk = self.getprop(serial, "ro.build.version.sdk")
        arch = self.getprop(serial, "ro.product.cpu.abi")
        android_id = self._shell(serial, "settings get secure android_id").stdout.strip()
        focus = self.current_focus(serial)
        return {
            "manufacturer": manu, "model": model,
            "android_version": version, "sdk_level": sdk, "arch": arch,
            "android_id": android_id or "",
            "current_package": focus["package"],
            "current_activity": focus["activity"],
            "display": self.display(serial),
            "battery": self.battery(serial),
            "storage": self.storage(serial),
            "network": self.network(serial),
        }


def _first_int(regex, text):
    m = re.search(regex, text)
    try:
        return int(m.group(1)) if m else None
    except (ValueError, IndexError):
        return None


def _first(regex, text):
    m = re.search(regex, text)
    return m.group(1) if m else ""
