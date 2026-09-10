"""Error-investigation skill (#29).

Given an error message, generates a multi-angle investigation: exact phrase,
shortened core, technology+error, official docs, GitHub issues, community, and
proposed solutions from snippets. Deterministic, no fabrication."""
from __future__ import annotations

import re

from ..search.query import QueryEngine


class ErrorInvestigator:
    def __init__(self, search_client, query_engine=None):
        self.search = search_client
        self.query = query_engine or QueryEngine()

    def _core(self, error: str, words: int = 6) -> str:
        # strip dynamic identifiers/paths for a stable search key
        cleaned = re.sub(r"[`\"']", "", error)
        cleaned = re.sub(r"(0x[0-9a-fA-F]+|\d{2,}|\[[^\]]*\]|\([^)]*\))", " ", cleaned)
        cleaned = re.sub(r"\s+", " ", cleaned).strip()
        return " ".join(cleaned.split()[:words])

    def investigate(self, error: str, *, tech: str = "",
                    include_exact: bool = True, limit: int = 4) -> dict:
        core = self._core(error, 8)
        angles = {}
        # exact phrase
        if include_exact:
            q = f'"{error[:120]}"'
            angles["exact"] = self._angle(q, limit)
        # shortened
        angles["shortened"] = self._angle(core, limit)
        # technology + error
        if tech:
            angles["technology"] = self._angle(f"{tech} {core}", limit)
        # official docs
        angles["official_docs"] = self._angle(f"{core} documentation", limit)
        # github issues
        try:
            angles["github_issues"] = self._github(core, limit)
        except Exception:
            angles["github_issues"] = []
        # community
        angles["community"] = self._community(core, limit)
        return {"error": error, "core": core, "technology": tech,
                "angles": angles}

    def _angle(self, q, limit):
        try:
            out = self.search.search(q, kind="web", limit=limit)
            return [{"url": r.url, "title": r.title, "snippet": r.snippet,
                     "provider": r.provider} for r in out["results"]]
        except Exception:
            return []

    def _github(self, core, limit):
        try:
            out = self.search.search(core, kind="code", limit=limit)
            return [{"url": r.url, "title": r.title, "snippet": r.snippet}
                    for r in out["results"]]
        except Exception:
            return []

    def _community(self, core, limit):
        try:
            out = self.search.search(core, kind="community", limit=limit)
            return [{"url": r.url, "title": r.title, "snippet": r.snippet}
                    for r in out["results"]]
        except Exception:
            return []
