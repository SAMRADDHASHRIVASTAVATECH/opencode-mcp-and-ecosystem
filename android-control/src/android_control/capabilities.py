"""Per-device capability profiling (§19): probe each capability and build a
device-specific CapabilityProfile. Also scan version-dependent features so we
never assume Android 10 == Android 16.
"""
from __future__ import annotations

from .config import Settings
from .devices.registry import CapabilityProfile


def scan(serial: str, transport, settings: Settings,
         have_scrcpy: bool = False) -> CapabilityProfile:
    """Probe a device and return its CapabilityProfile.

    ``transport`` must support a small probe method or we fall back to a shell
    probe helper built from the transport's own ``run``.
    """
    prof = CapabilityProfile()
    state = _device_state(transport, serial)
    if state != "device":
        prof.adb = "READY" if state == "device" else "UNAVAILABLE"
        prof.wireless_adb = "UNAVAILABLE"
        prof.shell = "UNAVAILABLE"
        return prof

    probe = _Prober(transport, serial)
    sdk = probe.sdk
    prof.adb = "READY"
    prof.wireless_adb = "READY" if sdk >= 30 else "PARTIAL"
    prof.shell = "READY"
    prof.input = "READY"
    prof.screenshot = _yes(probe.which("screencap"))
    prof.screen_recording = _yes(probe.which("screenrecord"))
    prof.file_transfer = "READY"
    prof.package_control = _yes(probe.which("pm"))
    prof.intent_control = _yes(probe.which("am"))
    prof.ui_hierarchy = _yes(probe.which("uiautomator"))
    prof.semantic_ui = prof.ui_hierarchy
    prof.scrcpy = "READY" if have_scrcpy else "UNAVAILABLE"

    prof.extra["android_version"] = probe.version
    prof.extra["sdk_level"] = str(sdk)
    return prof


class _Prober:
    """Non-raising shell probes for a single serial."""

    def __init__(self, transport, serial: str):
        self.t = transport
        self.serial = serial

    def _shell(self, cmd: str):
        try:
            return self.t.run(["shell", cmd], serial=self.serial)
        except Exception:
            return None

    def which(self, tool: str) -> bool:
        r = self._shell(f"command -v {tool} >/dev/null 2>&1 && echo yes")
        return bool(r and r.ok and "yes" in r.stdout)

    @property
    def sdk(self) -> int:
        r = self._shell("getprop ro.build.version.sdk")
        try:
            return int(r.stdout.strip()) if r and r.ok else 0
        except ValueError:
            return 0

    @property
    def version(self) -> str:
        r = self._shell("getprop ro.build.version.release")
        return r.stdout.strip() if r and r.ok else ""


def _yes(v: bool) -> str:
    return "READY" if v else "UNAVAILABLE"


def _device_state(transport, serial: str) -> str:
    try:
        res = transport.run(["devices"])
        for ln in res.stdout.splitlines():
            if ln.startswith(serial + "\t"):
                return ln.split("\t", 1)[1].strip()
    except Exception:
        pass
    return "offline"
