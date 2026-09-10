from __future__ import annotations

from typing import Any


class WinError(Exception):
    def __init__(self, code: str, message: str, details: dict[str, Any] | None = None) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.details = details or {}

    def to_dict(self) -> dict[str, Any]:
        return {"code": self.code, "message": self.message, "details": self.details}


class UnsupportedError(WinError):
    def __init__(self, message: str, details: dict[str, Any] | None = None) -> None:
        super().__init__("UNSUPPORTED", message, details)


class PolicyError(WinError):
    def __init__(self, message: str, details: dict[str, Any] | None = None) -> None:
        super().__init__("SECURITY", message, details)


class ValidationError(WinError):
    def __init__(self, message: str, details: dict[str, Any] | None = None) -> None:
        super().__init__("VALIDATION", message, details)


class TimeoutErr(WinError):
    def __init__(self, message: str, details: dict[str, Any] | None = None) -> None:
        super().__init__("TIMEOUT", message, details)


class BackendError(WinError):
    def __init__(self, message: str, details: dict[str, Any] | None = None) -> None:
        super().__init__("EXTERNAL", message, details)
