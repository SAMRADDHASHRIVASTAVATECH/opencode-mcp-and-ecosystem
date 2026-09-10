"""Reusable post-operation validation helpers (requirement 35).

These produce :class:`~universal_pdf.result.ValidationCheck` entries that are
attached to Outcomes. They are intentionally cheap and library-agnostic.
"""
from __future__ import annotations

import os

from ..result import ValidationCheck


def openable(path: str, backend="auto") -> ValidationCheck:
    try:
        from ..tools.adapter import load_document
        doc, _ = load_document(path)
        n = getattr(doc, "page_count", None) or getattr(doc, "pages", None)
        if hasattr(doc, "close"):
            doc.close()
        return ValidationCheck("pdf_openable", True, True, True)
    except Exception as exc:  # noqa: BLE001
        return ValidationCheck("pdf_openable", True, False, False, str(exc))


def page_count(path: str, expected: int, backend="auto") -> ValidationCheck:
    from ..tools.adapter import load_document
    try:
        doc, _ = load_document(path)
        actual = _pages(doc)
        if hasattr(doc, "close"):
            doc.close()
        return ValidationCheck("page_count", expected, actual,
                               actual == expected,
                               f"expected {expected}, actual {actual}")
    except Exception as exc:  # noqa: BLE001
        return ValidationCheck("page_count", expected, "ERR", False, str(exc))


def _pages(doc) -> int:
    if hasattr(doc, "page_count"):
        return int(doc.page_count)
    return int(len(doc.pages))


def file_exists(path: str) -> ValidationCheck:
    ok = bool(path) and os.path.exists(path)
    return ValidationCheck("output_exists", True, ok, ok, path or "")


def text_coverage(text: str, expected_nonempty: bool = True) -> ValidationCheck:
    nonempty = bool(text and text.strip())
    return ValidationCheck("text_coverage", expected_nonempty, nonempty,
                           nonempty == expected_nonempty,
                           f"{len(text or '')} chars extracted")
