"""pdf-extract: universal text extraction (requirement 5).

Preserves page and (optionally) positional / structural information instead of
flattening everything to raw text. Digital text layer is used when present;
callers needing OCR for image-only pages should layer pdf-ocr first.
"""
from __future__ import annotations

import json
import os
import re
from typing import Optional

from ..result import Outcome
from ..tools import adapter
from .. import config

PDF = adapter.preferred_backend()


def _open(path, password=None):
    doc, backend = adapter.load_document(path)
    if password and hasattr(doc, "authenticate") and doc.needs_pass:
        doc.authenticate(password)
    return doc, backend


def extract_text(path: str, pages: Optional[list] = None,
                 mode: str = "text", password: str | None = None) -> str:
    """Extract raw text. ``mode``: text | blocks | words | dict | json.

    When ``mode == text`` returns the concatenated plain text (with page
    separators). Other modes return structured layout info via PyMuPDF.
    """
    doc, backend = _open(path, password)
    try:
        if backend == "pymupdf":
            out_parts = []
            total = _pagecount(doc)
            pages = _resolve_pages(total, pages)
            for pno in pages:
                page = doc[pno - 1]
                if mode == "text":
                    out_parts.append(page.get_text("text"))
                elif mode in ("json", "dict"):
                    out_parts.append(json.dumps(page.get_text("dict")))
                else:
                    out_parts.append(page.get_text(mode))
            return ("\n".join(out_parts)
                    if mode == "text" else "\n".join(out_parts))
        # pdfplumber fallback
        import pdfplumber
        with pdfplumber.open(path) as pdf:
            parts = []
            for pno in (pages or list(range(1, _pagecount(doc) + 1))):
                pg = pdf.pages[pno - 1]
                parts.append(pg.extract_text() or "")
            return "\n".join(parts)
    finally:
        if hasattr(doc, "close"):
            doc.close()


def extract_per_page(path: str, password: str | None = None) -> list[str]:
    """Return a list with one text string per page (index 0 == page 1)."""
    doc, backend = _open(path, password)
    try:
        out = []
        for page in doc:
            out.append(page.get_text("text"))
        return out
    finally:
        if hasattr(doc, "close"):
            doc.close()


def iter_page_text(path: str, password: str | None = None, page_count=None):
    """Stream (page_number_1based, text) pairs one at a time.

    This is the memory-safe way to process very large PDFs (requirement 10):
    only one page's text is resident at a time. If page_count is unknown it is
    resolved lazily from the document on first iteration.
    """
    doc, backend = _open(path, password)
    try:
        total = _pagecount(doc) if page_count is None else page_count
        for i, page in enumerate(doc):
            if i >= total:
                break
            yield (i + 1), page.get_text("text")
    finally:
        if hasattr(doc, "close"):
            doc.close()


def extract_blocks_per_page(path: str) -> list[dict]:
    """Return per-page block layout (paragraph-ish units with bbox)."""
    doc, backend = _open(path)
    try:
        out = []
        for i, page in enumerate(doc, 1):
            blocks = []
            for b in page.get_text("blocks"):
                blocks.append({"page": i, "bbox": list(b[:4]),
                               "text": b[4].strip()})
            out.append({"page": i, "blocks": blocks})
        return out
    finally:
        if hasattr(doc, "close"):
            doc.close()


def _resolve_pages(total: int, pages: Optional[list]) -> list:
    if not pages:
        return list(range(1, total + 1))
    resolved = []
    for p in pages:
        if isinstance(p, str):
            resolved.extend(_expand_spec(p, total))
        elif 1 <= int(p) <= total:
            resolved.append(int(p))
    # de-dup, order preserved
    seen, result = set(), []
    for p in resolved:
        if p not in seen:
            seen.add(p)
            result.append(p)
    return result


def _expand_spec(spec: str, total: int) -> list[int]:
    """Parse specs like '1,3-5,8' into page numbers (1-based, inclusive)."""
    result = []
    for part in spec.split(","):
        part = part.strip()
        if not part:
            continue
        if "-" in part:
            a, b = part.split("-", 1)
            start, end = int(a), int(b)
            start = max(1, min(start, total))
            end = min(total, max(1, end))
            result.extend(range(start, end + 1))
        elif part.isdigit():
            n = int(part)
            if 1 <= n <= total:
                result.append(n)
    return result


def detect_text_layer(path: str, sample_pages: int = 5) -> dict:
    """Estimate whether pages carry a usable text layer (for OCR routing)."""
    doc, backend = _open(path)
    try:
        total = _pagecount(doc)
        sample = list(range(1, min(total, sample_pages) + 1))
        chars = 0
        pages_seen = 0
        for pno in sample:
            try:
                t = doc[pno - 1].get_text("text")
                chars += len(t.strip())
                pages_seen += 1
            except Exception:
                pass
        avg = chars / max(1, pages_seen)
        has_layer = avg >= 10
        return {"pages": total, "sampled": pages_seen,
                "avg_chars_per_page": round(avg, 1),
                "has_text_layer": has_layer,
                "needs_ocr": not has_layer}
    finally:
        if hasattr(doc, "close"):
            doc.close()


def _pagecount(doc) -> int:
    if hasattr(doc, "page_count"):
        return int(doc.page_count)
    return len(doc.pages)
