"""Structured errors for the OLCAP realtime assistant.

Every component returns structured outcomes. Capability-absence is reported as
`UNAVAILABLE` with a concrete reason (spec section 45) rather than faked success.
"""
from __future__ import annotations


class AssistantError(Exception):
    code = "ASSISTANT_ERROR"

    def __init__(self, message: str = "", code: str | None = None, **ctx):
        super().__init__(message or self.code)
        self.message = message or self.code
        if code:
            self.code = code
        self.ctx = ctx

    def to_dict(self):
        return {"ok": False, "code": self.code, "error": self.message, **self.ctx}


class Unavailable(AssistantError):
    """A capability is not available on this system, with the actual reason."""
    code = "UNAVAILABLE"


class NotConfigured(AssistantError):
    code = "NOT_CONFIGURED"


class ModeInactive(AssistantError):
    code = "MODE_INACTIVE"


class EmergencyStopActive(AssistantError):
    code = "EMERGENCY_STOP_ACTIVE"


class AuthRequired(AssistantError):
    code = "UNAUTHORIZED"


class ModelUnavailable(AssistantError):
    code = "MODEL_UNAVAILABLE"


class SttUnavailable(AssistantError):
    code = "STT_UNAVAILABLE"


class TtsUnavailable(AssistantError):
    code = "TTS_UNAVAILABLE"


class ScreenUnavailable(AssistantError):
    code = "SCREEN_UNAVAILABLE"


class AudioUnavailable(AssistantError):
    code = "AUDIO_UNAVAILABLE"


class SessionNotFound(AssistantError):
    code = "SESSION_NOT_FOUND"
