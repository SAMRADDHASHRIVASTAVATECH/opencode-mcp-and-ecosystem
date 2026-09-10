"""Typed errors surfaced to MCP tools as structured results."""
from __future__ import annotations


class OlcapError(Exception):
    """Base error with a stable code + structured context."""
    code = "error"

    def __init__(self, message: str, *, recoverable: bool = False,
                 recovery_attempted: bool = False,
                 recovery_action: str | None = None, **ctx):
        super().__init__(message)
        self.message = message
        self.recoverable = recoverable
        self.recovery_attempted = recovery_attempted
        self.recovery_action = recovery_action
        self.ctx = ctx

    def to_dict(self) -> dict:
        d = {"success": False,
             "error": {"code": self.code, "message": self.message,
                       "recoverable": self.recoverable,
                       "recovery_attempted": self.recovery_attempted,
                       "recovery_action": self.recovery_action}}
        d["error"].update(self.ctx)
        return d


class HardwareDetectionError(OlcapError):
    code = "HARDWARE_DETECTION"


class CUDAUnavailable(OlcapError):
    code = "CUDA_UNAVAILABLE"


class CUDAOutOfMemory(OlcapError):
    code = "CUDA_OUT_OF_MEMORY"


class ModelNotFound(OlcapError):
    code = "MODEL_NOT_FOUND"


class ModelCorrupt(OlcapError):
    code = "MODEL_CORRUPT"


class ModelDownloadFailed(OlcapError):
    code = "MODEL_DOWNLOAD_FAILED"


class MissingDependency(OlcapError):
    code = "MISSING_DEPENDENCY"


class RuntimeNotRunning(OlcapError):
    code = "RUNTIME_NOT_RUNNING"


class PortInUse(OlcapError):
    code = "PORT_IN_USE"


class DiskFull(OlcapError):
    code = "DISK_FULL"


class InsufficientRAM(OlcapError):
    code = "INSUFFICIENT_RAM"


class InvalidInputImage(OlcapError):
    code = "INVALID_INPUT_IMAGE"


class InvalidMask(OlcapError):
    code = "INVALID_MASK"


class UnsupportedFormat(OlcapError):
    code = "UNSUPPORTED_FORMAT"


class InvalidArguments(OlcapError):
    code = "INVALID_ARGUMENTS"


class JobNotFound(OlcapError):
    code = "JOB_NOT_FOUND"


class NotAuthorized(OlcapError):
    code = "NOT_AUTHORIZED"


class BackendError(OlcapError):
    code = "BACKEND_ERROR"


class ComfyUIError(OlcapError):
    code = "COMFYUI_ERROR"


class NoBackendAvailable(OlcapError):
    code = "NO_BACKEND_AVAILABLE"


class ValidationFailure(OlcapError):
    code = "VALIDATION_FAILURE"
