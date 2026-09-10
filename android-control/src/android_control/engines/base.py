"""Shared engine context and helpers for low-level command execution with
deterministic device targeting.
"""
from __future__ import annotations

from typing import Optional, Sequence

from ..config import Settings
from ..transport import CommandResult, CommandResultError
from .. import errors


class EngineBase:
    def __init__(self, transport, settings: Settings):
        self.t = transport
        self.settings = settings

    # -- device-targeted raw command ---------------------------------------
    def _adb(self, serial: Optional[str], args: Sequence[str],
             timeout_s: Optional[float] = None) -> CommandResult:
        res = self.t.run(args, timeout_s=timeout_s, serial=serial)
        return res

    def _run_ok(self, serial: Optional[str], args: Sequence[str],
                timeout_s: Optional[float] = None) -> CommandResult:
        res = self._adb(serial, args, timeout_s)
        if not res.ok:
            raise CommandResultError(res)
        return res

    # -- device-targeted shell ---------------------------------------------
    def _shell(self, serial: Optional[str], command: str,
               timeout_s: Optional[float] = None) -> CommandResult:
        return self._adb(serial, ["shell", command], timeout_s)

    def _shell_ok(self, serial: Optional[str], command: str,
                  timeout_s: Optional[float] = None) -> CommandResult:
        res = self._shell(serial, command, timeout_s)
        if not res.ok:
            raise CommandResultError(res)
        return res


def safe_shell_command(command: str) -> str:
    """Sanity-check a single shell command string before it is sent to a
    device. Blocks a handful of especially destructive host-affecting patterns
    as a last line of defence; normal Android shell usage is allowed."""
    lowered = command.strip().lower()
    if not lowered:
        return ""
    if lowered.startswith(("rm -rf /", "mkfs.", "dd if=", "> /dev/", ":(){ :|:& };:")):
        raise errors.InjectionDeniedError(f"refusing potentially destructive "
                                          f"shell command: {command[:60]}")
    return command
