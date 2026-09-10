"""Tool abstraction layer (requirement 36).

Every concrete PDF library is treated as an interchangeable *backend*.
``adapter.py`` exposes one clean interface; ``pymupdf_io`` is preferred,
``pypdf_io`` / ``pdfplumber_io`` are fallbacks. If a backend is missing the
system picks an available alternative automatically, or raises
:class:`~universal_pdf.errors.ToolUnavailableError` which callers translate
into a documented degradation.
"""
from .adapter import (
    backend_available,
    preferred_backend,
    available_backends,
    PDFBackend,
    load_document,
    resolve,
)
