"""Multi-device execution engine (§7, §8, §25, §26).

* :class:`MultiRunner` — run a per-device callable across a selection in
  parallel (or serially), collecting isolated per-device outcomes. Failure on
  one device never kills another (§25).
* :class:`DeviceGroups` — dynamic named device groups (all_devices, wifi,
  android_15, my_group, …) that can be created/modified/destroyed.

Supported targeting modes: single, explicit list, group, all, conditional,
per-device different tasks (via autonomous interpreter).
"""
from __future__ import annotations

import concurrent.futures
import time
from typing import Callable, Dict, List, Optional

from .. import errors
from ..result import (ActionResult, DeviceOutcome, FAILED, OFFLINE, RUNNING,
                      SUCCESS, UNSUPPORTED)
from ..devices.registry import DeviceRegistry, DeviceSession

# system group factories: (name, predicate)
SYSTEM_GROUP_RULES = {
    "all_devices": lambda s: True,
    "wifi_devices": lambda s: s.connection_type == "wifi",
    "adb_devices": lambda s: True,
    "usb_devices": lambda s: s.connection_type == "usb",
    "test_devices": lambda s: s.connection_type != "usb",  # alias to wireless in demo
}


class DeviceGroups:
    """Dynamic named groups over the registry. Group memberships are stored as
    device_ids so edits to the registry are reflected via lookups."""

    def __init__(self, registry: DeviceRegistry):
        self._registry = registry
        self._user: Dict[str, List[str]] = {}

    def create(self, name: str, device_ids: List[str]) -> None:
        if name in SYSTEM_GROUP_RULES:
            raise errors.AndroidControlError(f"'{name}' is a reserved group")
        ids = [self._resolve_any(d).device_id for d in device_ids]
        self._user[name] = ids

    def add(self, name: str, device_ids: List[str]) -> None:
        self._user.setdefault(name, [])
        for d in device_ids:
            sid = self._resolve_any(d).device_id
            if sid not in self._user[name]:
                self._user[name].append(sid)

    def remove(self, name: str, device_ids: List[str]) -> None:
        sids = {self._resolve_any(d).device_id for d in device_ids}
        self._user[name] = [x for x in self._user.get(name, []) if x not in sids]

    def destroy(self, name: str) -> None:
        self._user.pop(name, None)

    def members(self, name: str) -> List[DeviceSession]:
        if name in SYSTEM_GROUP_RULES:
            return [s for s in self._registry.connected()
                    if SYSTEM_GROUP_RULES[name](s)]
        ids = self._user.get(name, [])
        return [self._registry.get(i) for i in ids if i in self._registry.ids()]

    def names(self) -> List[str]:
        return list(SYSTEM_GROUP_RULES) + list(self._user)

    def _resolve_any(self, ref: str) -> DeviceSession:
        try:
            return self._registry.get(ref)
        except errors.UnknownDeviceError:
            hit = self._registry.by_serial(ref)
            if hit:
                return hit
        one = self._registry.select(ref)
        if len(one) == 1:
            return one[0]
        raise errors.AmbiguousDeviceError(f"ambiguous: {ref}")


class MultiRunner:
    """Execute a callable across a device selection with isolation."""

    def __init__(self, operation: str, timeout_each_s: float = 60.0):
        self.operation = operation
        self.timeout_each_s = timeout_each_s

    def run(self, sessions: List[DeviceSession],
            fn: Callable[[DeviceSession], dict], *,
            parallel: bool = True) -> ActionResult:
        """``fn(session) -> dict(status, data?, error?)`` per device.

        Returns an ActionResult whose per-device outcomes are isolated.
        """
        outcomes: Dict[str, DeviceOutcome] = {}
        t0 = time.monotonic()

        def _exec(s: DeviceSession) -> DeviceOutcome:
            if s.connection_state != "connected":
                return DeviceOutcome(s.device_id, serial=s.serial,
                                     model=s.model, status=OFFLINE,
                                     error="device not connected")
            try:
                r = fn(s)
                status = r.get("status", SUCCESS) if isinstance(r, dict) else SUCCESS
                data = r.get("data") if isinstance(r, dict) else r
                return DeviceOutcome(s.device_id, serial=s.serial,
                                     model=s.model, status=status,
                                     data=data, verification=r.get("verification", ""))
            except errors.DeviceOfflineError as e:
                return DeviceOutcome(s.device_id, serial=s.serial,
                                     model=s.model, status=OFFLINE, error=str(e))
            except errors.RequiresAuthorizationError as e:
                return DeviceOutcome(s.device_id, serial=s.serial,
                                     model=s.model,
                                     status="REQUIRES_AUTHORIZATION",
                                     error=str(e))
            except errors.UnsupportedOperationError as e:
                return DeviceOutcome(s.device_id, serial=s.serial,
                                     model=s.model, status=UNSUPPORTED,
                                     error=str(e))
            except Exception as e:  # noqa: BLE001
                return DeviceOutcome(s.device_id, serial=s.serial,
                                     model=s.model, status=FAILED, error=str(e))

        if not parallel or len(sessions) <= 1:
            for s in sessions:
                oc = _exec(s)
                outcomes[oc.device_id] = oc
        else:
            max_workers = len(sessions)
            with concurrent.futures.ThreadPoolExecutor(
                    max_workers=max_workers) as ex:
                futs = {ex.submit(_exec, s): s for s in sessions}
                for fut in concurrent.futures.as_completed(futs):
                    try:
                        oc = fut.result()
                        outcomes[oc.device_id] = oc
                    except Exception as e:  # noqa: BLE001
                        s = futs[fut]
                        outcomes[s.device_id] = DeviceOutcome(
                            s.device_id, serial=s.serial, model=s.model,
                            status=FAILED, error=f"worker error: {e}")

        act = ActionResult(self.operation,
                           devices=[outcomes[s.device_id]
                                    for s in sessions
                                    if s.device_id in outcomes])
        act.duration_ms = (time.monotonic() - t0) * 1000.0
        act.aggregate_from_outcomes()
        return act
