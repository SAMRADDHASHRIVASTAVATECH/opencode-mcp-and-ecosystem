"""Command transport layer.

Two implementations:

* ``AdbTransport`` — shells out to the real ``adb`` binary (the actual control
  interface on a Windows host). Every command is run with an explicit target
  serial when one is supplied.
* ``MockTransport`` — a deterministic, offline, hardware-free stand-in so the
  whole skill is importable and verifiable without a phone (used by
  ``--offline`` and selfchecks). It returns stable, plausible output.
"""
from __future__ import annotations

import os
import re
import shlex
import subprocess
import sys
import time
from pathlib import Path
from typing import List, Optional, Sequence, Tuple

from . import errors
from .config import Settings


# ---------------------------------------------------------------------------
# Result envelope for a single low-level command
# ---------------------------------------------------------------------------
class CommandResult:
    __slots__ = ("command", "stdout", "stderr", "exit_code", "duration_s",
                 "ok", "error")

    def __init__(self, command: str, stdout: str = "", stderr: str = "",
                 exit_code: int = 0, duration_s: float = 0.0):
        self.command = command
        self.stdout = stdout
        self.stderr = stderr
        self.exit_code = exit_code
        self.duration_s = duration_s
        self.ok = exit_code == 0
        self.error = "" if exit_code == 0 else (stderr or f"exit {exit_code}")

    def lines(self) -> List[str]:
        return [ln for ln in self.stdout.splitlines() if ln.strip()]

    def first_line(self) -> str:
        ls = self.lines()
        return ls[0] if ls else self.stdout.strip()


class CommandResultError(errors.CommandFailedError):
    def __init__(self, res: "CommandResult"):
        super().__init__(res.error or "command failed")
        self.result = res


# ---------------------------------------------------------------------------
# Safe command construction
# ---------------------------------------------------------------------------
def _build(args: Sequence[str]) -> List[str]:
    """Return args as a list (no shell interpretation of command bodies)."""
    out: List[str] = []
    for a in args:
        if a is None:
            continue
        out.append(str(a))
    return out


def _is_safe(text: str) -> bool:
    """Refuse obvious meta/shell metacharacters inside a device-targeted arg
    is NOT possible; shell commands are inherently arbitrary. Instead we ban a
    small set of dangerous prefixes at the adapter layer. This helper is kept
    for readability but enforcement happens in the ShellEngine."""
    return True


class BaseTransport:
    offline = False
    name = "base"

    def run(self, args: Sequence[str], *, timeout_s: Optional[float] = None,
            serial: Optional[str] = None) -> CommandResult:
        raise NotImplementedError

    def screencap(self, serial: str) -> bytes:
        """Return raw PNG bytes of the device screen. Transports override this
        because screenshot bytes must not go through the text decoder."""
        raise NotImplementedError


# ---------------------------------------------------------------------------
# Real ADB transport (Windows/Linux/mac host)
# ---------------------------------------------------------------------------
class AdbTransport(BaseTransport):
    offline = False
    name = "adb"

    def __init__(self, settings: Settings, adb_exe: Optional[str] = None):
        self.settings = settings
        self.adb_exe = adb_exe or _locate_adb(settings)
        if not self.adb_exe:
            raise errors.ToolNotFoundError(
                "ADB not found. Set AC_ADB_PATH / AC_PLATFORM_TOOLS_DIR, add it "
                "to PATH, or run the host-tools installer (skill: "
                "android-adb-bootstrap).")

    # -- base command -----------------------------------------------------
    def run(self, args: Sequence[str], *, timeout_s: Optional[float] = None,
            serial: Optional[str] = None) -> CommandResult:
        cmd = [self.adb_exe]
        if serial:
            cmd += ["-s", serial]
        cmd += list(args)
        timeout = timeout_s if timeout_s is not None else \
            self.settings.default_timeout_s
        t0 = time.monotonic()
        try:
            proc = subprocess.run(
                _build(cmd), capture_output=True, text=True,
                timeout=timeout, check=False)
        except subprocess.TimeoutExpired:
            return CommandResult(" ".join(cmd), stderr="timed out",
                                 exit_code=124,
                                 duration_s=time.monotonic() - t0)
        except OSError as e:
            return CommandResult(" ".join(cmd), stderr=str(e),
                                 exit_code=127, duration_s=time.monotonic() - t0)
        return CommandResult(" ".join(cmd),
                             stdout=proc.stdout or "",
                             stderr=proc.stderr or "",
                             exit_code=proc.returncode,
                             duration_s=time.monotonic() - t0)

    def push_bytes(self, serial: str, content: bytes, device_path: str) -> bool:
        """Write raw bytes to a device file via `adb push` from a temp host file."""
        import tempfile
        with tempfile.NamedTemporaryFile(suffix=".tmp", delete=False) as fh:
            fh.write(content)
            tmp = fh.name
        try:
            proc = subprocess.run(
                [self.adb_exe, "-s", serial, "push", tmp, device_path],
                capture_output=True, timeout=30)
            return proc.returncode == 0
        except (OSError, subprocess.TimeoutExpired):
            return False
        finally:
            try:
                os.remove(tmp)
            except OSError:
                pass

    def screencap(self, serial: str) -> bytes:
        cmd = [self.adb_exe, "-s", serial, "exec-out", "screencap", "-p"]
        t0 = time.monotonic()
        try:
            proc = subprocess.run(cmd, capture_output=True, timeout=30,
                                  check=False)
        except (subprocess.TimeoutExpired, OSError) as e:
            raise CommandResultError(CommandResult(
                "screencap", stderr=str(e), exit_code=127,
                duration_s=time.monotonic() - t0))
        if proc.returncode != 0 or not proc.stdout:
            raise CommandResultError(CommandResult(
                "screencap", stderr=proc.stderr.decode("utf-8", "replace"),
                exit_code=proc.returncode, duration_s=time.monotonic() - t0))
        return proc.stdout


def _locate_adb(settings: Settings) -> Optional[str]:
    if settings.adb_path:
        return settings.adb_path
    if settings.platform_tools_dir:
        cand = Path(settings.platform_tools_dir) / _exe("adb")
        if cand.exists():
            return str(cand)
    # PATH lookup
    from shutil import which
    return which("adb")


def _exe(name: str) -> str:
    return name + ".exe" if os.name == "nt" else name


# ---------------------------------------------------------------------------
# Deterministic offline mock transport
# ---------------------------------------------------------------------------
class MockTransport(BaseTransport):
    """Deterministic, no-hardware transport used by --offline.

    Devices are drawn from Settings.mock_devices; command parsing mirrors the
    real ADB surface closely enough that the engines are exercised the same
    way. Screenshots are tiny generated PNGs; ui dumps are stable XML.
    """
    offline = True
    name = "mock"

    def __init__(self, settings: Settings):
        self.settings = settings
        self.mock = True
        self._device_meta = {}
        self._screens = {}
        self._files = {}
        self._logcat: List[str] = []
        self._state = "device"          # device|offline|unauthorized
        self._sn = 0
        self._focus = {}                # serial -> {pkg, activity}

    # Device descriptor parse --------------------------------------------------
    def _serial_model(self, serial: str) -> Tuple[str, str]:
        parts = serial.split("_")
        return parts[0], (parts[1] if len(parts) > 1 else "MockPhone")

    def _meta(self, serial: str) -> dict:
        if serial not in self._device_meta:
            s, model = self._serial_model(serial)
            self._device_meta[serial] = {
                "serial": serial, "model": model,
                "manufacturer": "MockCorp",
                "android_version": "15", "sdk_level": "35",
                "arch": "arm64-v8a", "state": self._state,
            }
        return self._device_meta[serial]

    # -- root parser ----------------------------------------------------------
    def run(self, args: Sequence[str], *, timeout_s: Optional[float] = None,
            serial: Optional[str] = None) -> CommandResult:
        argv = list(args)
        # consume -s SERIAL if the engine already added it (defensive)
        if argv and argv[0] == "-s" and len(argv) > 1:
            serial, argv = argv[1], argv[2:]
        op = argv[0] if argv else ""
        t0 = time.monotonic()

        if serial and self._meta(serial)["state"] != "device":
            return self._res(op, "", "device offline/unauthorized", 1, t0)

        if op == "devices":
            lines = ["List of devices attached"]
            for s in self.settings.mock_devices:
                lines.append(f"{s}\tdevice")
            lines.append("")
            return self._res(op, "\n".join(lines), "", 0, t0)

        if op == "connect":
            host = argv[1] if len(argv) > 1 else ""
            return self._res(op, f"connected to {host}", "", 0, t0)

        if op == "disconnect":
            return self._res(op, "disconnected", "", 0, t0)

        if op == "version":
            return self._res(op, "Android Debug Bridge version 1.0.41 (mock)", "", 0, t0)

        if op == "shell":
            return self._shell(argv[1:], serial, t0)

        if op in ("push", "pull"):
            return self._transfer(op, argv[1:], serial, t0)

        if op == "install":
            return self._res(op, "Success (mock install)", "", 0, t0)

        if op == "uninstall":
            return self._res(op, "Success (mock uninstall)", "", 0, t0)

        if op in ("forward", "reverse"):
            return self._res(op, "", "", 0, t0)

        if op == "exec-out" and len(argv) > 1 and argv[1] == "screencap":
            png = self._png()
            self._screens[serial] = png
            return CommandResult("screencap", stdout="", stderr="",
                                 exit_code=0, duration_s=time.monotonic() - t0)

        if op == "get-serialno":
            return self._res(op, serial or "MOCK", "", 0, t0)

        if op == "reconnect":
            return self._res(op, "reconnected", "", 0, t0)

        if op == "kill-server" or op == "start-server":
            return self._res(op, "", "", 0, t0)

        return self._res(op, "", f"mock: unsupported op {op}", 1, t0)

    def _shell(self, argv: List[str], serial: Optional[str], t0: float):
        if not argv:
            return self._res("shell", "", "", 0, t0)
        # argv may be a single whole command string or token list; normalise by
        # whitespace-splitting so the mock parses real command strings.
        if len(argv) == 1:
            full = argv[0]
        else:
            full = " ".join(str(a) for a in argv)
        tokens = full.split()
        cmd = tokens[0]
        args = tokens[1:]
        meta = self._meta(serial or "MOCK")

        if cmd == "command" and args and args[0] == "-v":
            tool = args[1] if len(args) > 1 else ""
            present = tool in ("screencap", "screenrecord", "pm", "am",
                               "uiautomator", "input", "dumpsys", "wm",
                               "cmd", "settings", "getprop", "monkey")
            return self._res("command -v", "yes" if present else "", "", 0, t0)

        if cmd == "test":
            # test -d path && echo yes handled generically below
            if len(args) >= 3 and args[0] == "-d":
                return self._res("test", "yes" if args[-1] else "", "", 0, t0)

        if cmd == "getprop":
            prop = args[0] if args else ""
            table = {"ro.product.model": meta["model"],
                     "ro.product.manufacturer": meta["manufacturer"],
                     "ro.build.version.release": meta["android_version"],
                     "ro.build.version.sdk": meta["sdk_level"],
                     "ro.product.cpu.abi": meta["arch"]}
            return self._res("getprop", table.get(prop, prop + ": []"), "", 0, t0)

        if cmd == "wm":
            if args and args[0] == "size":
                return self._res("wm", "Physical size: 1080x2400", "", 0, t0)
            if args and args[0] == "density":
                return self._res("wm", "Physical density: 420", "", 0, t0)

        if cmd == "dumpsys":
            service = args[0] if args else ""
            if service == "battery":
                return self._res("dumpsys",
                                 "  level: 87\n  status: 2\n  powered: true",
                                 "", 0, t0)
            if service == "window":
                f = self._focus.get(serial or "MOCK",
                                    {"pkg": "com.android.launcher",
                                     "act": "com.android.launcher.Launcher"})
                return self._res("dumpsys",
                                 f"mCurrentFocus=Window{{hash u0 "
                                 f"{f['pkg']}/{f['act']}}}", "", 0, t0)

        if cmd == "input":
            return self._res("input", "", "", 0, t0)

        if cmd == "screencap" and args and args[0] == "-p":
            png = self._png()
            self._screens[serial] = png
            return self._res("screencap", "", "", 0, t0)

        if cmd == "screenrecord":
            return self._res("screenrecord", "", "", 0, t0)

        if cmd == "am":
            if args and args[0] == "start":
                pkg, act = _resolve_component(args)
                self._set_focus(serial, pkg, act)
                return self._res("am", "Starting: Intent", "", 0, t0)
            if args and args[0] == "force-stop" and len(args) > 1:
                self._set_focus(serial, "com.android.launcher",
                                "com.android.launcher.Launcher")
                return self._res("am", "", "", 0, t0)
            if args and args[0] == "broadcast":
                return self._res("am", "Broadcast completed", "", 0, t0)

        if cmd == "monkey":
            pkg = None
            for i, a in enumerate(args):
                if a == "-p" and i + 1 < len(args):
                    pkg = args[i + 1]
            if pkg:
                self._set_focus(serial, pkg, pkg + ".MainActivity")
                return self._res("monkey", f"Events injected: 1", "", 0, t0)
            return self._res("monkey", "", "", 0, t0)

        if cmd == "pm":
            if args and args[0] == "list":
                return self._res("pm", "\n".join(_packages()), "", 0, t0)
            if args and args[0] in ("path", "dump"):
                return self._res("pm", "", "", 0, t0)
            if args and args[0] == "clear":
                return self._res("pm", "Success", "", 0, t0)
            if args and args[0] in ("enable", "disable-user", "disable"):
                return self._res("pm", "", "", 0, t0)

        if cmd == "cmd":
            # wifi, settings etc.
            return self._res("cmd", "", "", 0, t0)

        if cmd == "settings":
            if args and args[0] in ("get", "put"):
                return self._res("settings", "", "", 0, t0)

        if cmd == "svc":
            return self._res("svc", "", "", 0, t0)

        if cmd == "reboot":
            self._meta(serial)["state"] = "device"   # comes back up
            return self._res("reboot", "", "", 0, t0)

        if cmd == "uiautomator":
            return self._res("uiautomator", _ui_xml(), "", 0, t0)

        if cmd == "ls":
            return self._res("ls", "\n".join(_ls(meta["model"])), "", 0, t0)

        if cmd == "mkdir":
            return self._res("mkdir", "", "", 0, t0)

        if cmd == "cat":
            return self._res("cat", "mock-file-content\n", "", 0, t0)

        if cmd == "rm":
            return self._res("rm", "", "", 0, t0)

        if cmd == "sha1sum":
            return self._res("sha1sum", "da39a3ee5e6b4b0d3255bfef95601890afd80709", "", 0, t0)

        if cmd == "logcat":
            return self._res("logcat", "\n".join(self._logcat[-30:]), "", 0, t0)

        if cmd == "pidof" and args:
            return self._res("pidof", "1234", "", 0, t0)

        if cmd == "whoami":
            return self._res("whoami", "shell", "", 0, t0)

        if cmd == "date":
            return self._res("date", "Thu Jan  1 00:00:00 UTC 1970", "", 0, t0)

        return self._res("shell " + cmd, "", f"mock: unsupported {cmd}", 1, t0)

    def _transfer(self, op, argv, serial, t0):
        return self._res(op, "", "", 0, t0)

    def screencap(self, serial: str) -> bytes:
        png = self._png()
        self._screens[serial] = png
        return png

    def push_bytes(self, serial: str, content: bytes, device_path: str) -> bool:
        self._files[(serial, device_path)] = content
        return True

    def _set_focus(self, serial, pkg, act):
        key = serial or "MOCK"
        if pkg:
            self._focus[key] = {"pkg": pkg,
                                "act": act or (pkg + ".MainActivity")}

    def _res(self, op, stdout, stderr, code, t0):
        return CommandResult(op, stdout=stdout, stderr=stderr,
                             exit_code=code, duration_s=time.monotonic() - t0)

    def screenshot_bytes(self, serial) -> bytes:
        return self._png()

    def _png(self) -> bytes:
        # Tiny valid 1x1 PNG (deterministic)
        return bytes.fromhex(
            "89504e470d0a1a0a0000000d4948445200000001000000010806000000"
            "1f15c4890000000d49444154789c6360000002000155a2fc9c00000000"
            "49454e44ae426082")


def _resolve_component(args) -> tuple:
    """Extract (package, activity) from an `am start` arg list in the mock."""
    joined = " ".join(args)
    # -n pkg/act
    m = re.search(r"-n\s+([a-zA-Z0-9_.$]+)/([a-zA-Z0-9_.$]+)", joined)
    if m:
        return m.group(1), m.group(2)
    # package from component
    m = re.search(r"([a-zA-Z0-9_.]+/[a-zA-Z0-9_.$]+)", joined)
    if m:
        comp = m.group(1)
        if "/" in comp:
            return comp.split("/")[0], comp.split("/")[1]
    # -p package (category launch)
    m = re.search(r"-p\s+([a-zA-Z0-9_.]+)", joined)
    if m:
        return m.group(1), ""
    # ACTION_VIEW of a URL -> browser
    if "-a" in joined and "android.intent.action.VIEW" in joined \
       and ("http" in joined or "https" in joined):
        return "com.android.chrome", "org.chromium.chrome.browser.ChromeTabbedActivity"
    # heuristic by keyword
    lower = joined.lower()
    for kw, pkg in (("camera", "com.google.android.GoogleCamera"),
                    ("settings", "com.android.settings"),
                    ("whatsapp", "com.whatsapp"),
                    ("chrome", "com.android.chrome"),
                    ("calculator", "com.google.android.calculator"),
                    ("maps", "com.google.android.apps.maps"),
                    ("youtube", "com.google.android.youtube")):
        if kw in lower:
            return pkg, pkg.split(".")[-1].capitalize() + "Activity"
    return "com.example.app", "MainActivity"


def _packages() -> List[str]:
    return [
        "package:com.android.settings",
        "package:com.google.android.GoogleCamera",
        "package:com.whatsapp",
        "package:com.android.chrome",
        "package:com.google.android.calculator",
        "package:com.google.android.apps.maps",
        "package:org.mozilla.firefox",
    ]


def _ls(model: str) -> List[str]:
    return [
        "-rw-rw---- root sdcard_rw 4096 2026-01-01 00:00 DCIM",
        "-rw-rw---- root sdcard_rw 4096 2026-01-01 00:00 Pictures",
        "-rw-r--r-- root root 2026 2026-01-01 00:00 hello.txt",
    ]


def _ui_xml() -> str:
    # Stable accessibility dump with semantic nodes for exercises.
    return ('<?xml version="1.0" encoding="UTF-8"?>\n'
            '<hierarchy rotation="0">\n'
            '  <node index="0" text="" resource-id="android:id/content" '
            'class="android.widget.FrameLayout" package="com.android.settings" '
            'content-desc="" checkable="false" checked="false" '
            'clickable="false" enabled="true" focusable="false" '
            'focused="false" scrollable="false" long-clickable="false" '
            'password="false" selected="false" bounds="[0,0][1080,2400]">\n'
            '    <node index="0" text="Wi-Fi" resource-id="android:id/title" '
            'class="android.widget.TextView" package="com.android.settings" '
            'content-desc="" checkable="false" checked="false" '
            'clickable="true" enabled="true" focusable="true" focused="false" '
            'scrollable="false" long-clickable="false" password="false" '
            'selected="false" bounds="[0,400][540,520]"/>\n'
            '  </node>\n'
            '</hierarchy>\n')
