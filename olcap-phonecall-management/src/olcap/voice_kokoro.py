"""Kokoro GPU-accelerated realtime voice provider.

Routes TTS through the Kokoro-82M pipeline running on CUDA (RTX 2050) via the
warm GPU server at OLCAP_VOICE_API_URL (default http://127.0.0.1:8899).

Design for lowest latency:
  * Model stays resident in GPU memory (warm server, no cold start).
  * HTTP/1.1 keep-alive connection pool (no per-request TCP handshake).
  * Synthesis runs in a background thread so the MCP control path is non-blocking.
  * Audio plays through the PC speakers (or routed to the phone via android_bridge).
"""
from __future__ import annotations

import threading
import time
from concurrent.futures import ThreadPoolExecutor

import httpx

from .errors import AiProviderUnavailable
from .voice import RealtimeVoiceProvider

_DEFAULT_URL = "http://127.0.0.1:8899"
_DEFAULT_VOICE = "af_heart"
_DEFAULT_SPEED = 1.2
_DEFAULT_LANG = "a"  # American English


class KokoroRealtimeVoiceProvider(RealtimeVoiceProvider):
    name = "kokoro"

    def __init__(self, base_url: str = _DEFAULT_URL, voice: str = _DEFAULT_VOICE,
                 speed: float = _DEFAULT_SPEED, lang: str = _DEFAULT_LANG):
        self._url = base_url.rstrip("/")
        self._voice = voice
        self._speed = speed
        self._lang = lang
        self._sessions: dict[str, dict] = {}
        self._lock = threading.Lock()
        # keep-alive connection pool for low-latency HTTP
        self._client = httpx.Client(
            base_url=self._url,
            timeout=30,
            limits=httpx.Limits(
                max_keepalive_connections=2,
                keepalive_expiry=300,
            ),
        )
        # background synthesis pool (1 thread = serial GPU, avoids contention)
        self._pool = ThreadPoolExecutor(max_workers=1, thread_name_prefix="kokoro-tts")

    def available(self) -> bool:
        try:
            r = self._client.get("/health", timeout=3)
            return r.status_code == 200
        except Exception:
            return False

    def create_session(self, call_id, objective="", constraints=None,
                       max_duration_seconds=0, language="", accent="") -> dict:
        sid = f"kokoro_{int(time.time() * 1000)}"
        with self._lock:
            self._sessions[sid] = {
                "session_id": sid,
                "call_id": call_id,
                "objective": objective,
                "constraints": constraints or [],
                "max_duration_seconds": max_duration_seconds,
                "language": language or self._lang,
                "accent": accent or "",
                "transcript": [],
                "created": time.time(),
                "synthesized_chars": 0,
                "synthesized_seconds": 0.0,
            }
        return {
            "session_id": sid,
            "call_id": call_id,
            "state": "AI_SESSION_STARTING",
            "language": language or self._lang,
            "accent": accent or "",
            "provider": "kokoro",
            "gpu": True,
            "simulated": False,
        }

    def send_transcript_chunk(self, session_id, text) -> dict:
        with self._lock:
            sess = self._sessions.get(session_id)
        if not sess:
            raise AiProviderUnavailable(f"no AI session {session_id}")
        # record in transcript
        with self._lock:
            sess["transcript"].append({"ts": time.time(), "text": text})
        # synthesize and play in background (non-blocking)
        future = self._pool.submit(self._synthesize, text, sess)
        return {
            "session_id": session_id,
            "received": True,
            "synthesizing": True,
            "simulated": False,
            "chars": len(text),
        }

    def _synthesize(self, text: str, sess: dict) -> dict:
        """Synthesize text via Kokoro GPU server and play through speakers."""
        try:
            lang = sess.get("language", self._lang)
            # map language codes to Kokoro lang codes
            lang_map = {"hi": "h", "en": "a", "ja": "j", "zh": "z", "fr": "f",
                        "es": "e", "de": "d", "pt": "p"}
            kokoro_lang = lang_map.get(lang, lang or self._lang)

            r = self._client.post("/speak", json={
                "text": text,
                "speed": self._speed,
                "voice": self._voice,
                "lang": kokoro_lang,
            }, timeout=30)
            result = r.json()
            with self._lock:
                sess["synthesized_chars"] += len(text)
                sess["synthesized_seconds"] += result.get("seconds", 0)
            return result
        except Exception as e:
            return {"error": str(e)}

    def get_transcript(self, session_id) -> dict:
        with self._lock:
            sess = self._sessions.get(session_id)
        if not sess:
            raise AiProviderUnavailable(f"no AI session {session_id}")
        return {
            "session_id": session_id,
            "transcript": sess["transcript"],
            "simulated": False,
            "synthesized_chars": sess["synthesized_chars"],
            "synthesized_seconds": sess["synthesized_seconds"],
        }

    def stop(self, session_id) -> dict:
        with self._lock:
            sess = self._sessions.pop(session_id, None)
        if not sess:
            raise AiProviderUnavailable(f"no AI session {session_id}")
        return {
            "session_id": session_id,
            "stopped": True,
            "simulated": False,
            "total_chars": sess["synthesized_chars"],
            "total_seconds": sess["synthesized_seconds"],
        }

    def capabilities(self) -> dict:
        avail = self.available()
        caps = {"name": self.name, "available": avail, "gpu": avail, "simulated": False}
        if avail:
            try:
                r = self._client.get("/health", timeout=3)
                caps.update(r.json())
            except Exception:
                pass
        return caps
