"""Host-side ADB device supervisor.

Reuses the ``android_control`` library in-process (no second MCP server, no
phone-side app). It:

  * discovers attached real devices (USB + already-paired wireless),
  * selects one authoritative device via OLCAP_ADB_SERIAL / MODEL / MANUFACTURER,
    falling back to the first real connected device (mock fleet is excluded),
  * self-heals disconnects in the background with exponential backoff
    (USB<->wireless transitions, restarts, sleep/wake),
  * exposes checked shell / dumpsys / getprop / keyevent primitives for the
    AdbTelephonyBackend.

Everything is real-mode: the deterministic mock/offline fleet is explicitly
disabled so we never operate on placeholder devices.
"""
from __future__ import annotations

import os
import threading
import time

from ..errors import OlcapError

_MOCK_SUFFIX = "_mock"


def _is_mock(serial: str) -> bool:
    return serial.lower().endswith(_MOCK_SUFFIX)


class AdbSupervisor:
    name = "adb"

    def __init__(self, config):
        self.cfg = config
        # Real mode only -- never target the deterministic mock fleet.
        os.environ["AC_MOCK_DEVICES"] = ""
        try:
            from android_control.controller import AndroidControl
            self._ctrl_cls = AndroidControl
        except Exception as e:  # pragma: no cover - import guard
            self._ctrl_cls = None
            self._import_error = str(e)
        self._import_error = getattr(self, "_import_error", "")
        self._lock = threading.RLock()
        self._stop = threading.Event()
        self._thread: threading.Thread | None = None
        self._ctrl = None
        self._session = None          # DeviceSession or None
        self._connected = False
        self._last_error = ""
        self._last_profile = {}
        self._backoff_s = 1.0
        self._boot()

    # ---- lifecycle -------------------------------------------------- #
    def _ensure_ctrl(self):
        if self._ctrl is not None:
            return self._ctrl
        if self._ctrl_cls is None:
            raise OlcapError(
                "ADB backend requires the android_control library "
                f"(import failed: {self._import_error}). Add "
                "android-control\\src to PYTHONPATH.")
        c = self._ctrl_cls(offline=False)
        self._ctrl = c
        return c

    def _boot(self):
        try:
            self._ensure_ctrl()
            self._discover()
        except Exception as e:
            self._last_error = str(e)
        if self._thread is None and self._ctrl_cls is not None:
            self._thread = threading.Thread(
                target=self._run, name="olcap-adb-supervisor", daemon=True)
            self._thread.start()

    def shutdown(self):
        self._stop.set()

    # ---- discovery / selection -------------------------------------- #
    def _discover(self):
        c = self._ensure_ctrl()
        c.discover()
        self._drop_mocks(self.cfg.adb_serial)

    def _drop_mocks(self, keep_serial: str = ""):
        """Remove mock sessions (and everything except a pinned real serial)."""
        reg = self._ensure_ctrl().registry
        for s in list(reg.all()):
            if _is_mock(s.serial):
                reg.remove(s.device_id)
                continue
            if keep_serial and s.serial != keep_serial:
                reg.remove(s.device_id)

    def _select(self):
        """Resolve the active session. Returns a DeviceSession or None."""
        c = self._ensure_ctrl()
        cfg = self.cfg
        pins = []
        if getattr(cfg, "adb_serial", ""):
            pins.append(("serial", cfg.adb_serial))
        if getattr(cfg, "adb_model", ""):
            pins.append(("model", cfg.adb_model))
        if getattr(cfg, "adb_manufacturer", ""):
            pins.append(("manufacturer", cfg.adb_manufacturer))

        # re-run discovery so USB re-plug / pairings show up
        try:
            c.discover()
            self._drop_mocks(cfg.adb_serial)
        except Exception:
            pass

        for kind, want in pins:
            for s in c.registry.all():
                val = getattr(s, kind, "")
                if val and (val.lower() == want.lower()
                            or want.lower() in val.lower()):
                    return s

        connected = [s for s in c.registry.connected()
                     if s.connection_state == "connected" and not _is_mock(s.serial)]
        if connected:
            return connected[0]
        real = [s for s in c.registry.all() if not _is_mock(s.serial)]
        return real[0] if real else None

    # ---- state ------------------------------------------------------ //
    def _run(self):
        poll = max(1, getattr(self.cfg, "adb_health_poll_s", 2) or 2)
        backoff = self._backoff_s
        while not self._stop.is_set():
            time.sleep(poll)
            try:
                c = self._ensure_ctrl()
                s = self._select()
                if s is None:
                    self._connected = False
                    self._session = None
                    backoff = min(backoff * 2,
                                  getattr(self.cfg, "adb_reconnect_backoff_max_s", 60))
                    continue
                hc = c.health_check(s.device_id)
                ok = hc.get("now") in ("connected", "device")
                self._session = s
                self._connected = bool(ok)
                if ok:
                    backoff = 1.0
                    try:
                        self._last_profile = c.status(s.device_id)
                    except Exception:
                        pass
                    continue
                # offline -> attempt self-heal with capped exponential backoff
                self._last_error = f"{s.serial} offline (state={hc.get('now')})"
                try:
                    c.reconnect(s.device_id)
                except Exception as e:
                    self._last_error = f"reconnect failed: {e}"
                backoff = min(backoff * 2,
                              getattr(self.cfg, "adb_reconnect_backoff_max_s", 60))
            except Exception as e:
                self._last_error = str(e)
                time.sleep(min(backoff, 5))
                backoff = min(backoff * 2, 30)

    # ---- accessors -------------------------------------------------- #
    def available(self) -> bool:
        # Library importability = the backend exists. Connectivity is reported
        # separately via online() so an offline device never looks 'absent'.
        return self._ctrl_cls is not None

    def online(self) -> bool:
        s = self._session
        return bool(s and self._connected)

    def serial(self) -> str:
        s = self._session
        return s.serial if s else ""

    def device_id(self) -> str:
        s = self._session
        return s.device_id if s else ""

    def profile(self) -> dict:
        p = dict(self._last_profile) if self._last_profile else {}
        p["device_id"] = self.device_id()
        p["serial"] = self.serial()
        p["connected"] = self.online()
        p["last_error"] = self._last_error
        p["connection_type"] = (self._session.connection_type
                                if self._session else "")
        return p

    def health(self) -> dict:
        return {"backend": self.name, "online": self.online(),
                "device": self.profile(), "last_error": self._last_error}

    # ---- primitives (require online device) ------------------------- #
    def _require(self):
        s = self._session
        if not s or not self._connected:
            raise OlcapError(
                "no ADB device attached (supervisor is retrying with backoff)")
        return s

    def _ctrl_for(self):
        return self._require(), self._ensure_ctrl()

    def shell(self, command: str) -> str:
        s, c = self._ctrl_for()
        return c.shell.shell(s.serial, command)

    def dumpsys(self, service: str) -> str:
        s, c = self._ctrl_for()
        return c.shell.dumpsys(s.serial, service)

    def getprop(self, prop: str) -> str:
        s, c = self._ctrl_for()
        return c.shell.getprop(s.serial, prop)

    def input(self, text: str) -> str:
        return self.shell(f"input text {text}")

    def keyevent(self, code: int) -> str:
        return self.shell(f"input keyevent {int(code)}")

    def am_call(self, destination: str) -> str:
        return self.shell(f"am start -a android.intent.action.CALL -d tel:{destination}")

    # ---- telephony state -------------------------------------------- #
    def call_state(self) -> tuple:
        """Return (mCallState:int, mCallIncomingNumber:str) best-effort.
        mCallState: 0 idle, 1 ringing, 2 offhook. Never fabricated."""
        reg = ""
        try:
            reg = self.dumpsys("telephony.registry")
        except Exception:
            return (0, "")
        import re
        codes = [int(v) for v in re.findall(r"mCallState=(\d+)", reg)]
        code = max(codes) if codes else 0
        numbers = re.findall(r"mCallIncomingNumber=([^\n\r]*)", reg)
        number = (numbers[-1].strip() if numbers else "")
        return (code, number)

    def reconnect_now(self) -> dict:
        try:
            s = self._require()
        except OlcapError:
            self._discover()
            s = self._select()
        if s is None:
            return {"reconnected": False, "error": "no device"}
        try:
            prof = self._ensure_ctrl().reconnect(s.device_id)
            return {"reconnected": prof.get("connection_state") == "connected",
                    "profile": prof}
        except Exception as e:
            return {"reconnected": False, "error": str(e)}