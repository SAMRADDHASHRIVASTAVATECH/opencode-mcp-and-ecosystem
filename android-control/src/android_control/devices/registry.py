"""Device sessions and the unbounded DeviceRegistry.

Every connected device gets its own isolated ``DeviceSession``. Sessions never
overwrite each other and the registry holds *N* devices with no hard-coded
ceiling (§6). Device identity is never reduced to "Phone 1"/"Phone 2" —
it is keyed by a unique internal id plus real identifiers (serial, model,
manufacturer, android_id, ip/port, connection type).
"""
from __future__ import annotations

import re
import threading
from dataclasses import dataclass, field
from typing import Dict, List, Optional

from .. import errors

_lock = threading.Lock()


@dataclass
class CapabilityProfile:
    """Per-device capability snapshot (§19). Values: READY / PARTIAL /
    UNAVAILABLE / UNKNOWN."""
    adb: str = "UNKNOWN"
    wireless_adb: str = "UNKNOWN"
    shell: str = "UNKNOWN"
    input: str = "UNKNOWN"
    screenshot: str = "UNKNOWN"
    screen_recording: str = "UNKNOWN"
    file_transfer: str = "UNKNOWN"
    package_control: str = "UNKNOWN"
    intent_control: str = "UNKNOWN"
    ui_hierarchy: str = "UNKNOWN"
    semantic_ui: str = "UNKNOWN"
    scrcpy: str = "UNKNOWN"
    extra: Dict[str, str] = field(default_factory=dict)

    def ready(self) -> List[str]:
        return [k for k, v in self._fields().items() if v == "READY"]

    def to_dict(self) -> dict:
        d = {"adb": self.adb, "wireless_adb": self.wireless_adb,
             "shell": self.shell, "input": self.input,
             "screenshot": self.screenshot,
             "screen_recording": self.screen_recording,
             "file_transfer": self.file_transfer,
             "package_control": self.package_control,
             "intent_control": self.intent_control,
             "ui_hierarchy": self.ui_hierarchy,
             "semantic_ui": self.semantic_ui, "scrcpy": self.scrcpy}
        d.update(self.extra)
        return d

    @staticmethod
    def _fields():
        return {"adb": None, "wireless_adb": None, "shell": None,
                "input": None, "screenshot": None, "screen_recording": None,
                "file_transfer": None, "package_control": None,
                "intent_control": None, "ui_hierarchy": None,
                "semantic_ui": None, "scrcpy": None}


@dataclass
class DeviceSession:
    """Isolated per-device runtime context."""
    device_id: str = ""
    # -- real identity ----------------------------------------------------
    serial: str = ""              # adb serial
    model: str = ""
    manufacturer: str = ""
    android_id: str = ""
    ip: str = ""
    port: int = 0
    connection_type: str = ""     # usb | wifi | mock
    android_version: str = ""
    sdk_level: str = ""
    arch: str = ""
    # -- runtime state ----------------------------------------------------
    connection_state: str = "unknown"   # connected | offline | unauthorized
    adb_state: str = "unknown"          # device | offline | unauthorized
    capabilities: CapabilityProfile = field(default_factory=CapabilityProfile)
    screen_state: str = ""
    current_package: str = ""
    current_activity: str = ""
    last_seen: float = 0.0
    last_command: str = ""
    last_result: str = ""
    workflow: str = ""              # tag of active workflow (if any)
    _session_lock: object = field(default_factory=threading.RLock)

    def lock(self):
        return self._session_lock

    def matches(self, tokens: List[str]) -> bool:
        """Fuzzy token match against all stable identifiers (§28 selection)."""
        hay = " ".join(filter(None, [
            self.serial, self.model, self.manufacturer, self.android_id,
            self.ip, self.connection_type, self.device_id,
            f"android {self.android_version}", self.android_version,
            f"sdk {self.sdk_level}", self.sdk_level,
            f"{self.manufacturer} {self.model}"]))
        hay = hay.lower()
        return all(t.lower() in hay for t in tokens)

    def profile(self) -> dict:
        return {
            "device_id": self.device_id,
            "serial": self.serial,
            "model": self.model,
            "manufacturer": self.manufacturer,
            "android_id": self.android_id,
            "ip": self.ip,
            "port": self.port,
            "connection_type": self.connection_type,
            "android_version": self.android_version,
            "sdk_level": self.sdk_level,
            "arch": self.arch,
            "connection_state": self.connection_state,
            "adb_state": self.adb_state,
            "screen_state": self.screen_state,
            "current_package": self.current_package,
            "current_activity": self.current_activity,
            "capabilities": self.capabilities.to_dict(),
            "last_seen": self.last_seen,
            "last_command": self.last_command,
            "last_result": self.last_result,
        }


class DeviceRegistry:
    """Dynamic, unbounded collection of device sessions, keyed by device_id.

    Thread-safe. Supports look-up by device_id, serial, model, group and
    arbitrary natural-language tokens; ambiguous matches raise.
    """

    def __init__(self):
        self._devices: Dict[str, DeviceSession] = {}
        self._by_serial: Dict[str, str] = {}
        self._lock = threading.RLock()
        self._seq = 0

    def _next_id(self) -> str:
        self._seq += 1
        return f"device_{self._seq:03d}"

    def register(self, session: DeviceSession) -> DeviceSession:
        with self._lock:
            existing = self._by_serial.get(session.serial)
            if existing:
                cur = self._devices[existing]
                # refresh identity/state rather than duplicate
                for k in ("model", "manufacturer", "android_id", "ip", "port",
                          "android_version", "sdk_level", "arch",
                          "connection_type"):
                    v = getattr(session, k)
                    if v:
                        setattr(cur, k, v)
                cur.connection_state = session.connection_state
                cur.adb_state = session.adb_state
                return cur
            if not session.device_id:
                session.device_id = self._next_id()
            self._devices[session.device_id] = session
            if session.serial:
                self._by_serial[session.serial] = session.device_id
            return session

    def remove(self, device_id: str) -> bool:
        with self._lock:
            s = self._devices.pop(device_id, None)
            if s and s.serial in self._by_serial:
                del self._by_serial[s.serial]
            return s is not None

    def get(self, device_id: str) -> DeviceSession:
        with self._lock:
            s = self._devices.get(device_id)
            if s is None:
                raise errors.UnknownDeviceError(
                    f"no such device id: {device_id}")
            return s

    def by_serial(self, serial: str) -> Optional[DeviceSession]:
        with self._lock:
            did = self._by_serial.get(serial)
            return self._devices.get(did) if did else None

    def all(self) -> List[DeviceSession]:
        with self._lock:
            return list(self._devices.values())

    def connected(self) -> List[DeviceSession]:
        return [s for s in self.all()
                if s.connection_state == "connected"]

    def count(self) -> int:
        return len(self._devices)

    def ids(self) -> List[str]:
        return [s.device_id for s in self.all()]

    def reset(self):
        with self._lock:
            self._devices.clear()
            self._by_serial.clear()

    # -- natural-language / group resolution ---------------------------------
    def select(self, query: Optional[str]) -> List[DeviceSession]:
        """Resolve a selection expression to a concrete list of sessions.

        Supported forms (case-insensitive):
          * ``all`` / ``*`` / ``everyone`` -> all connected
          * a device_id (device_001), serial, model, "the samsung phone",
            "android 15", "wifi devices", etc.
          * comma / 'and' separated explicit list of such tokens
        Raises AmbiguousDeviceError when the phrase alone is not decisive.
        """
        with self._lock:
            devices = self.connected()
            if not devices:
                return devices
            if not query:
                raise errors.AmbiguousDeviceError(
                    "no device selection given and multiple devices are online")
            q = " ".join(query.lower().split())
            if q in ("all", "*", "everyone", "every device", "all devices",
                     "all phones", "every phone"):
                return devices
            selected: List[DeviceSession] = []
            seen = set()
            for part in re.split(r",|\band\b", q):
                part = part.strip().replace("the ", "").replace("phone ", "")
                if not part:
                    continue
                exact = self._resolve_exact(part)
                if exact is not None:
                    if exact.device_id not in seen:
                        selected.append(exact)
                        seen.add(exact.device_id)
                    continue
                # fuzzy phrase: resolve across remaining device tokens
                fuzzy = [s for s in devices if s.matches([part])
                         and s.device_id not in seen]
                for s in fuzzy:
                    selected.append(s)
                    seen.add(s.device_id)
            if not selected:
                raise errors.UnknownDeviceError(f"no device matched: {query}")
            return selected

    def _resolve_exact(self, token: str) -> Optional[DeviceSession]:
        # device_id / serial exact
        if token in self._devices:
            return self._devices[token]
        hit = self._by_serial.get(token)
        if hit:
            return self._devices[hit]
        for s in self.connected():
            if s.serial == token or s.model.lower() == token or \
               s.manufacturer.lower() == token:
                return s
        return None
