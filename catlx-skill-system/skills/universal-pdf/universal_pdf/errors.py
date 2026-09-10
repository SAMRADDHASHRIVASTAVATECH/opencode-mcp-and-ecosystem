"""Central exception hierarchy for the universal PDF system.

A small, predictable exception tree lets every skill and the orchestrator
report *limitations* versus *failures* distinctly, so graceful degradation
never masquerades as success.
"""


class PDFError(Exception):
    """Base class for all system errors."""


class ToolUnavailableError(PDFError):
    """A required underlying library / binary is not installed.

    Skills catching this error should attempt a documented fallback and, if
    none exists, report a clear limitation (never a fake success).
    """


class ResourceError(PDFError):
    """Operation cannot proceed due to resource constraints (RAM, disk...)."""


class ValidationError(PDFError):
    """Post-operation validation produced unacceptable results."""


class DocumentOpenError(PDFError):
    """Input could not be opened / parsed as a valid PDF."""


class EncryptedDocumentError(DocumentOpenError):
    """Document is password protected and cannot be opened without a key."""


class NotSupportedError(PDFError):
    """The requested operation is not technically supported for this input."""
