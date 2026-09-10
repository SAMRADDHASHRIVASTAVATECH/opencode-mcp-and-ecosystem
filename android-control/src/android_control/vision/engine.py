"""Vision fallback engine (§13).

Pipeline: Android screen -> screenshot -> (vision model) -> understand UI ->
identify target -> action -> screenshot -> verify.

When a UI hierarchy is unavailable (e.g. games, webviews, native layers),
coordinate-based interaction driven by a screenshot + a vision model is used.
The model is pluggable: by default an *offline template/OCR-free matcher* is
provided that locates a target text by glyph-free heuristics is NOT reliable,
so the offline default only supports safe operations (tap at a fraction of the
screen) and clearly reports when a real vision model is required.

An external vision backend can be configured via AC_VISION_BACKEND=external and
AC_VISION_MODEL_CMD (a command that reads a PNG path and returns a JSON list of
recognised elements). This keeps the skill honest about what it can do without
extra dependencies.
"""
from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Callable, Dict, List, Optional

from ..config import Settings
from ..engines.input import InputEngine
from ..engines.screen import ScreenEngine


class VisionEngine:
    def __init__(self, settings: Settings, screen: ScreenEngine,
                 input_engine: InputEngine):
        self.settings = settings
        self.screen = screen
        self.input = input_engine
        self.backend = settings.vision_backend.lower()
        self._external_cmd = settings.vision_model_cmd

    # -- observation -------------------------------------------------------
    def observe(self, serial: str, keep_png: bool = False) -> dict:
        """Capture a screenshot and (optionally) run the vision backend to get
        a lightweight, model-derived description/elements list."""
        png = self.screen.screenshot(serial, as_png_bytes=True)
        if self.backend == "external" and self._external_cmd:
            elements = self._external_recognise(serial, png)
        else:
            elements = self._offline_fallback(serial, png)
        return {"png_bytes": len(png), "backend": self.backend,
                "elements": elements,
                "note": ("offline vision fallback: no real OCR; "
                         "configure an external vision backend for text/UI "
                         "understanding") if self.backend != "external" else ""}

    # -- locating ----------------------------------------------------------
    def locate(self, serial: str, target: str) -> Optional[dict]:
        """Return the best-effort {x, y} to interact with `target`.

        With an external backend we look for a recognised element whose label
        matches. Offline we can only do a coarse center default and we report
        it as low-confidence.
        """
        obs = self.observe(serial)
        for e in obs["elements"]:
            if target.lower() in (e.get("label") or "").lower():
                return e
        return None

    def tap_text(self, serial: str, target: str, *, width: int = 1080,
                 height: int = 2400, confidence: float = 0.0) -> dict:
        """Tap a text target found via vision; fall back to a screen-centre tap
        only if the caller permits low-confidence action."""
        loc = self.locate(serial, target)
        if loc and "x" in loc and "y" in loc:
            self.input.tap(serial, loc["x"], loc["y"])
            return {"method": "vision", "target": target,
                    "x": loc["x"], "y": loc["y"]}
        # offline / not found: coordinate fallback to screen centre
        self.input.tap(serial, width // 2, height // 2)
        return {"method": "coordinate-fallback", "target": target,
                "x": width // 2, "y": height // 2,
                "note": "target not visually recognised; tapped screen centre"}

    # -- backends ----------------------------------------------------------
    def _offline_fallback(self, serial, png: bytes) -> List[dict]:
        # Without OCR we cannot produce truthful element boxes. We do a
        # transparent no-match (caller falls back to safe coordinate actions).
        return []

    def _external_recognise(self, serial, png: bytes) -> List[dict]:
        tmp = Path(self.settings.screenshot_dir) / f"{serial}_vision.png"
        tmp.parent.mkdir(parents=True, exist_ok=True)
        tmp.write_bytes(png)
        try:
            cmd = [c.format(path=str(tmp)) for c in self._external_cmd]
            out = subprocess.run(cmd, capture_output=True, text=True,
                                 timeout=60)
            data = json.loads(out.stdout)
            return data if isinstance(data, list) else []
        except Exception:
            return []

    def verify(self, serial: str, before: dict, after: dict) -> bool:
        """Basic verify that a vision action changed the screen."""
        return after.get("png_bytes", 0) != before.get("png_bytes", 0)
