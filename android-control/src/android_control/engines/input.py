"""Complete input control engine (§11): tap, double-tap, long-press, swipe,
drag, scroll, text, key events, back/home/recents/volume/power.
"""
from __future__ import annotations

from typing import Optional

from ..config import Settings
from .base import EngineBase

# Android key codes (subset, stable across versions)
KEYCODE = {
    "home": 3, "back": 4, "call": 5, "endcall": 6, "0": 7, "1": 8, "2": 9,
    "3": 10, "4": 11, "5": 12, "6": 13, "7": 14, "8": 15, "9": 16,
    "star": 17, "pound": 18, "up": 19, "down": 20, "left": 21, "right": 22,
    "enter": 66, "del": 67, "tab": 61, "space": 62, "clear": 28,
    "volume_up": 24, "volume_down": 25, "power": 26, "camera": 27,
    "menu": 82, "notifications": 83, "search": 84, "recents": 187,
    "app_switch": 187, "backspace": 67, "escape": 111, "dpad_center": 23,
    "page_up": 92, "page_down": 93, "comma": 55, "period": 56,
}


class InputEngine(EngineBase):
    def __init__(self, transport, settings: Settings):
        super().__init__(transport, settings)

    def _input(self, serial: str, *argv: str) -> None:
        cmd = "input " + " ".join(argv)
        res = self._shell(serial, cmd)
        if not res.ok:
            raise Exception(f"input[{serial}] failed: {res.error}")

    def tap(self, serial: str, x: int, y: int) -> None:
        self._input(serial, "tap", str(int(x)), str(int(y)))

    def double_tap(self, serial: str, x: int, y: int) -> None:
        for _ in range(2):
            self.tap(serial, x, y)

    def long_press(self, serial: str, x: int, y: int,
                   duration_ms: int = 600) -> None:
        self.swipe(serial, x, y, x, y, duration_ms)

    def swipe(self, serial: str, x1: int, y1: int, x2: int, y2: int,
              duration_ms: int = 300) -> None:
        self._input(serial, "swipe", str(int(x1)), str(int(y1)),
                    str(int(x2)), str(int(y2)), str(int(duration_ms)))

    def drag(self, serial: str, x1: int, y1: int, x2: int, y2: int,
             duration_ms: int = 600) -> None:
        self.swipe(serial, x1, y1, x2, y2, duration_ms)

    def scroll(self, serial: str, direction: str = "down",
               steps: int = 4) -> None:
        dur = str(int(300 * steps))
        if direction.lower() in ("down", "up"):
            if direction.lower() == "down":
                self._input(serial, "swipe", "540", "1500", "540", "500", dur)
            else:
                self._input(serial, "swipe", "540", "500", "540", "1500", dur)
        elif direction.lower() in ("left", "right"):
            if direction.lower() == "right":
                self._input(serial, "swipe", "200", "1200", "880", "1200", dur)
            else:
                self._input(serial, "swipe", "880", "1200", "200", "1200", dur)
        else:
            raise ValueError(f"unknown scroll direction: {direction}")

    def text(self, serial: str, text: str) -> None:
        """Type text. Uses `input text` escaping spaces (reliable method)."""
        safe = text.replace(" ", "%s")
        self._input(serial, "text", safe)

    def key(self, serial: str, keycode: str) -> None:
        code = KEYCODE.get(keycode.lower(), keycode)
        self._input(serial, "keyevent", str(code))

    # -- high-level navigational helpers -----------------------------------
    def back(self, serial: str) -> None:
        self.key(serial, "back")

    def home(self, serial: str) -> None:
        self.key(serial, "home")

    def recents(self, serial: str) -> None:
        self.key(serial, "recents")

    def volume_up(self, serial: str, n: int = 1) -> None:
        for _ in range(n):
            self.key(serial, "volume_up")

    def volume_down(self, serial: str, n: int = 1) -> None:
        for _ in range(n):
            self.key(serial, "volume_down")
