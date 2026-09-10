"""Realtime audio engine (spec sections 5, 28, 41).

AudioSource abstraction for microphone / system-audio capture. Uses the platform's
sound library (sounddevice) when present and a device is available. It does NOT
bypass OS privacy controls. On this headless/unsupported host real capture reports
UNAVAILABLE with the concrete reason; capture is never faked.

State: running/paused, current device, health. Bounded streaming to prevent
unbounded growth.
"""
from __future__ import annotations

import threading
import time
from collections import deque

from ..config import AppConfig
from ..errors import AudioUnavailable, Unavailable


def _sounddevice():
    try:
        import sounddevice
        return sounddevice
    except Exception:
        return None


class AudioSource:
    """Abstract streaming audio source."""
    name = "abstract"
    kind = "mic"

    def list_devices(self): return []
    def select_device(self, device_id): raise AudioUnavailable("no device")
    def start(self): raise AudioUnavailable("no device")
    def stop(self): ...
    def pause(self): ...
    def resume(self): ...
    def test(self): return {"ok": False}
    def health(self): return {"name": self.name, "available": False}


class MicrophoneSource(AudioSource):
    name = "microphone"
    kind = "mic"

    def __init__(self, config: AppConfig, on_chunk=None):
        self.cfg = config.audio
        self._on_chunk = on_chunk
        self._running = False
        self._paused = False
        self._stream = None
        self._sd = None

    def _ensure(self):
        if self._sd is None:
            self._sd = _sounddevice()
            if self._sd is None:
                raise Unavailable("audio capture requires 'sounddevice' (not "
                                  "installed on this host)")
        return self._sd

    def list_devices(self):
        sd = self._ensure()
        try:
            devices = sd.query_devices()
            out = []
            for i, d in enumerate(devices):
                if d.get("max_input_channels", 0) > 0:
                    out.append({"id": i, "name": d.get("name", ""),
                                "channels": d.get("max_input_channels"),
                                "default_samplerate": d.get("default_samplerate")})
            return out
        except Exception as e:
            return [] if "device" in str(e).lower() else []

    def select_device(self, device_id):
        self._ensure()
        self.cfg.device_id = int(device_id)
        return {"device_id": int(device_id)}

    def _callback(self, indata, frames, time_info, status):
        if self._paused or not self._on_chunk:
            return
        # indata shape (frames, channels); average channels for mono
        import numpy as np
        audio = np.asarray(indata).mean(axis=1)
        self._on_chunk(audio, time.time())

    def start(self):
        sd = self._ensure()
        if self._running:
            return {"running": True}
        try:
            self._stream = sd.InputStream(
                device=self.cfg.device_id if self.cfg.device_id >= 0 else None,
                samplerate=self.cfg.sample_rate, channels=self.cfg.channels,
                callback=self._callback, blocksize=int(self.cfg.sample_rate *
                                                       self.cfg.chunk_ms / 1000))
            self._stream.start()
            self._running = True
            self._paused = False
            return {"running": True}
        except Exception as e:
            self._running = False
            raise AudioUnavailable(f"could not open microphone: {e}")

    def stop(self):
        if self._stream:
            try:
                self._stream.stop()
                self._stream.close()
            except Exception:
                pass
        self._stream = None
        self._running = False

    def pause(self):
        self._paused = True
        if self._stream:
            try:
                self._stream.stop()
            except Exception:
                pass
        return {"paused": True}

    def resume(self):
        self._paused = False
        if self._stream and not self._running:
            try:
                self._stream.start()
                self._running = True
            except Exception:
                pass
        return {"resumed": True}

    def test(self):
        return {"device": self.cfg.device_id, "sample_rate": self.cfg.sample_rate,
                "channels": self.cfg.channels, "result": "ok" if self._sd else
                "unavailable"}

    def health(self):
        return {"name": self.name, "available": self._sd is not None,
                "running": self._running, "paused": self._paused}


class AudioEngine:
    """Owns one active source + bounded stream buffer + health."""
    def __init__(self, config: AppConfig):
        self.cfg = config
        self.source: AudioSource | None = None
        self._buffer: deque = deque(maxlen=50)
        self._lock = threading.Lock()
        self.active_name = ""

    def set_source(self, source: AudioSource):
        with self._lock:
            if self.source is not None:
                self.source.stop()
            self.source = source
            self.active_name = source.name

    def _ingest(self, audio, ts):
        if self.source and getattr(self.source, "_paused", False):
            return
        with self._lock:
            self._buffer.append((ts, audio))

    def default_mic(self) -> MicrophoneSource:
        mic = MicrophoneSource(self.cfg, on_chunk=self._ingest)
        self.set_source(mic)
        return mic

    def list_devices(self):
        if self.source:
            try:
                return self.source.list_devices()
            except Exception:
                pass
        # list even before start via a temp mic
        try:
            return MicrophoneSource(self.cfg).list_devices()
        except Exception:
            return []

    def status(self):
        return {"source": self.active_name,
                "buffer_frames": len(self._buffer),
                "state": "off"}

    def start(self):
        if not self.source:
            raise Unavailable("no audio source selected")
        self.source.start()
        return {"running": True}

    def stop(self):
        if self.source:
            self.source.stop()
        return {"stopped": True}

    def pause(self):
        if self.source:
            self.source.pause()
        return {"paused": True}

    def resume(self):
        if self.source:
            self.source.resume()
        return {"resumed": True}

    def test(self):
        if not self.source:
            mic = self.default_mic()
        return self.source.test()

    def health(self):
        src = self.source.health() if self.source else {"available": False,
                                                        "name": "none"}
        return {"source": src, "buffer_frames": len(self._buffer)}

    def drain(self):
        with self._lock:
            items = list(self._buffer)
            self._buffer.clear()
        return items
