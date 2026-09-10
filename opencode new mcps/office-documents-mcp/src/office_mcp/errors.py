"""Typed errors for the Office MCP."""

from __future__ import annotations

from typing import Any


class OfficeError(Exception):
    def __init__(
        self,
        code: str,
        message: str,
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.details = details or {}

    def to_dict(self) -> dict[str, Any]:
        return {"code": self.code, "message": self.message, "details": self.details}


class ValidationError(OfficeError):
    def __init__(self, message: str, details: dict[str, Any] | None = None) -> None:
        super().__init__("VALIDATION", message, details)


class NotFoundError(OfficeError):
    def __init__(self, message: str, details: dict[str, Any] | None = None) -> None:
        super().__init__("NOT_FOUND", message, details)


class PermissionDenied(OfficeError):
    def __init__(self, message: str, details: dict[str, Any] | None = None) -> None:
        super().__init__("PERMISSION", message, details)


class UnsupportedError(OfficeError):
    def __init__(self, message: str, details: dict[str, Any] | None = None) -> None:
        super().__init__("UNSUPPORTED", message, details)


class DependencyMissing(OfficeError):
    def __init__(self, message: str, details: dict[str, Any] | None = None) -> None:
        super().__init__("DEPENDENCY_MISSING", message, details)


class MalformedError(OfficeError):
    def __init__(self, message: str, details: dict[str, Any] | None = None) -> None:
        super().__init__("MALFORMED", message, details)


class TimeoutError_(OfficeError):
    def __init__(self, message: str, details: dict[str, Any] | None = None) -> None:
        super().__init__("TIMEOUT", message, details)


class SecurityError(OfficeError):
    def __init__(self, message: str, details: dict[str, Any] | None = None) -> None:
        super().__init__("SECURITY", message, details)
