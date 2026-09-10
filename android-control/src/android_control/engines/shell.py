"""Android shell engine: exposes ``am``, ``pm``, ``cmd``, ``settings``,
``input``, ``dumpsys``, ``getprop``, ``logcat``, ``screencap``,
``screenrecord``, ``wm``, ``svc`` and free-form shell (§10). Detects Android
version differences and refuses destructive host-style commands.
"""
from __future__ import annotations

import time
from typing import List, Optional

from .. import errors
from ..config import Settings
from .base import EngineBase, safe_shell_command


class ShellEngine(EngineBase):
    def __init__(self, transport, settings: Settings):
        super().__init__(transport, settings)

    # -- low-level ---------------------------------------------------------
    def shell(self, serial: str, command: str,
              timeout_s: Optional[float] = None) -> str:
        """Run an arbitrary (checked) shell command on the device."""
        cmd = safe_shell_command(command)
        if not cmd:
            return ""
        res = self._shell(serial, cmd, timeout_s)
        if not res.ok:
            raise errors.CommandFailedError(
                f"shell[{serial}] failed: {res.error or res.stdout[:200]}")
        return res.stdout

    def command(self, serial: str, *argv: str,
                timeout_s: Optional[float] = None) -> str:
        """Run a tool command that does not need a shell, e.g. ``exec-out``."""
        res = self._run_ok(serial, ["exec-out", *argv], timeout_s)
        return res.stdout

    # -- getprop -----------------------------------------------------------
    def getprop(self, serial: str, prop: str) -> str:
        try:
            res = self._shell_ok(serial, f"getprop {prop}")
        except errors.CommandFailedError:
            return ""
        v = res.stdout.strip()
        return v if v and v != "[]" else ""

    # -- dumpsys -----------------------------------------------------------
    def dumpsys(self, serial: str, service: str,
                args: Optional[List[str]] = None) -> str:
        c = f"dumpsys {service}"
        if args:
            c += " " + " ".join(args)
        return self.shell(serial, c, timeout_s=self.settings.long_timeout_s)

    # -- am / pm / cmd convenience (delegated to apps/intents where richer) --
    def am(self, serial: str, *argv: str) -> str:
        return self._shell_out(serial, "am", argv)

    def pm(self, serial: str, *argv: str) -> str:
        return self._shell_out(serial, "pm", argv, long=True)

    def cmd(self, serial: str, *argv: str) -> str:
        return self._shell_out(serial, "cmd", argv)

    def settings(self, serial: str, *argv: str) -> str:
        return self._shell_out(serial, "settings", argv)

    def _shell_out(self, serial, tool, argv, long=False) -> str:
        cmd = tool + " " + " ".join(str(a) for a in argv)
        to = self.settings.long_timeout_s if long else None
        res = self._shell(serial, cmd, to)
        if not res.ok:
            raise errors.CommandFailedError(
                f"{tool}[{serial}] failed: {res.error or res.stdout[:200]}")
        return res.stdout

    # -- logs --------------------------------------------------------------
    def logcat(self, serial: str, filter_expr: str = "*:D",
               lines: int = 200) -> List[str]:
        cmd = f"logcat -d {filter_expr} -t {int(lines)}"
        out = self.shell(serial, cmd, timeout_s=self.settings.long_timeout_s)
        return [ln for ln in out.splitlines()]

    def clear_logcat(self, serial: str) -> None:
        self.shell(serial, "logcat -c")

    # -- reboot ------------------------------------------------------------
    def reboot(self, serial: str, wait_for_device_s: float = 45.0) -> None:
        self.shell(serial, "reboot")
        # not waiting here; recovery engine handles re-appearance

    # -- misc system info ---------------------------------------------------
    def sdk_level(self, serial: str) -> str:
        return self.getprop(serial, "ro.build.version.sdk")

    def android_version(self, serial: str) -> str:
        return self.getprop(serial, "ro.build.version.release")

    def model(self, serial: str) -> str:
        return self.getprop(serial, "ro.product.model")

    def manufacturer(self, serial: str) -> str:
        return self.getprop(serial, "ro.product.manufacturer")

    def arch(self, serial: str) -> str:
        return self.getprop(serial, "ro.product.cpu.abi")
