"""PowerShell backend with a testable executor."""

from __future__ import annotations

import json
import os
import platform
import shutil
import subprocess
from typing import Any, Protocol

from windows_mcp.config import SETTINGS, Settings
from windows_mcp.errors import BackendError, TimeoutErr, UnsupportedError


class Executor(Protocol):
    def run(self, script: str, timeout: int) -> str: ...


class SubprocessExecutor:
    def __init__(self, binary: str) -> None:
        self.binary = binary

    def run(self, script: str, timeout: int) -> str:
        # Encoded command avoids quoting hell; still our script only.
        completed = subprocess.run(
            [
                self.binary,
                "-NoProfile",
                "-NonInteractive",
                "-ExecutionPolicy",
                "Bypass",
                "-Command",
                script,
            ],
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        if completed.returncode != 0:
            err = (completed.stderr or completed.stdout or "").strip()[:4000]
            raise BackendError("PowerShell failed", {"stderr": err, "code": completed.returncode})
        return completed.stdout


class UnavailableExecutor:
    def run(self, script: str, timeout: int) -> str:
        raise UnsupportedError(
            "Local Windows APIs are unavailable on this host. "
            "Run this MCP on Windows, or configure WIN_MCP_REMOTE_HOST with WinRM (optional).",
            {"platform": platform.system()},
        )


def find_powershell() -> str | None:
    if os.environ.get("WIN_MCP_PWSH"):
        return os.environ["WIN_MCP_PWSH"]
    for name in ("pwsh", "powershell"):
        found = shutil.which(name)
        if found:
            return found
    return None


class PowerShellBackend:
    def __init__(self, executor: Executor | None = None, settings: Settings | None = None) -> None:
        self.settings = settings or SETTINGS
        if executor is not None:
            self.executor = executor
            self.available = True
            return
        if platform.system() == "Windows":
            binary = find_powershell()
            if binary:
                self.executor = SubprocessExecutor(binary)
                self.available = True
                return
        self.executor = UnavailableExecutor()
        self.available = False

    def json(self, script: str) -> Any:
        wrapped = (
            "$ErrorActionPreference = 'Stop'\n"
            + script
            + "\n"
        )
        try:
            raw = self.executor.run(wrapped, self.settings.timeout)
        except subprocess.TimeoutExpired as exc:
            raise TimeoutErr("PowerShell timed out") from exc
        raw = raw.strip()
        if not raw:
            return None
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            return {"raw": raw[:8000]}

    def platform_info(self) -> dict[str, Any]:
        return {
            "os": platform.system(),
            "release": platform.release(),
            "python": platform.python_version(),
            "powershell_available": self.available and not isinstance(self.executor, UnavailableExecutor),
            "read_only": self.settings.read_only,
            "allow_destructive": self.settings.allow_destructive,
        }


BACKEND = PowerShellBackend()
