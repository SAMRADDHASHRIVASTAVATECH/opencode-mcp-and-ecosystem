"""Structured errors for the self-improvement engine."""
from __future__ import annotations


class EngineError(Exception):
    code = "ENGINE_ERROR"

    def __init__(self, message="", code=None, **ctx):
        super().__init__(message)
        self.message = message
        if code:
            self.code = code
        self.ctx = ctx

    def to_dict(self):
        return {"ok": False, "code": self.code, "error": self.message, **self.ctx}


class ProtectedLesson(EngineError):
    code = "PROTECTED_LESSON"


class NotFound(EngineError):
    code = "NOT_FOUND"


class ValidationError(EngineError):
    code = "VALIDATION_ERROR"
