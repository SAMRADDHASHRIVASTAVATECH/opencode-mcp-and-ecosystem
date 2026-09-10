"""Two primary modes + switching (spec sections 2, 3, 4).

Default mode is OFF/INACTIVE. Microphone / continuous screen monitoring are
NEVER silently activated - activation is explicit via mode.set/start.

Distinct policies per mode:
  * interview   - audio+transcript+reasoning priority (no screen by default)
  * workspace   - audio + screen-changes + context reasoning
"""
from __future__ import annotations

import time

from .config import AppConfig
from .errors import ModeInactive
from .events import EventBus

VALID_MODES = {"off", "interview", "workspace"}


class ModeManager:
    def __init__(self, config: AppConfig, bus: EventBus):
        self.cfg = config
        self.bus = bus
        self.mode = config.default_mode if config.default_mode in VALID_MODES else "off"
        self.sub_mode = ""          # e.g. "coding" inside interview
        self.paused = False
        self._flags = {
            "microphone": False,    # explicit enablements
            "screen": False,
            "system_audio": False,
        }
        self.status = {"screen": "OFF", "microphone": "OFF",
                       "system_audio": "OFF", "ai": "IDLE"}

    def get(self) -> dict:
        return {"mode": self.mode, "sub_mode": self.sub_mode, "paused": self.paused,
                "status": dict(self.status)}

    def set_mode(self, mode: str) -> dict:
        if mode not in VALID_MODES:
            raise ValueError(f"mode must be one of {sorted(VALID_MODES)}")
        old = self.mode
        self.mode = mode
        self.bus.publish("mode.changed",
                         {"from": old, "to": mode, "ts": time.time()})
        # Only workspace mode may enable screen monitoring; never auto.
        if mode != "workspace":
            self._flags["screen"] = False
            self.status["screen"] = "OFF"
        if mode == "off":
            self._clear_activity()
        self._emit_status()
        return self.get()

    def _clear_activity(self):
        for k in self._flags:
            self._flags[k] = False
        self.status.update({"screen": "OFF", "microphone": "OFF",
                            "system_audio": "OFF", "ai": "IDLE"})

    def _emit_status(self):
        self.bus.publish("state.changed", {"mode": self.mode, "status": dict(self.status)})

    # ---- per-sensor enable (explicit only) ---- #
    def set_sensor(self, sensor: str, enabled: bool, mode_required: str = "") -> dict:
        if enabled and mode_required and self.mode != mode_required:
            raise ModeInactive(
                f"cannot enable {sensor} in mode '{self.mode}' "
                f"(requires '{mode_required}')")
        if enabled and self.mode == "off":
            raise ModeInactive("cannot enable capture while mode is 'off'")
        self._flags[sensor] = enabled
        key = {"microphone": "microphone", "screen": "screen",
               "system_audio": "system_audio"}.get(sensor)
        if key:
            self.status[key] = "ACTIVE" if enabled else ("PAUSED" if self.paused else "OFF")
        self._emit_status()
        return self.get()

    # ---- pause / resume ---- #
    def pause(self) -> dict:
        if self.mode == "off":
            raise ModeInactive("assistant is OFF")
        self.paused = True
        for k in ("screen", "microphone", "system_audio"):
            if self._flags.get(k):
                self.status[k] = "PAUSED"
        self.bus.publish("session.paused", {"mode": self.mode})
        self._emit_status()
        return self.get()

    def resume(self) -> dict:
        self.paused = False
        for k in ("screen", "microphone", "system_audio"):
            if self._flags.get(k):
                self.status[k] = "ACTIVE"
        self.bus.publish("session.resumed", {"mode": self.mode})
        self._emit_status()
        return self.get()

    def set_ai(self, state: str):
        if state in ("ACTIVE", "IDLE"):
            self.status["ai"] = state

    @property
    def active(self) -> bool:
        return self.mode != "off" and not self.paused and not self._emergency()

    def _emergency(self):
        return False
