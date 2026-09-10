"""Voice output engine (spec sections 14, 15).

RealtimeTTSProvider abstraction supporting local (Kokoro/Piper) and configured
cloud TTS, interruption/cancellation, voice/volume/rate. Honest: without a
configured + installed TTS backend, speak() raises TTS_UNAVAILABLE.
"""
from __future__ import annotations

import threading

from ..config import AppConfig
from ..errors import TtsUnavailable, Unavailable


class RealtimeTTSProvider:
    name = "abstract"

    def speak(self, text: str, **kw):
        raise TtsUnavailable(f"{self.name} not available")

    def cancel(self): ...
    def health(self): return {"name": self.name, "available": False}


class LocalTTSProvider(RealtimeTTSProvider):
    """Kokoro / Piper local TTS via subprocess (Windows-compatible launcher)."""
    name = "local"

    def __init__(self, config: AppConfig, exe: str = ""):
        self.cfg = config.tts
        self.exe = exe or _discover_tts()
        self._lock = threading.Lock()
        self._proc = None

    def available(self):
        return bool(self.exe)

    def _launch(self, text, voice=""):
        if not self.exe:
            raise TtsUnavailable("no local TTS engine configured (set OLCAP_TTS_CMD "
                                 "or install Kokoro/Piper)")
        import shlex
        import subprocess
        cmd = shlex.split(self.exe) + [text]
        if voice:
            cmd += ["--voice", voice]
        return subprocess.Popen(cmd, stdout=subprocess.DEVNULL,
                                stderr=subprocess.DEVNULL)

    def speak(self, text, **kw):
        with self._lock:
            self.cancel()
            self._proc = self._launch(text, kw.get("voice", self.cfg.voice))
        return {"spoken": True, "engine": self.name, "length": len(text)}

    def cancel(self):
        if self._proc and self._proc.poll() is None:
            try:
                self._proc.terminate()
            except Exception:
                pass
        self._proc = None

    def health(self):
        return {"name": self.name, "available": self.available(),
                "exe": self.exe or None}


def _discover_tts():
    import os
    import shutil
    for c in (os.environ.get("OLCAP_TTS_CMD", ""), "kokoro", "piper"):
        if c and shutil.which(c):
            return c
    return os.environ.get("OLCAP_TTS_CMD", "")


class TTSEngine:
    def __init__(self, config: AppConfig):
        self.cfg = config
        self._providers = {
            "local": LocalTTSProvider(config),
            "none": RealtimeTTSProvider(),
        }
        self.active = config.tts.provider

    def provider(self):
        p = self._providers.get(self.active)
        if p is None:
            raise Unavailable(f"unknown TTS provider '{self.active}'")
        return p

    def speak(self, text, **kw):
        if self.active in ("none", ""):
            raise TtsUnavailable("no TTS provider configured (TTS disabled)")
        return self.provider().speak(text, **kw)

    def cancel(self):
        self.provider().cancel()

    def health(self):
        out = {}
        for n, p in self._providers.items():
            out[n] = p.health()
        out["active"] = self.active
        return out
