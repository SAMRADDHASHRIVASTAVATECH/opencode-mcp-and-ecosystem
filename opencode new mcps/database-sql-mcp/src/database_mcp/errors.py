from __future__ import annotations

from typing import Any


class DBError(Exception):
    def __init__(self, code: str, message: str, details: dict[str, Any] | None = None) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.details = details or {}

    def to_dict(self) -> dict[str, Any]:
        return {"code": self.code, "message": self.message, "details": self.details}


class ValidationError(DBError):
    def __init__(self, message: str, details: dict[str, Any] | None = None) -> None:
        super().__init__("VALIDATION", message, details)


class NotFoundError(DBError):
    def __init__(self, message: str, details: dict[str, Any] | None = None) -> None:
        super().__init__("NOT_FOUND", message, details)


class PermissionDenied(DBError):
    def __init__(self, message: str, details: dict[str, Any] | None = None) -> None:
        super().__init__("PERMISSION", message, details)


class UnsupportedError(DBError):
    def __init__(self, message: str, details: dict[str, Any] | None = None) -> None:
        super().__init__("UNSUPPORTED", message, details)


class DependencyMissing(DBError):
    def __init__(self, message: str, details: dict[str, Any] | None = None) -> None:
        super().__init__("DEPENDENCY_MISSING", message, details)


class PolicyError(DBError):
    def __init__(self, message: str, details: dict[str, Any] | None = None) -> None:
        super().__init__("SECURITY", message, details)


class TimeoutErr(DBError):
    def __init__(self, message: str, details: dict[str, Any] | None = None) -> None:
        super().__init__("TIMEOUT", message, details)
