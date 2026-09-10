"""Remote Touchpad companion backend.

This manages the GPLv3 ``Unrud/remote-touchpad`` host that is vendored under
``third_party/remote-touchpad`` (full source + COPYING). It runs ON the Windows
PC and lets an authorized Android phone act as a wireless touchpad + keyboard
**for the PC**. This is a *separate direction* from the ADB Android-control
engine (which drives Android from Windows). Both are exposed through the one
agent interface so the whole system lives in one place.

Reliability / deployment notes (honest):
  * The Windows build is a real, prebuilt binary fetched from the project's
    official GitHub release (or built from the vendored source with a recent
    Go + mingw-w64). A phone is required to exercise it end-to-end.
  * This workspace has no Go/Windows/phone, so this module's *state machine*
    is verified offline against a stub binary; the real Windows binary is not
    run here. ``--version`` exists on the real binary.
  * The server prints the connect URL (+ QR) to stdout/stderr; we parse and
    expose it.
  * License: remote-touchpad is GPLv3 (see third_party/remote-touchpad/COPYING).
    It is kept as a separate component under android-control, not merged into
    the MIT core.
"""
from __future__ import annotations

import os
import re
import shutil
import subprocess
import tempfile
import threading
import urllib.request
from pathlib import Path
from typing import Optional

from .. import errors
from ..config import Settings

DEFAULT_RELEASE = "v1.5.4"
ASSET = "remote-touchpad_windows_amd64.exe"
DOWNLOAD_URL = ("https://github.com/Unrud/remote-touchpad/releases/download/"
                "{release}/" + ASSET)

_URL_RE = re.compile(r"(https?://\S+)")
_BIN_CANDIDATES = ("remote-touchpad", "remote-touchpad.exe",
                   "remote-touchpad_windows_amd64.exe")


class RemoteTouchpadBackend:
    """Manages a single remote-touchpad host process (phone-as-PC-input)."""

    def __init__(self, settings: Settings):
        self.settings = settings
        self._proc: Optional[subprocess.Popen] = None
        self._url: Optional[str] = None
        self._secret: Optional[str] = None
        self._bind: Optional[str] = None
        self._lock = threading.RLock()

    # ------------------------------------------------------------------ #
    # binary resolution
    # ------------------------------------------------------------------ #
    def resolve_binary(self) -> str:
        """Return a usable remote-touchpad binary path or raise
        ToolNotFoundError with clear install guidance."""
        s = self.settings
        if s.rt_bin and Path(s.rt_bin).exists() and Path(s.rt_bin).is_file():
            return s.rt_bin
        # look in install dir / install-dir/bin (only real files, not folders)
        for cand in _bin_candidates_in(Path(s.install_dir)):
            if cand.is_file() and cand.exists():
                return str(cand)
        # PATH
        for name in _BIN_CANDIDATES:
            p = shutil.which(name)
            if p:
                return p
        # auto-download path
        if s.rt_autodownload and os.name == "nt":
            target = self._download()
            if target:
                return target
        raise errors.ToolNotFoundError(
            "remote-touchpad binary not found. Either set AC_RT_BIN to the "
            "downloaded exe, or run scripts/download_remote_touchpad.py, or "
            f"build from third_party/remote-touchpad (go build). Official "
            f"release: v{s.rt_release or DEFAULT_RELEASE}.")

    def _download(self) -> Optional[str]:
        release = self.settings.rt_release or DEFAULT_RELEASE
        dest_dir = Path(self.settings.install_dir) / "remote-touchpad"
        dest_dir.mkdir(parents=True, exist_ok=True)
        target = dest_dir / ASSET
        url = DOWNLOAD_URL.format(release=release)
        try:
            tmp = target.with_suffix(".tmp")
            urllib.request.urlretrieve(url, tmp)
            tmp.replace(target)
            return str(target)
        except Exception:
            return None

    # ------------------------------------------------------------------ #
    # lifecycle
    # ------------------------------------------------------------------ #
    def start(self, *, bind: Optional[str] = None, secret: Optional[str] = None,
              cert_file: Optional[str] = None, key_file: Optional[str] = None,
              wait_s: float = 3.0) -> dict:
        """Start the remote-touchpad host and capture the connect URL.

        ``secret`` defaults to a random one (matching upstream). Returns
        {status, url, bind, secret} once the process reports a URL.
        Raises if the process exits early (e.g. unsupported platform).
        """
        with self._lock:
            if self._proc and self._proc.poll() is None:
                return {"status": "RUNNING", "url": self._url,
                        "bind": self._bind}
            binary = self.resolve_binary()
            self._bind = bind or self.settings.rt_bind or ":0"
            self._secret = secret if secret is not None else \
                (self.settings.rt_secret or _rand_secret())
            cmd = [binary, "--bind", self._bind, "--secret", self._secret]
            if cert_file and key_file:
                cmd += ["--cert", cert_file, "--key", key_file]
            # capture output (server prints URL + QR there)
            self._proc = subprocess.Popen(
                cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                text=True)
            self._url = self._wait_for_url(self._proc, wait_s)
            if self._url is None:
                # give a short grace for startup; if exited, report platform
                if self._proc.poll() is not None:
                    code = self._proc.poll()
                    raise errors.CommandFailedError(
                        f"remote-touchpad exited early (code {code}). On this "
                        "host it needs a supported desktop input backend "
                        "(Windows/X11/Wayland). Check the binary runs on the "
                        "target machine.")
            return {"status": "RUNNING", "url": self._url,
                    "bind": self._bind, "secret": self._secret}

    def _wait_for_url(self, proc, wait_s: float) -> Optional[str]:
        import time
        t0 = time.monotonic()
        buf = ""
        while time.monotonic() - t0 < wait_s:
            line = proc.stdout.readline()
            if not line:
                if proc.poll() is not None:
                    break
                time.sleep(0.1)
                continue
            buf += line
            m = _URL_RE.search(line)
            if m:
                return m.group(1)
        # fallback: scan what we captured
        m = _URL_RE.search(buf)
        return m.group(1) if m else None

    def stop(self) -> dict:
        with self._lock:
            if self._proc is not None:
                self._proc.terminate()
                try:
                    self._proc.wait(timeout=5)
                except Exception:
                    self._proc.kill()
                self._proc = None
            self._url = None
            return {"status": "STOPPED"}

    def status(self) -> dict:
        with self._lock:
            running = bool(self._proc and self._proc.poll() is None)
            return {"status": "RUNNING" if running else "STOPPED",
                    "url": self._url, "bind": self._bind,
                    "binary": self.resolve_binary() if running else None}

    @property
    def url(self) -> Optional[str]:
        return self._url

    # ------------------------------------------------------------------ #
    # connection payload for the agent
    # ------------------------------------------------------------------ #
    def connection_info(self) -> dict:
        return {"url": self._url, "secret": self._secret,
                "bind": self._bind,
                "note": ("Open this URL in the Android browser (or scan the "
                         "QR) to use the phone as a wireless touchpad + "
                         "keyboard for this PC.")}


def _bin_candidates_in(d: Path):
    for name in _BIN_CANDIDATES:
        yield d / name
    yield d / "remote-touchpad" / _BIN_CANDIDATES[0]
    yield d / "remote-touchpad" / _BIN_CANDIDATES[1]
    yield d / "remote-touchpad" / _BIN_CANDIDATES[2]


def _rand_secret(length: int = 12) -> str:
    import base64
    import os as _os
    raw = _os.urandom(length)
    return base64.urlsafe_b64encode(raw).decode().rstrip("=")
