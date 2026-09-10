"""Screen engine (§12): screenshots, screen recording, display info,
orientation, and (optionally) scrcpy screen streaming.
"""
from __future__ import annotations

import base64
import subprocess
import time
from pathlib import Path
from typing import Optional

from .. import errors
from ..config import Settings
from .base import EngineBase


class ScreenEngine(EngineBase):
    def __init__(self, transport, settings: Settings):
        super().__init__(transport, settings)
        self._media = Path(settings.screenshot_dir)
        self._media.mkdir(parents=True, exist_ok=True)

    def screenshot(self, serial: str, dest: Optional[str] = None,
                   as_png_bytes: bool = False):
        """Capture a PNG screenshot of the device.

        Returns a local file path (default) or raw PNG bytes when requested.
        Binary capture goes through the transport's ``screencap`` so bytes are
        never corrupted by a text decoder.
        """
        png = self.t.screencap(serial)
        if as_png_bytes:
            return png
        dest = dest or str(self._media / f"{serial}_{int(time.time())}.png")
        Path(dest).write_bytes(png)
        return dest

    def screenrecord(self, serial: str, seconds: float = 10.0,
                     dest: Optional[str] = None) -> str:
        """Record the screen to an mp4 on the device, pull it, return local path."""
        if seconds <= 0 or seconds > 180:
            raise ValueError("seconds must be in (0, 180]")
        dev_path = f"/sdcard/rec_{int(time.time())}.mp4"
        dest = dest or str(self._media / f"{serial}_{int(time.time())}.mp4")
        cmd = (f"screenrecord --time-limit {int(seconds)} {dev_path}")
        self._shell_ok(serial, cmd, timeout_s=self.settings.long_timeout_s + int(seconds))
        self._pull(serial, dev_path, dest)
        return dest

    def display_size(self, serial: str):
        out = self._shell(serial, "wm size")
        return _parse_wm_size(out.stdout)

    def display_density(self, serial: str):
        out = self._shell(serial, "wm density")
        m = _first(r"Physical density:\s*(\d+)", out.stdout)
        return int(m) if m else None

    def orientation(self, serial: str) -> str:
        out = self._dumpsys_rotation(serial)
        return _map_rotation(out)

    def info(self, serial: str) -> dict:
        w, h = self.display_size(serial)
        return {"resolution": f"{w}x{h}", "density": self.display_density(serial),
                "orientation": self.orientation(serial)}

    # -- scrcpy ------------------------------------------------------------
    def stream(self, serial: str, *, bitrate: int = 8_000_000,
               max_size: int = 1024, no_control: bool = False,
               wait_s: float = 5.0) -> subprocess.Popen:
        """Start an scrcpy session for interactive/observable screen streaming.

        Requires scrcpy on PATH or AC_SCRCPY_PATH. Returns the live Popen so
        the caller can stream/stop it. Raises ToolNotFoundError if absent.
        """
        scrcpy = _locate_scrcpy(self.settings)
        if not scrcpy:
            raise errors.ToolNotFoundError(
                "scrcpy not found (needed for live screen streaming). Set "
                "AC_SCRCPY_PATH or install scrcpy via the host bootstrap.")
        cmd = [scrcpy, "-s", serial, "--bit-rate", str(bitrate),
               "--max-size", str(max_size), "--stay-awake"]
        if no_control:
            cmd.append("--no-control")
        proc = subprocess.Popen(cmd, stdout=subprocess.DEVNULL,
                                stderr=subprocess.DEVNULL)
        if wait_s:
            time.sleep(wait_s)
            if proc.poll() is not None:
                raise errors.CommandFailedError("scrcpy exited early")
        return proc

    # helpers --------------------------------------------------------------
    def _pull(self, serial, src, dest):
        res = self._adb(serial, ["pull", src, dest],
                        timeout_s=self.settings.long_timeout_s)
        if not res.ok:
            raise errors.CommandFailedError(f"pull failed: {res.error}")
        return dest

    def _dumpsys_rotation(self, serial):
        out = self._shell(serial, "dumpsys input")
        return out.stdout


def _parse_wm_size(out: str):
    m = _first(r"Physical size:\s*(\d+)x(\d+)", out)
    if m:
        return int(m[0]), int(m[1])
    m = _first(r"Override size:\s*(\d+)x(\d+)", out)
    if m:
        return int(m[0]), int(m[1])
    return 1080, 2400


def _first(regex, text):
    import re
    m = re.search(regex, text)
    return m.groups() if m else None


def _map_rotation(out: str):
    if "SurfaceOrientation: 0" in out or "mOrientation=ROTATION_0" in out \
       or "rotation=0" in out:
        return "portrait"
    if "ROTATION_90" in out or "rotation=1" in out:
        return "landscape"
    return "unknown"


def _locate_scrcpy(settings):
    if settings.scrcpy_path:
        return settings.scrcpy_path
    from shutil import which
    return which("scrcpy")
