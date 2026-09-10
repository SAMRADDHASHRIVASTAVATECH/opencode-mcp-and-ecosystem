"""Typed errors for the unified operator."""
from __future__ import annotations


class OpError(Exception):
    """Base."""


class NotConfigured(OpError):
    """A connector/provider needs credentials/config that are absent."""


class AuthError(OpError):
    """Authentication expired/invalid."""


class PermissionDenied(OpError):
    """Action blocked by the permission system or provider policy."""


class AmbiguousTarget(OpError):
    """Target identity is ambiguous and requires confirmation."""


class NotSupported(OpError):
    """Capability not supported by the configured provider."""


class ApiError(OpError):
    """An upstream API call failed."""


class Validation(OpError):
    """Tool arguments failed validation."""
