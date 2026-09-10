"""Typed exceptions for the Android Control system."""
from __future__ import annotations


class AndroidControlError(Exception):
    """Base class."""


class NoDevicesError(AndroidControlError):
    """No devices matched the requested selection."""


class AmbiguousDeviceError(AndroidControlError):
    """Natural-language device selection matched more than one device."""


class DeviceOfflineError(AndroidControlError):
    """The targeted device is offline / unreachable."""


class UnknownDeviceError(AndroidControlError):
    """No such device id / serial is registered."""


class ToolNotFoundError(AndroidControlError):
    """A required host-side tool could not be found or installed."""


class CommandFailedError(AndroidControlError):
    """A low-level command returned a non-success exit or expected-error."""


class TimeoutError(AndroidControlError):
    """A command exceeded its allowed time."""


class RequiresAuthorizationError(AndroidControlError):
    """A destructive operation requires explicit authorization."""


class UnsupportedOperationError(AndroidControlError):
    """The operation is not available on this device / Android version."""


class InjectionDeniedError(AndroidControlError):
    """A command string failed a safety check and was refused."""
