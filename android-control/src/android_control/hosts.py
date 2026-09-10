"""Host-side tool bootstrapping (§3–4): detect, version, locate, validate,
and (where permitted + from trustworthy sources) install missing Windows
tooling. Never re-installs what is already present. No arbitrary downloads.
"""
from __future__ import annotations

import os
import re
import shutil
import subprocess
from pathlib import Path
from typing import Dict, List, Optional

from . import errors
from .config import HostTool, Settings

# Tool registry: canonical Windows-friendly definitions.
TOOL_DEFS: Dict[str, dict] = {
    "python": {"exe": "python", "ver": ["--version"], "source": "https://www.python.org"},
    "adb": {"exe": "adb", "ver": ["version"],
            "source": "https://developer.android.com/tools/releases/platform-tools"},
    "scrcpy": {"exe": "scrcpy", "ver": ["--version"],
               "source": "https://github.com/Genymobile/scrcpy"},
    "platform-tools": {"source": "https://developer.android.com/tools/releases/platform-tools"},
}


def _run(exe: str, args: List[str]) -> str:
    try:
        p = subprocess.run([exe] + args, capture_output=True, text=True,
                           timeout=20, check=False)
        return (p.stdout or "") + (p.stderr or "")
    except (OSError, subprocess.TimeoutExpired):
        return ""


class HostBootstrap:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.tools: Dict[str, HostTool] = {}
        self.install_dir = Path(settings.install_dir).expanduser()
        self.install_dir.mkdir(parents=True, exist_ok=True)

    # -- individual detection ---------------------------------------------
    def _exe_on(self, name: str) -> Optional[str]:
        # explicit settings
        if name == "adb" and self.settings.adb_path:
            return self.settings.adb_path
        if name == "scrcpy" and self.settings.scrcpy_path:
            return self.settings.scrcpy_path
        # platform-tools dir
        if name in ("adb", "adb.exe"):
            if self.settings.platform_tools_dir:
                cand = Path(self.settings.platform_tools_dir) / ("adb.exe" if os.name == "nt" else "adb")
                if cand.exists():
                    return str(cand)
        # PATH
        return shutil.which(name)

    def detect(self, name: str, *, quiet: bool = True) -> HostTool:
        info = TOOL_DEFS[name]
        exe = self._exe_on(info["exe"] if name != "platform-tools" else "adb")
        ht = HostTool(name=name, exe_names=[info["exe"]],
                      source=info["source"], verify_args=info.get("ver", []))
        if exe:
            ht.exe_path = exe
            ht.installed = True
            out = _run(exe, info.get("ver", []))
            v = _extract_version(out)
            if v:
                ht.version = v
            if not quiet:
                print(f"[hosts] {name}: {exe} ({ht.version or 'version?'})")
        return ht

    def check(self, *names: str, quiet: bool = True) -> Dict[str, HostTool]:
        for n in names:
            self.tools[n] = self.detect(n, quiet=quiet)
        return self.tools

    def ensure(self, name: str, *, install: Optional[bool] = None) -> HostTool:
        """Ensure a tool is present. Install only if permitted & installable
        from an official source; otherwise raise ToolNotFoundError with clear
        guidance."""
        ht = self.detect(name, quiet=True)
        if ht.installed and _works(ht):
            return ht
        should_install = self.settings.allow_auto_install if install is None else install
        if should_install:
            if self._try_install(ht):
                ht = self.detect(name, quiet=True)
                if ht.installed and _works(ht):
                    return ht
        raise errors.ToolNotFoundError(
            f"required host tool '{name}' is missing or not usable. "
            f"Official source: {ht.source}. Install it and set AC_ADB_PATH / "
            f"AC_PLATFORM_TOOLS_DIR, or allow auto-install (AC_AUTO_INSTALL=true).")

    def _try_install(self, ht: HostTool) -> bool:
        """Attempt a trustworthy install. Returns True on success.

        We prefer the platform package manager / existing platform-tools
        package rather than downloading binaries from random hosts. On Windows
        this uses winget when available; elsewhere it reports and returns False
        so the caller can surface precise guidance.
        """
        if os.name == "nt":
            winget = shutil.which("winget")
            mapping = {"adb": "Google.PlatformTools",
                       "scrcpy": "Genymobile.scrcpy"}
            pkg = mapping.get(ht.name)
            if winget and pkg:
                try:
                    r = subprocess.run(
                        ["winget", "install", "-e", "--id", pkg,
                         "--accept-source-agreements", "--accept-package-agreements",
                         "--disable-interactivity"],
                        capture_output=True, text=True, timeout=240)
                    return r.returncode == 0
                except (OSError, subprocess.TimeoutExpired):
                    return False
        # Non-Windows or no winget: point to official source (never auto-download).
        return False

    def summary(self) -> List[dict]:
        return [{"name": t.name, "installed": t.installed,
                 "version": t.version, "exe_path": t.exe_path,
                 "source": t.source} for t in self.tools.values()]


def _extract_version(out: str) -> str:
    m = re.search(r"(\d+\.\d+(?:\.\d+)?)", out)
    return m.group(1) if m else ""


def _works(ht: HostTool) -> bool:
    if not ht.exe_path:
        return False
    if not ht.verify_args:
        return True
    exe = ht.exe_path
    # adb has no friendly "version" without the server; try `adb version`
    try:
        p = subprocess.run([exe] + ht.verify_args, capture_output=True,
                           text=True, timeout=20)
        return True
    except Exception:
        return False
