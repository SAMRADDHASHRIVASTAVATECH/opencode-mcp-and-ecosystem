"""Universal Android Control Master (§2, §5-6, §30).

Wires the registry, transport, engines and lifecycle into one master object.
It discovers, connects, verifies, capability-scans and controls N devices with
no artificial limit, keeping every device session isolated.
"""
from __future__ import annotations

import os
import re
import time
from typing import Callable, Dict, List, Optional

from . import errors
from .capabilities import scan as scan_caps
from .config import Settings, load_settings
from .devices.registry import DeviceRegistry, DeviceSession
from .engines.adb import AdbEngine
from .engines.apps import AppsEngine
from .engines.files import FilesEngine
from .engines.info import InfoEngine
from .engines.input import InputEngine
from .engines.intents import IntentEngine
from .engines.message import MessageEngine
from .engines.recovery import RecoveryEngine
from .engines.screen import ScreenEngine
from .engines.shell import ShellEngine
from .engines.ui import UIEngine
from .hosts import HostBootstrap
from .logging import OperationLog
from .transport import AdbTransport, MockTransport
from .vision.engine import VisionEngine


class AndroidControl:
    """The master runtime. One instance manages the whole fleet."""

    def __init__(self, settings: Optional[Settings] = None, *,
                 offline: Optional[bool] = None, authorizer: Optional[Callable] = None):
        self.settings = settings or load_settings()
        if offline is not None:
            self.settings.offline = offline
        self.offline = self.settings.offline
        # authorizer(operation, detail) -> bool; default destructive-policy
        self.authorizer = authorizer or self._default_authorizer

        self.log = OperationLog(self.settings.log_dir, debug=self.settings.debug)
        self.bootstrap = HostBootstrap(self.settings)
        # transport (real or deterministic mock)
        if self.offline:
            self.transport = MockTransport(self.settings)
        else:
            # lazy ADB: do not hard-require it until connect/discover
            self.transport = None
        self.adb_exe = None

        # engines (lazy-created after transport is ready)
        self.registry = DeviceRegistry()
        self._engines: Dict[str, object] = {}
        self._vision: Optional[VisionEngine] = None

    # -- engine access -----------------------------------------------------
    def _need_adb(self) -> AdbTransport:
        if self.offline:
            return self.transport
        if self.transport is None:
            try:
                self.transport = AdbTransport(self.settings)
                self.adb_exe = self.transport.adb_exe
            except errors.ToolNotFoundError:
                # let host bootstrap try to install first
                ht = self.bootstrap.ensure("adb")
                self.settings.adb_path = ht.exe_path
                self.transport = AdbTransport(self.settings)
                self.adb_exe = ht.exe_path
        return self.transport

    def _eng(self, name: str):
        if name not in self._engines:
            t = self._need_adb()
            s = self.settings
            if name == "adb":
                self._engines[name] = AdbEngine(t, s)
            elif name == "shell":
                self._engines[name] = ShellEngine(t, s)
            elif name == "input":
                self._engines[name] = InputEngine(t, s)
            elif name == "info":
                self._engines[name] = InfoEngine(t, s)
            elif name == "screen":
                self._engines[name] = ScreenEngine(t, s)
            elif name == "apps":
                self._engines[name] = AppsEngine(t, s,
                                                 authorizer=self._authorize)
            elif name == "files":
                self._engines[name] = FilesEngine(t, s)
            elif name == "intents":
                self._engines[name] = IntentEngine(t, s)
            elif name == "recovery":
                self._engines[name] = RecoveryEngine(t, s)
            elif name == "message":
                self._engines[name] = MessageEngine(t, s)
            elif name == "ui":
                self._engines[name] = UIEngine(t, s,
                                               input_engine=self._eng("input"))
            elif name == "vision":
                self._vision = VisionEngine(s, self._eng("screen"),
                                            self._eng("input"))
                self._engines[name] = self._vision
        return self._engines[name]

    def _authorize(self, op: str, detail: str) -> bool:
        try:
            return bool(self.authorizer(op, detail))
        except Exception:
            return False

    @staticmethod
    def _default_authorizer(op: str, detail: str) -> bool:
        # In library use, destructive operations require an explicit override.
        return False

    # ======================================================================
    # §5-6  Discovery & registration
    # ======================================================================
    def discover(self, *, usb: bool = True, wireless: bool = True,
                 reconnect_wireless: bool = False) -> List[dict]:
        """Enumerate attached devices (USB + already-paired wireless) and
        register a session for each. Deterministic in offline mode."""
        t = self._need_adb()
        adb = self._eng("adb")
        raw = adb.devices()
        profiles = []
        for serial, state in raw:
            profiles.append(self._upsert(serial, state))
        # offline mock transport lists mock serials already; ensure all present
        for serial in self.settings.mock_devices:
            if not self.registry.by_serial(serial):
                profiles.append(self._upsert(serial, "device"))
        return [self.status(p.device_id) for p in profiles]

    def _upsert(self, serial: str, state: str) -> DeviceSession:
        t = self._need_adb()
        session = DeviceSession(serial=serial, adb_state=state,
                                connection_type="usb" if ":" not in serial else "wifi")
        info = self._eng("info")
        try:
            prof = info.profile(serial)
            session.manufacturer = prof["manufacturer"]
            session.model = prof["model"]
            session.android_version = prof["android_version"]
            session.sdk_level = prof["sdk_level"]
            session.arch = prof["arch"]
            session.android_id = prof["android_id"]
            session.current_package = prof["current_package"]
            session.current_activity = prof["current_activity"]
            if ":" in serial:
                host, _, port = serial.partition(":")
                session.ip = host
                try:
                    session.port = int(port)
                except ValueError:
                    session.port = 0
        except Exception:
            pass
        if state == "device":
            session.connection_state = "connected"
            session.screen_state = "on"
        else:
            session.connection_state = "offline" if state == "offline" \
                else "unauthorized" if state == "unauthorized" else state
        session.last_seen = time.time()
        return self.registry.register(session)

    def connect_wireless(self, ip: str, port: int = 0) -> DeviceSession:
        """Pair-less wireless connect via `adb connect ip:port` (already trusted
        device), then register."""
        port = port or self.settings.adb_tcp_port
        self._eng("adb").connect(ip, port)
        serial = f"{ip}:{port}"
        state = self._eng("adb").state(serial)
        if state != "device":
            raise errors.DeviceOfflineError(
                f"could not connect to {serial} (state={state}). Pair first "
                f"via android.pair(ip, port, code) if it is a new device.")
        return self._upsert(serial, state)

    def pair(self, ip: str, port: int, code: str) -> bool:
        """Pair a new wireless-debugging device (Android 11+). Human must read
        the 6-digit pairing code from the phone."""
        ok = self._eng("adb").pair(ip, port, code)
        return ok

    def disconnect(self, serial_or_id: str) -> None:
        s = self._resolve_one(serial_or_id)
        if s.connection_type in ("wifi", "usb") and ":" in s.serial:
            host, _, port = s.serial.partition(":")
            self._eng("adb").disconnect(host, int(port) if port else 0)
        s.connection_state = "disconnected"
        s.adb_state = "offline"

    def forget(self, serial_or_id: str) -> bool:
        s = self._resolve_one(serial_or_id)
        return self.registry.remove(s.device_id)

    # ======================================================================
    # §28-29 selection & status
    # ======================================================================
    def select(self, query: Optional[str] = None) -> List[DeviceSession]:
        return self.registry.select(query)

    def _resolve_one(self, query: str) -> DeviceSession:
        found = self.registry.select(query)
        if len(found) > 1:
            raise errors.AmbiguousDeviceError(
                f"selection '{query}' matched {len(found)} devices: "
                + ", ".join(s.device_id for s in found))
        return found[0]

    def devices(self) -> List[dict]:
        return [self.status(s.device_id) for s in self.registry.all()]

    def status(self, serial_or_id: str) -> dict:
        s = self._by_id_or_serial(serial_or_id)
        # refresh light state if connected
        return s.profile()

    def _by_id_or_serial(self, ref: str) -> DeviceSession:
        try:
            return self.registry.get(ref)
        except errors.UnknownDeviceError:
            hit = self.registry.by_serial(ref)
            if hit:
                return hit
            # fuzzy single
            one = self.registry.select(ref)
            if len(one) == 1:
                return one[0]
            if not one:
                raise errors.UnknownDeviceError(f"no device: {ref}")
            raise errors.AmbiguousDeviceError(f"ambiguous device: {ref}")

    def capability_scan(self, serial_or_id: str) -> dict:
        s = self._by_id_or_serial(serial_or_id)
        have_scrcpy = bool(os.environ.get("AC_SCRCPY_PATH")) or _which("scrcpy")
        cap = scan_caps(s.serial, self._need_adb(), self.settings,
                        have_scrcpy=have_scrcpy)
        s.capabilities = cap
        return s.profile()

    def scan_all(self) -> List[dict]:
        return [self.capability_scan(d.device_id) for d in self.registry.all()]

    # ======================================================================
    # §21-22 lifecycle / recovery
    # ======================================================================
    def health_check(self, serial_or_id: str) -> dict:
        s = self._by_id_or_serial(serial_or_id)
        state = self._eng("adb").state(s.serial) if not self.offline else "device"
        before = s.connection_state
        s.connection_state = "connected" if state == "device" \
            else ("offline" if state == "offline" else state)
        s.last_seen = time.time()
        return {"device_id": s.device_id, "serial": s.serial,
                "was": before, "now": s.connection_state}

    def reconnect(self, serial_or_id: str) -> dict:
        s = self._by_id_or_serial(serial_or_id)
        host = s.ip or (s.serial.partition(":")[0] if ":" in s.serial else "")
        ok = self._eng("recovery").recover(s.serial, host=host, port=s.port)
        s.connection_state = "connected" if ok else "offline"
        s.adb_state = "device" if ok else "offline"
        if ok:
            self.capability_scan(s.device_id)
        return self.status(s.device_id)

    def recover_all(self) -> Dict[str, dict]:
        out = {}
        for s in self.registry.all():
            if s.connection_state != "connected":
                out[s.device_id] = self.reconnect(s.device_id)
        return out

    # convenience accessors used by skills/orchestrators
    @property
    def shell(self) -> ShellEngine:
        return self._eng("shell")

    @property
    def input(self) -> InputEngine:
        return self._eng("input")

    @property
    def screen(self) -> ScreenEngine:
        return self._eng("screen")

    @property
    def ui(self) -> UIEngine:
        return self._eng("ui")

    @property
    def apps(self) -> AppsEngine:
        return self._eng("apps")

    @property
    def files(self) -> FilesEngine:
        return self._eng("files")

    @property
    def intents(self) -> IntentEngine:
        return self._eng("intents")

    @property
    def info(self) -> InfoEngine:
        return self._eng("info")

    @property
    def message(self) -> MessageEngine:
        return self._eng("message")

    @property
    def vision(self) -> VisionEngine:
        return self._vision or self._eng("vision")

    # ------------------------------------------------------------------ #
    # Remote Touchpad companion backend (phone-as-PC-input, GPLv3 vendor)
    # ------------------------------------------------------------------ #
    def _backend(self, name: str):
        if name not in self._engines:
            if name == "remote_touchpad":
                from .backends.remote_touchpad import RemoteTouchpadBackend
                self._engines[name] = RemoteTouchpadBackend(self.settings)
        return self._engines[name]

    @property
    def remote_touchpad(self):
        return self._backend("remote_touchpad")

    def log_record(self, **kw):
        self.log.record(**kw)


def _which(name: str) -> Optional[str]:
    import shutil
    return shutil.which(name)
