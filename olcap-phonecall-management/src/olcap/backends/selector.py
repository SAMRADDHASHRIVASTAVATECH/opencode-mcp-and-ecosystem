"""Backend selection for the phone-call control plane.

Returns the live, honest backend that satisfies the config:

  1. adb             -> AndroidControl via AdbSupervisor (real SIM + cellular)
  2. openclaw_voice  -> OpenClaw CLI voice-call fallback
  3. simulated       -> dev-only fallback (never reported as a real call)

Priority:
  * explicit ``OLCAP_BACKEND`` (non-"auto") pins the chain start
  * an ADB device pinned via OLCAP_ADB_SERIAL / MODEL / MANUFACTURER wins even
    when currently offline (the supervisor self-heals in the background)
  * otherwise try ``provider_fallback`` then ADB again (last resort).

Returns ``(backend, reasons)`` where ``reasons`` is a human-readable chain.
"""
from __future__ import annotations

from ..errors import OlcapError
from .adb import AdbTelephonyBackend
from .adbdevice import AdbSupervisor
from .openclaw_call import OpenClawCallBackend
from .simulated import SimulatedTelephonyBackend

_LEGACY = {"android_bridge": "adb", "provider_voice": "openclaw_voice",
           "voip": "openclaw_voice"}
_FALLBACK_DEFAULT = ("adb", "openclaw_voice", "simulated", "adb")


def _pinned(config) -> bool:
    return bool(getattr(config, "adb_serial", "")
                or getattr(config, "adb_model", "")
                or getattr(config, "adb_manufacturer", ""))


def _chain(config) -> list[str]:
    want = (getattr(config, "backend", "auto") or "auto").strip().lower()
    want = _LEGACY.get(want, want)
    chain: list[str] = []
    if want and want != "auto":
        chain.append(want)
    if _pinned(config):
        chain.append("adb")
    if not chain:
        chain = list(_FALLBACK_DEFAULT)
    else:
        chain.append("adb")  # final self-healing resort
    return chain


def select_backend(config) -> tuple:
    """Return (backend_instance, reason_list)."""
    reasons: list[str] = []
    chain = _chain(config)

    for kind in chain:
        if kind == "adb":
            try:
                sup = AdbSupervisor(config)
            except Exception as e:
                reasons.append(f"adb unavailable: {e}")
                continue
            if sup.available():
                if sup.online():
                    reasons.append("adb: device online")
                else:
                    reasons.append("adb: device detached; supervisor retrying")
                return (AdbTelephonyBackend(sup, getattr(config, "country_code", "+91")),
                        list(reasons))
            reasons.append("adb: android_control not importable")
            continue
        if kind == "openclaw_voice":
            oc = OpenClawCallBackend()
            if oc.available():
                reasons.append("openclaw_voice: CLI available")
                return (oc, list(reasons))
            reasons.append("openclaw_voice: CLI unavailable")
            continue
        if kind == "simulated":
            reasons.append("simulated: dev-only fallback")
            return (SimulatedTelephonyBackend(config), list(reasons))
        reasons.append(f"unknown backend {kind!r}")

    raise OlcapError("no phone-call backend available: " + "; ".join(reasons),
                     code="NO_BACKEND")