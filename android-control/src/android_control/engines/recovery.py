"""Recovery & self-healing engine (§21–22, §32): reconnect, wait-for-device,
reboot-recovery, capability refresh. Never crashes the fleet for one device.
"""
from __future__ import annotations

import time

from ..config import Settings
from .base import EngineBase


class RecoveryEngine(EngineBase):
    def __init__(self, transport, settings: Settings):
        super().__init__(transport, settings)

    def wait_for_device(self, serial: str, timeout_s: float = 90.0,
                        poll: float = 1.0) -> bool:
        """Wait until adb reports the device as 'device' (not offline)."""
        t0 = time.monotonic()
        while time.monotonic() - t0 < timeout_s:
            if self._adb_state(serial) == "device":
                return True
            time.sleep(poll)
        return False

    def adb_reconnect(self, serial: str) -> bool:
        """adb reconnect for a specific transport (wireless)."""
        res = self._adb(serial, ["reconnect"])
        return res.ok

    def restart_adb_server(self) -> None:
        self._adb(None, ["kill-server"])
        self._adb(None, ["start-server"])
        time.sleep(1.5)

    def _adb_state(self, serial: str) -> str:
        res = self._adb(None, ["devices"])
        for ln in res.lines():
            if ln.startswith(serial + "\t"):
                return ln.split("\t", 1)[1].strip()
        return "offline"

    def recover(self, serial: str, *, host: str = "", port: int = 0,
                wait_s: float = 90.0) -> bool:
        """Best-effort recovery for a single device. Returns True if back to
        'device' state."""
        attempts = [
            ("reconnect", lambda: self.adb_reconnect(serial)),
        ]
        if host and port:
            attempts.append(
                ("tcp-reconnect", lambda: self._adb(serial, ["connect", f"{host}:{port}"]) or True))
        for name, fn in attempts:
            try:
                fn()
            except Exception:
                pass
            if self.wait_for_device(serial, timeout_s=min(wait_s, 15)):
                return True
        return self._adb_state(serial) == "device"

    def mark_boot_pending(self, session) -> None:
        session.connection_state = "rebooting"
        session.adb_state = "offline"
