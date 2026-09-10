"""Deterministic offline provider used by tests and as a guaranteed fallback
ONLY when explicitly requested (never for real research). It fabricates nothing
from the network; its fixtures are fixed and documented."""
from __future__ import annotations

from typing import Optional

from ..models import SearchResult
from .base import Adapter, ProviderCapabilities

# curated sample corpus (keywords -> entries). Not real-time; used to test the
# routing/search/evidence logic deterministically.
_CORPUS = [
    {"kw": "pdf parser", "title": "PyMuPDF", "kind": "web",
     "url": "https://pymupdf.io/",
     "snippet": "PyMuPDF is a high performance Python library for data "
                "extraction, analysis, conversion and manipulation of PDF files."},
    {"kw": "pdf", "title": "PyMuPDF GitHub", "kind": "code",
     "url": "https://github.com/pymupdf/PyMuPDF",
     "snippet": "PyMuPDF source repository - rendering, OCR, layout and tables."},
    {"kw": "pdf", "title": "pdfplumber", "kind": "web",
     "url": "https://github.com/jsvine/pdfplumber",
     "snippet": "pdfplumber for parsing PDFs and extracting tables and text."},
    {"kw": "pdf parser best", "title": "Comparing PDF libraries", "kind": "web",
     "url": "https://example.org/comparing-pdf-libraries",
     "snippet": "An overview comparing PyMuPDF, pdfplumber, pypdf, pdfminer."},
    {"kw": "local llm", "title": "Local LLM tools overview", "kind": "community",
     "url": "https://example.org/local-llm",
     "snippet": "Community discussion on running local language models."},
    {"kw": "evidence claim contradiction", "kind": "paper",
     "title": "A survey of claim verification", "url": "https://arxiv.org/abs/1234.5678",
     "snippet": "Survey of automated claim verification methods."},
]


class MockProvider(Adapter):
    capabilities = frozenset({ProviderCapabilities.WEB, ProviderCapabilities.CODE,
                              ProviderCapabilities.PAPER,
                              ProviderCapabilities.NEWS,
                              ProviderCapabilities.COMMUNITY})
    name = "mock"

    def __init__(self, settings=None):
        super().__init__(settings)

    def configured(self) -> bool:
        return True

    def search(self, query: str, *, limit: int = 10,
               opts: Optional[dict] = None) -> list[SearchResult]:
        q = query.lower()
        want_kind = (opts or {}).get("kind")
        results = []
        for entry in _CORPUS:
            if any(k in q for k in entry["kw"].split()):
                if want_kind and entry["kind"] != want_kind:
                    continue
                results.append(SearchResult(
                    title=entry["title"], url=entry["url"],
                    snippet=entry["snippet"], provider=self.name,
                    kind=entry["kind"], rank=len(results) + 1))
        return results[:limit]
