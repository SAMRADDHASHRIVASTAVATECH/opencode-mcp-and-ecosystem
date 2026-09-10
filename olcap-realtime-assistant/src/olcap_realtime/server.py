"""Unified MCP server: olcap-realtime-assistant-mcp (spec sections 18, 19, 21).

Namespaced tools (assistant.*, audio.*, screen.*, transcript.*, practice.*,
meeting.*, session.*, model.*). No unrestricted shell access. Every handler wraps
the Assistant, applies auth, and returns structured JSON (errors carry codes).
"""
from __future__ import annotations

import functools
import json
from typing import Annotated, Any, Optional

from pydantic import Field

from .mcp_compat import MCPServer

from . import __version__
from .assistant import Assistant
from .errors import AssistantError

DESCRIPTION = (
    "OLCAP realtime multimodal assistant - a single realtime AI assistant with "
    "two modes (INTERVIEW/PRACTICE and ALWAYS-ON WORKSPACE). Real audio/screen/"
    "STT/reasoning/TTS; capabilities that are unavailable on the host return "
    "UNAVAILABLE with the reason. No fake capabilities."
)

Str = Optional[str]
Int = Optional[int]
Bool = Optional[bool]


class OlcapRealtimeServer(MCPServer):
    def __init__(self, assistant: Assistant):
        self.a = assistant
        super().__init__(name="olcap-realtime-assistant-mcp",
                         instructions=DESCRIPTION, version=__version__)
        self._register_all()

    def tool(self, *a, **k):
        orig = super().tool(*a, **k)

        def _g(fn):
            @functools.wraps(fn)
            def w(*args, **kw):
                try:
                    r = fn(*args, **kw)
                except AssistantError as e:
                    return json.dumps(e.to_dict())
                except Exception as e:  # noqa: BLE001
                    return json.dumps({"ok": False, "code": "ASSISTANT_ERROR",
                                       "error": str(e)})
                return r if isinstance(r, str) else json.dumps(
                    {"ok": True, **r}, default=str)
            return orig(w)
        return _g

    def _reg(self, name, desc):
        return self.tool(name=name, description=desc)

    def _register_all(self):
        a = self.a

        # ============ assistant ============ #
        @self._reg("assistant.get_status", "Overall assistant status + mode + indicators.")
        def assistant_get_status():
            st = a.get_mode()
            return {"mode": st["mode"], "paused": st["paused"],
                    "status": st["status"],
                    "session_id": a._active_session or None,
                    "emergency_stop": a.security.emergency_stop}

        @self._reg("assistant.mode.get", "Current operating mode.")
        def assistant_mode_get():
            return a.get_mode()

        @self._reg("assistant.mode.set", "Switch mode: off|interview|workspace.")
        def assistant_mode_set(mode: str):
            return a.set_mode(mode)

        @self._reg("assistant.mode.interview", "Enter INTERVIEW/PRACTICE mode.")
        def assistant_mode_interview():
            return a.set_mode("interview")

        @self._reg("assistant.mode.workspace", "Enter ALWAYS-ON WORKSPACE mode.")
        def assistant_mode_workspace():
            return a.set_mode("workspace")

        @self._reg("assistant.mode.pause", "Pause the assistant.")
        def assistant_mode_pause():
            return a.pause()

        @self._reg("assistant.mode.resume", "Resume the assistant.")
        def assistant_mode_resume():
            return a.resume()

        @self._reg("assistant.start", "Start the assistant (default workspace).")
        def assistant_start(mode: Str = ""):
            return a.start(mode or "")

        @self._reg("assistant.stop", "Stop the assistant (ends active session).")
        def assistant_stop():
            return a.stop()

        @self._reg("assistant.pause", "Pause the assistant.", )
        def assistant_pause():
            return a.pause()

        @self._reg("assistant.resume", "Resume the assistant.")
        def assistant_resume():
            return a.resume()

        @self._reg("assistant.health", "Overall health report.")
        def assistant_health():
            return a.health()

        @self._reg("assistant.diag", "End-to-end pipeline diagnostic.")
        def assistant_diag():
            return a.diag()

        @self._reg("assistant.analyze", "Analyse a prompt with current context.")
        def assistant_analyze(prompt: str, session_id: Str = ""):
            return a.analyze(prompt, session_id or "")

        @self._reg("assistant.analyze_screen", "Capture + analyse the screen.")
        def assistant_analyze_screen():
            return a.analyze_screen()

        @self._reg("assistant.analyze_voice", "Analyse the latest voice transcript.")
        def assistant_analyze_voice(text: str, session_id: Str = ""):
            return a.analyze("Analyse this spoken input and respond helpfully.\n\n"
                             + text, session_id or "")

        @self._reg("assistant.analyze_context", "Analyse the current session context.")
        def assistant_analyze_context(session_id: Str = ""):
            sid = session_id or a._active_session
            if not sid:
                return {"context": None, "error": "no active session"}
            return a.context.rolling_context(sid)

        @self._reg("assistant.emergency_stop", "EMERGENCY STOP - halt everything.")
        def assistant_emergency_stop():
            return a.emergency_stop()

        @self._reg("assistant.release_emergency_stop", "Release the emergency stop.")
        def assistant_release_emergency_stop():
            return a.release_emergency_stop()

        # ============ audio ============ #
        @self._reg("audio.list_devices", "List available audio input devices.")
        def audio_list_devices():
            return {"devices": a.audio.list_devices()}

        @self._reg("audio.get_status", "Audio engine status.")
        def audio_get_status():
            return a.audio.status()

        @self._reg("audio.select_device", "Select an audio input device by id.")
        def audio_select_device(device_id: Int):
            # ensure a mic source exists
            if not a.audio.source:
                a.audio.default_mic()
            return a.audio.source.select_device(device_id)

        @self._reg("audio.start", "Start microphone capture.")
        def audio_start():
            a.security.require_active()
            if not a.audio.source:
                a.audio.default_mic()
            return a.audio.start()

        @self._reg("audio.stop", "Stop microphone capture.")
        def audio_stop():
            return a.audio.stop()

        @self._reg("audio.pause", "Pause microphone capture.")
        def audio_pause():
            return a.audio.pause()

        @self._reg("audio.resume", "Resume microphone capture.")
        def audio_resume():
            return a.audio.resume()

        @self._reg("audio.test", "Test the audio input.")
        def audio_test():
            return a.audio.test()

        @self._reg("audio.health", "Audio health.")
        def audio_health():
            return a.audio.health()

        # ============ screen ============ #
        @self._reg("screen.get_status", "Screen monitoring status.")
        def screen_get_status():
            return a.screen.status()

        @self._reg("screen.start", "Start screen monitoring (must be enabled in "
                   "config + workspace mode).")
        def screen_start():
            a.security.require_active()
            a.modes.set_sensor("screen", True, mode_required="workspace")
            return a.screen.start()

        @self._reg("screen.stop", "Stop screen monitoring.")
        def screen_stop():
            return a.screen.stop()

        @self._reg("screen.pause", "Pause screen monitoring.")
        def screen_pause():
            return a.screen.pause()

        @self._reg("screen.resume", "Resume screen monitoring.")
        def screen_resume():
            return a.screen.resume()

        @self._reg("screen.get_current", "Capture current screen (if available).")
        def screen_get_current():
            try:
                a.screen.capture_frame()
                return {"ok": True, "note": "frame captured"}
            except Exception as e:
                return {"ok": False, "code": "SCREEN_UNAVAILABLE", "error": str(e)}

        @self._reg("screen.get_active_window", "Get the active window title/app.")
        def screen_get_active_window():
            return a.screen.get_active_window()

        @self._reg("screen.get_changes", "Report screen change stats.")
        def screen_get_changes():
            return a.screen.get_changes()

        @self._reg("screen.capture_region", "Capture a screen region.")
        def screen_capture_region(region: Any = None):
            try:
                a.screen.capture_frame(region=region)
                return {"ok": True, "region": region}
            except Exception as e:
                return {"ok": False, "code": "SCREEN_UNAVAILABLE", "error": str(e)}

        @self._reg("screen.health", "Screen health.")
        def screen_health():
            return a.screen.health()

        # ============ transcript ============ #
        @self._reg("transcript.get_live", "Live (active session) transcript.")
        def transcript_get_live(session_id: Str = ""):
            sid = session_id or a._active_session
            if not sid:
                return {"transcript": []}
            try:
                return {"transcript": list(a.context.require(sid).transcript_window)}
            except Exception:
                return {"transcript": []}

        @self._reg("transcript.get_recent", "Recent transcript lines.")
        def transcript_get_recent(session_id: Str = ""):
            return transcript_get_live(session_id)

        @self._reg("transcript.get_history", "Full stored transcript for a session.")
        def transcript_get_history(session_id: str):
            sess = a.sessions.get(session_id)
            if not sess:
                return {"transcript": [], "error": "no such session"}
            return {"transcript": sess.get("transcript", [])}

        @self._reg("transcript.search", "Search transcripts for a term.")
        def transcript_search(term: str, session_id: Str = ""):
            sid = session_id or a._active_session
            hits = []
            if sid:
                sess = a.sessions.get(sid)
                for t in (sess or {}).get("transcript", []):
                    if term.lower() in (t.get("text") or "").lower():
                        hits.append(t)
            return {"matches": hits, "term": term}

        # ============ practice ============ #
        @self._reg("practice.analyze_question", "Classify + structure an interview "
                   "question.")
        def practice_analyze_question(question: str):
            return a.practice.analyze_question(question)

        @self._reg("practice.generate_answer", "Generate a suggested answer "
                   "(needs reasoning model).")
        def practice_generate_answer(question: str, session_id: Str = ""):
            r = a.practice.generate_answer(question, _ctx_or_none(a, session_id))
            return {"ok": r.get("suggested_answer") is not None, **r}

        @self._reg("practice.generate_hint", "Generate a hint for a question.")
        def practice_generate_hint(question: str):
            return a.practice.generate_hint(question)

        @self._reg("practice.evaluate_answer", "Score/evaluate a practice answer.")
        def practice_evaluate_answer(question: str, answer: str):
            return a.practice.evaluate_answer(question, answer)

        @self._reg("practice.analyze_code", "Analyse a coding problem into its "
                   "structure.")
        def practice_analyze_code(problem: str):
            return a.practice.analyze_code(problem)

        @self._reg("practice.generate_solution", "Generate a full coding solution "
                   "(needs reasoning model).")
        def practice_generate_solution(problem: str, code: Str = ""):
            return a.practice.generate_solution(problem, code or None)

        @self._reg("practice.explain_solution", "Explain code (needs reasoning "
                   "model).")
        def practice_explain_solution(code: str):
            return a.practice.explain_solution(code)

        # ============ meeting ============ #
        @self._reg("meeting.summarize", "Summarize a meeting transcript.")
        def meeting_summarize(transcript: str):
            return a.meeting.summarize(transcript)

        @self._reg("meeting.extract_actions", "Extract action items from a "
                   "transcript.")
        def meeting_extract_actions(transcript: str):
            return a.meeting.extract_actions(transcript)

        @self._reg("meeting.extract_decisions", "Extract decisions from a "
                   "transcript.")
        def meeting_extract_decisions(transcript: str):
            return a.meeting.extract_decisions(transcript)

        @self._reg("meeting.extract_questions", "Extract questions from a "
                   "transcript.")
        def meeting_extract_questions(transcript: str):
            return a.meeting.extract_questions(transcript)

        # ============ session ============ #
        @self._reg("session.create", "Create a new session.")
        def session_create(mode: str = "workspace"):
            s = a.sessions.create(mode)
            a._active_session = s["session_id"]
            return s

        @self._reg("session.get", "Get a session by id.")
        def session_get(session_id: str):
            s = a.sessions.get(session_id)
            return s or {"error": "no such session", "session_id": session_id}

        @self._reg("session.pause", "Pause a session.")
        def session_pause(session_id: str):
            return a.sessions.pause(session_id)

        @self._reg("session.resume", "Resume a session.")
        def session_resume(session_id: str):
            return a.sessions.resume(session_id)

        @self._reg("session.end", "End a session with optional summary.")
        def session_end(session_id: str, summary: Str = ""):
            return a.sessions.end(session_id, summary or "")

        @self._reg("session.summarize", "Attach a summary to a session.")
        def session_summarize(session_id: str, summary: str):
            return {"summary": a.sessions.summarize(session_id, summary)}

        @self._reg("session.delete", "Delete a session.")
        def session_delete(session_id: str):
            return a.sessions.delete(session_id)

        @self._reg("session.export", "Export a session (record + events + context).")
        def session_export(session_id: str):
            return a.sessions.export(session_id)

        @self._reg("session.list", "List sessions.")
        def session_list():
            return {"sessions": a.sessions.list()}

        # ============ model ============ #
        @self._reg("model.list", "List models available on each provider.")
        def model_list():
            return {"providers": a.reasoning.list_models()}

        @self._reg("model.get_status", "Active reasoning provider status.")
        def model_get_status():
            return a.reasoning.health()

        @self._reg("model.set_provider", "Set active reasoning provider.")
        def model_set_provider(provider: str):
            return a.reasoning.set_provider(provider)

        @self._reg("model.get_usage", "Reasoning provider availability.")
        def model_get_usage():
            return a.reasoning.health()


def _ctx_or_none(a, session_id):
    sid = session_id or a._active_session
    if not sid:
        return None
    try:
        return a.context.rolling_context(sid)
    except Exception:
        return None
