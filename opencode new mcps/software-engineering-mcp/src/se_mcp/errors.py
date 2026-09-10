from __future__ import annotations

from typing import Any


class SEError(Exception):
    def __init__(self, code: str, message: str, details: dict[str, Any] | None = None) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.details = details or {}

    def to_dict(self) -> dict[str, Any]:
        return {"code": self.code, "message": self.message, "details": self.details}


class ValidationError(SEError):
    def __init__(self, message: str, details: dict[str, Any] | None = None) -> None:
        super().__init__("VALIDATION", message, details)


class NotFoundError(SEError):
    def __init__(self, message: str, details: dict[str, Any] | None = None) -> None:
        super().__init__("NOT_FOUND", message, details)


class DependencyMissing(SEError):
    def __init__(self, message: str, details: dict[str, Any] | None = None) -> None:
        super().__init__("DEPENDENCY_MISSING", message, details)


class PolicyError(SEError):
    def __init__(self, message: str, details: dict[str, Any] | None = None) -> None:
        super().__init__("SECURITY", message, details)


class ExternalError(SEError):
    def __init__(self, message: str, details: dict[str, Any] | None = None) -> None:
        super().__init__("EXTERNAL", message, details)
