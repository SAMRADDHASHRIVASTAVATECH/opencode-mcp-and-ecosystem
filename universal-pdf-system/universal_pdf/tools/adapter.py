"""Tool abstraction interface + availability probing.

Preferred tool: PyMuPDF (``pymupdf``) — richest single library.
Fallbacks:      pypdf (pure-python structural ops, crypto),
                pdfplumber (high-fidelity text/table layout extraction),
                reportlab (creation).
"""
from __future__ import annotations

import importlib
import logging
from typing import Optional

from ..errors import ToolUnavailableError

log = logging.getLogger("universal_pdf.tools")

_BACKENDS: dict[str, bool] = {}


def _probe(name: str, module: str) -> bool:
    try:
        importlib.import_module(module)
        _BACKENDS[name] = True
        return True
    except Exception:
        _BACKENDS[name] = False
        return False


def backend_available(name: str) -> bool:
    """Return whether a named backend is importable (cached)."""
    if name not in _BACKENDS:
        _probe(name, {"pymupdf": "pymupdf",
                      "pypdf": "pypdf",
                      "pdfplumber": "pdfplumber",
                      "reportlab": "reportlab",
                      "pillow": "PIL"}.get(name, name))
    return _BACKENDS[name]


def available_backends() -> list[str]:
    for n in ["pymupdf", "pypdf", "pdfplumber", "reportlab", "pillow"]:
        backend_available(n)
    return [k for k, v in _BACKENDS.items() if v]


def preferred_backend() -> str:
    """Highest-priority available backend for general operations."""
    for cand in ["pymupdf", "pypdf", "pdfplumber"]:
        if backend_available(cand):
            return cand
    return "none"


# --- lightweight marker + helpers -------------------------------------------
class PDFBackend:  # pragma: no cover - namespace only
    """Namespace marker for backend implementations."""


def resolve(preferred: Optional[str] = None, needed: Optional[str] = None) -> str:
    """Choose a backend: ``preferred`` if available, else a capable fallback.

    Raises ToolUnavailableError when nothing usable exists.
    """
    order = []
    if preferred and preferred != "auto":
        order.append(preferred)
    if needed == "layout":
        order += ["pdfplumber", "pymupdf", "pypdf"]
    elif needed == "crypto":
        order += ["pypdf", "pymupdf"]
    elif needed == "structure":
        order += ["pymupdf", "pypdf"]
    else:
        order += ["pymupdf", "pypdf", "pdfplumber"]
    # de-dup preserving order
    seen, clean = set(), []
    for b in order:
        if b not in seen and b in available_backends():
            seen.add(b)
            clean.append(b)
    if not clean:
        raise ToolUnavailableError(
            "No PDF backend is installed. Install 'pymupdf' (and optionally "
            "'pypdf', 'pdfplumber', 'reportlab').")
    return clean[0]


def load_document(path: str):
    """Load a document with the preferred backend, raising a friendly error.

    Returns a backend-specific open document object and its backend name.
    """
    backend = preferred_backend()
    if backend == "pymupdf":
        import pymupdf
        try:
            doc = pymupdf.open(path)
        except Exception as exc:  # includes encrypted / broken
            msg = str(exc)
            if "password" in msg.lower() or "encrypted" in msg.lower():
                from ..errors import EncryptedDocumentError
                raise EncryptedDocumentError(msg) from exc
            from ..errors import DocumentOpenError
            raise DocumentOpenError(f"Could not open {path}: {exc}") from exc
        return doc, backend
    if backend == "pypdf":
        from pypdf import PdfReader
        reader = PdfReader(path)
        return reader, backend
    raise ToolUnavailableError("No supported PDF backend available.")
