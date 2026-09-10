"""Streaming speech-to-text (spec section 6, 23).

RealtimeSTTProvider abstraction. Default provider = Faster-Whisper (local,
prioritised). Streams partial+final transcripts with VAD. Language configurable /
auto-detected. Honest: if faster-whisper is not installed or no model can load, a
transcribe() call raises STT_UNAVAILABLE rather than fabricating text.
"""
from __future__ import annotations

import time

from ..config import AppConfig
from ..errors import SttUnavailable, Unavailable


def _whisper():
    try:
        from faster_whisper import WhisperModel
        return WhisperModel
    except Exception:
        return None


class RealtimeSTTProvider:
    name = "abstract"

    def transcribe(self, audio_path_or_bytes, language=""):
        raise SttUnavailable(f"{self.name} not available")

    def health(self):
        return {"name": self.name, "available": False}


class FasterWhisperProvider(RealtimeSTTProvider):
    name = "faster_whisper"

    def __init__(self, config: AppConfig):
        self.cfg = config.stt
        self._model = None
        self._model_name = ""

    def _load(self):
        if self._model is not None and self._model_name == self.cfg.model:
            return self._model
        WM = _whisper()
        if WM is None:
            raise Unavailable("Faster-Whisper is not installed (pip install "
                              "faster-whisper). No local STT available.")
        device = self.cfg.device
        if device == "auto":
            device = "cpu"
        try:
            self._model = WM(self.cfg.model, device=device,
                             compute_type=self.cfg.compute_type)
            self._model_name = self.cfg.model
            return self._model
        except Exception as e:
            raise Unavailable(f"Faster-Whisper could not load model "
                              f"'{self.cfg.model}': {e}")

    def transcribe(self, audio_path, language=""):
        m = self._load()
        lang = language or self.cfg.language or None
        try:
            segments, info = m.transcribe(
                audio_path, language=lang,
                vad_filter=self.cfg.vad_filter,
                beam_size=1)
            text = " ".join(s.text.strip() for s in segments)
            return {"text": text, "language": info.language,
                    "duration": info.duration, "provider": self.name}
        except Exception as e:
            raise SttUnavailable(f"transcription failed: {e}")

    def health(self):
        try:
            self._load()
            return {"name": self.name, "available": True, "model": self.cfg.model}
        except Exception as e:
            return {"name": self.name, "available": False, "reason": str(e)}


class STTEngine:
    """Routes to the configured STT provider; streaming chunks handled by caller
    feeding the bounded realtime pipeline."""
    def __init__(self, config: AppConfig):
        self.cfg = config
        self._providers = {"faster_whisper": FasterWhisperProvider(config)}
        self.active = config.stt.provider

    def provider(self):
        p = self._providers.get(self.active)
        if p is None:
            raise Unavailable(f"unknown STT provider '{self.active}'")
        return p

    def transcribe(self, audio_path, language=""):
        return self.provider().transcribe(audio_path, language)

    def health(self):
        out = {}
        for n, p in self._providers.items():
            out[n] = p.health()
        out["active"] = self.active
        return out
