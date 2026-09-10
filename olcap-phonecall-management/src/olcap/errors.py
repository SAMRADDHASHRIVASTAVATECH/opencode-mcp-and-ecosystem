"""Structured error codes for the OLCAP control plane.

Every operation must return a structured error. Codes match the spec section 25.
Errors raised here carry a stable `code` (a short uppercase token) that the MCP
layer serialises alongside the message, never hiding capability limitations.
"""
from __future__ import annotations


class OlcapError(Exception):
    code = "OLCAP_ERROR"

    def __init__(self, message: str, code: str | None = None, **ctx):
        super().__init__(message)
        self.message = message
        if code:
            self.code = code
        self.ctx = ctx

    def to_dict(self):
        return {"code": self.code, "message": self.message, **self.ctx}


class CapabilityUnsupported(OlcapError):
    code = "CAPABILITY_UNSUPPORTED"


class UnsupportedOnThisDevice(OlcapError):
    code = "UNSUPPORTED_ON_THIS_DEVICE"


class CallAudioUnavailable(OlcapError):
    code = "CALL_AUDIO_UNAVAILABLE"


class AndroidPermissionDenied(OlcapError):
    code = "ANDROID_PERMISSION_DENIED"


class SimUnavailable(OlcapError):
    code = "SIM_UNAVAILABLE"


class CallNotActive(OlcapError):
    code = "CALL_NOT_ACTIVE"


class AiProviderUnavailable(OlcapError):
    code = "AI_PROVIDER_UNAVAILABLE"


class McpUnauthorized(OlcapError):
    code = "MCP_UNAUTHORIZED"


class DestinationNotAllowed(OlcapError):
    code = "DESTINATION_NOT_ALLOWED"


class NetworkUnavailable(OlcapError):
    code = "NETWORK_UNAVAILABLE"


class CallFailed(OlcapError):
    code = "CALL_FAILED"


class InvalidCallState(OlcapError):
    code = "INVALID_CALL_STATE"


class EmergencyStopActive(OlcapError):
    code = "EMERGENCY_STOP_ACTIVE"


class PolicyConflict(OlcapError):
    code = "POLICY_CONFLICT"
