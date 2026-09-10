"""OLCAP realtime assistant core - the single coordinating object behind the MCP.

Owns: config, mode manager, session manager, context engine, event bus, security,
audio/screen/stt/reasoning/tts engines, practice/workspace/meeting engines.
Honest: hardware/model capabilities report their true availability; nothing is
faked. Emergency stop halts everything.
"""
from __future__ import annotations

import threading
import time

from .config import AppConfig
from .context import ContextEngine
from .engines.reasoning import ModelRouter
from .engines.screen import ScreenEngine
from .engines.stt import STTEngine
from .engines.tts import TTSEngine
from .events import EventBus
from .modes import ModeManager
from .practice import InterviewPracticeEngine, MeetingEngine, WorkspaceEngine
from .security import SecurityManager
from .session import SessionManager
from .store import Store
from .engines.audio import AudioEngine, MicrophoneSource


class Assistant:
    def __init__(self, config: AppConfig | None = None):
        self.cfg = config or AppConfig()
        # dirs
        from pathlib import Path
        for d in (self.cfg.state_dir, self.cfg.log_dir, self.cfg.screenshot_dir):
            Path(d).mkdir(parents=True, exist_ok=True)
        self.store = Store(self.cfg.db_path)
        self.bus = EventBus()
        self.security = SecurityManager(self.cfg, self.store)
        self.context = ContextEngine()
        self.modes = ModeManager(self.cfg, self.bus)
        self.sessions = SessionManager(self.cfg, self.store, self.context, self.bus)
        self.audio = AudioEngine(self.cfg)
        self.screen = ScreenEngine(self.cfg)
        self.stt = STTEngine(self.cfg)
        self.tts = TTSEngine(self.cfg)
        self.reasoning = ModelRouter(self.cfg, openclaw=self._openclaw())
        self.practice = InterviewPracticeEngine(self._reasoning_or_none())
        self.workspace = WorkspaceEngine(self._reasoning_or_none())
        self.meeting = MeetingEngine(self._reasoning_or_none())
        self._lock = threading.Lock()
        self._active_session: str = ""
        self._interrupt = threading.Event()
        self._stopped = False
        self._hook_events()

    def _openclaw(self):
        # OpenClaw integration is additive; if an existing openclaw client object
        # is injected later it is used here. We never rebuild OpenClaw's stack.
        return None

    def _reasoning_or_none(self):
        # Engines use a thin adapter to the router. When no model is reachable it
        # returns None (not an exception) so engines fall back to deterministic /
        # honest "no model" behaviour instead of crashing.
        router = self.reasoning

        class _R:
            def generate(self, messages, **kw):
                try:
                    return router.generate(messages, **kw)
                except Exception:
                    return None
            @property
            def available(self):
                try:
                    return router.get(router.active).available()
                except Exception:
                    return False
        return _R()

    def _hook_events(self):
        self.bus.subscribe(lambda e: self._on_event(e))

    def _on_event(self, ev):
        # persist important events to the active session store
        sid = self._active_session
        if sid and ev.type in ("transcript.final", "transcript.partial",
                               "question.detected", "mode.changed"):
            self.store.append_event(sid, ev.dict())

    # ---- lifecycle / health ---- #
    def emergency_stop(self) -> dict:
        self.security.engage_emergency_stop()
        self._interrupt.set()
        # halt capture + generation
        try:
            self.audio.stop()
        except Exception:
            pass
        try:
            self.screen.stop()
        except Exception:
            pass
        try:
            self.tts.cancel()
        except Exception:
            pass
        try:
            self.reasoning.get(self.reasoning.active).cancel()
        except Exception:
            pass
        self.modes.set_mode("off")
        self._stopped = True
        self.bus.publish("emergency_stop", {})
        return {"emergency_stop": True}

    def release_emergency_stop(self):
        self.security.release_emergency_stop()
        self._stopped = False
        return {"emergency_stop": False}

    def health(self) -> dict:
        return {
            "assistant": {"ok": True, "emergency_stop": self.security.emergency_stop},
            "audio": self.audio.health(),
            "screen": self.screen.health(),
            "stt": self.stt.health(),
            "reasoning": self.reasoning.health(),
            "tts": self.tts.health(),
            "mode": self.modes.get(),
        }

    def diag(self) -> dict:
        """End-to-end pipeline diagnostic (spec 34). Reports each stage honestly."""
        steps = {
            "mode": {"ok": self.modes.mode in ("workspace", "interview"),
                     "detail": self.modes.get()},
            "microphone": self._diag_mic(),
            "screen": self._diag_screen(),
            "stt": self.stt.health(),
            "reasoning": self.reasoning.health(),
            "tts": self.tts.health(),
        }
        return {"steps": steps,
                "all_ok": all(s.get("available", False) or s.get("ok", False)
                              for s in steps.values()) if steps else False}

    def _diag_mic(self):
        try:
            devs = self.audio.list_devices()
            return {"available": len(devs) > 0, "devices": len(devs)}
        except Exception as e:
            return {"available": False, "reason": str(e)}

    def _diag_screen(self):
        return {"available": self.screen.available(),
                "reason": (None if self.screen.available() else
                           self.screen._reason_unavailable())}

    # ---- mode/session orchestration ---- #
    def set_mode(self, mode: str, token: str = "") -> dict:
        self.security.authorize(token)
        self.security.require_active()
        prev = self.modes.get()
        if mode != "off" and not self._active_session:
            self._active_session = self.sessions.create(mode)["session_id"]
        self.modes.set_mode(mode)
        return {"mode": self.modes.get(), "session_id": self._active_session or None,
                "previous": prev}

    def get_mode(self):
        return self.modes.get()

    def start(self, mode: str = "", token: str = ""):
        self.security.authorize(token)
        self.security.require_active()
        m = mode or self.modes.mode
        if m == "off":
            m = "workspace"
        return self.set_mode(m)

    def stop(self, token: str = ""):
        self.security.authorize(token)
        if self._active_session:
            self.sessions.end(self._active_session)
            self._active_session = ""
        self.audio.stop()
        self.screen.stop()
        return self.set_mode("off")

    def pause(self, token: str = ""):
        self.security.authorize(token)
        if self._active_session:
            self.sessions.pause(self._active_session)
        return self.modes.pause()

    def resume(self, token: str = ""):
        self.security.authorize(token)
        if self._active_session:
            self.sessions.resume(self._active_session)
        return self.modes.resume()

    # ---- interrupt management ---- #
    def interruption(self, text: str = ""):
        """New speech arrives mid-generation -> cancel stale reasoning."""
        self._interrupt.set()
        try:
            self.reasoning.get(self.reasoning.active).cancel()
        except Exception:
            pass
        self.bus.publish("interruption", {"text": text})
        self._interrupt.clear()
        return {"interrupted": True}

    # ---- helpers to feed transcripts into context/session ---- #
    def feed_partial(self, text: str):
        if self._active_session:
            self.sessions.add_transcript(self._active_session, text, final=False)
        else:
            self.context.add_utterance("_live", text, final=False)

    def feed_final(self, text: str):
        if self._active_session:
            self.sessions.add_transcript(self._active_session, text, final=True)
        else:
            self.context.add_utterance("_live", text, final=True)
        return {"transcript": text}

    def feed_screen(self, summary: str = "", app: str = "", window: str = ""):
        sid = self._active_session or "_live"
        self.context.add_screen(sid, app=app, window=window, summary=summary,
                                changed=True)
        return {"screen": summary or "", "app": app or "", "window": window or ""}

    # ---- analysis entrypoints ---- #
    def analyze(self, prompt: str, session_id: str = ""):
        sid = session_id or self._active_session
        ctx = {}
        if sid:
            try:
                ctx = self.context.rolling_context(sid)
            except Exception:
                ctx = {}
        if self._reasoning_available():
            return self.reasoning.generate(
                [{"role": "system", "content": "You are the OLCAP realtime assistant."},
                 ({"role": "system", "content": "Context:\n" + str(ctx)} if ctx else None),
                 {"role": "user", "content": prompt}])
        return {"ok": False, "code": "MODEL_UNAVAILABLE",
                "error": "analysis requires a reachable reasoning model",
                "context": ctx}

    def analyze_screen(self):
        # capture + OCR/summary path; honest about availability
        if not self.screen.available():
            return {"ok": False, "code": "SCREEN_UNAVAILABLE",
                    "error": self.screen._reason_unavailable()}
        try:
            self.screen.capture_frame()
            return {"ok": True, "note": "frame captured; vision summary requires a "
                    "vision model (cloud_vision only if enabled)"}
        except Exception as e:
            return {"ok": False, "code": "SCREEN_UNAVAILABLE", "error": str(e)}

    def _reasoning_available(self) -> bool:
        try:
            return self.reasoning.get(self.reasoning.active).available()
        except Exception:
            return False
