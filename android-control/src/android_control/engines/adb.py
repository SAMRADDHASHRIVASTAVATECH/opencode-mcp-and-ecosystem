"""ADB engine (§9): adb server lifecycle, device listing, connect/disconnect,
pair, forward/reverse, get-state, plus passthrough to the transport.
"""
from __future__ import annotations

from typing import List, Tuple

from ..config import Settings
from .base import EngineBase


class AdbEngine(EngineBase):
    def __init__(self, transport, settings: Settings):
        super().__init__(transport, settings)

    # -- server lifecycle --------------------------------------------------
    def start_server(self) -> bool:
        res = self._adb(None, ["start-server"])
        return res.ok

    def kill_server(self) -> bool:
        res = self._adb(None, ["kill-server"])
        return res.ok

    def version(self) -> str:
        res = self._adb(None, ["version"])
        m = None
        import re
        mm = re.search(r"version\s+([\d.]+)", res.stdout)
        return mm.group(1) if mm else res.stdout.strip()

    # -- listing -----------------------------------------------------------
    def devices(self) -> List[Tuple[str, str]]:
        """Return [(serial, state)] for attached devices (usb + wireless)."""
        res = self._adb(None, ["devices"])
        out = []
        for ln in res.lines():
            if "\t" not in ln or ln.startswith("List"):
                continue
            serial, state = ln.split("\t", 1)
            serial, state = serial.strip(), state.strip()
            if serial:
                out.append((serial, state))
        return out

    # -- connect / disconnect ---------------------------------------------
    def connect(self, host: str, port: int = 5555) -> bool:
        res = self._adb(None, ["connect", f"{host}:{port}"],
                        timeout_s=self.settings.adb_connect_timeout_s)
        return res.ok

    def disconnect(self, host: str = "", port: int = 0) -> bool:
        target = f"{host}:{port}" if host else ""
        args = ["disconnect"] + ([target] if target else [])
        res = self._adb(None, args)
        return res.ok

    def pair(self, host: str, port: int, pairing_code: str) -> bool:
        """Pair with a wireless-debugging device (Android 11+). Requires the
        six-digit code shown by the device."""
        import subprocess
        # `adb pair host:port code` needs stdin-free; run directly.
        res = self._adb(None, ["pair", f"{host}:{port}", pairing_code],
                        timeout_s=self.settings.adb_connect_timeout_s)
        return res.ok

    def state(self, serial: str) -> str:
        for s, st in self.devices():
            if s == serial:
                return st
        return "offline"

    def reconnect(self, serial: str) -> bool:
        res = self._adb(serial, ["reconnect"])
        return res.ok

    # -- port forwarding ---------------------------------------------------
    def forward(self, serial: str, local: str, remote: str) -> bool:
        res = self._adb(serial, ["forward", local, remote])
        return res.ok

    def reverse(self, serial: str, remote: str, local: str) -> bool:
        res = self._adb(serial, ["reverse", remote, local])
        return res.ok
