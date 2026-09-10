"""ToolRouter (#5, #35): decides which providers/tools/search-methods to use
for a research objective. Provider auto-routing with fallback. Exposes a
dynamic selection so an agent does not need provider specifics."""
from __future__ import annotations

from typing import Optional


class ToolRouter:
    def __init__(self, providers, settings=None):
        self.providers = providers
        self.settings = settings
        self.mock_only = False

    # kind -> capability + preferred provider order
    _PREFERENCE = {
        "web": ["brave", "searxng", "bing", "duckduckgo"],
        "code": ["github"],
        "paper": ["arxiv", "crossref"],
        "news": ["googlenews"],
        "community": ["hackernews", "github"],
        "gov": ["bing", "duckduckgo"],   # with site: operator via query engine
        "doc": ["bing", "duckduckgo"],
    }

    def choose_providers(self, kind: str = "web", *, require: Optional[list] = None,
                         use_mock: bool = False) -> list[str]:
        """Pick an ordered provider list for a kind, honouring configured status.

        When ``require`` is set, ensure those providers lead; when use_mock,
        restrict to mock (offline determinism)."""
        if self.mock_only or use_mock:
            return ["mock"] if self.providers.has("mock") else []
        pref = list(self._PREFERENCE.get(kind, self._PREFERENCE["web"]))
        if require:
            pref = [r for r in require if r in pref] + \
                   [p for p in pref if p not in (require or [])]
        # only configured providers remain, keeping configured mock last
        out = [n for n in pref if self._configured(n)]
        if not out:
            out = [n for n in self.providers.names() if self._configured(n)]
        return out

    def best_provider(self, kind: str) -> Optional[str]:
        chosen = self.choose_providers(kind)
        return chosen[0] if chosen else None

    def route(self, *, query: str = "", kind: str = "web", target: str = "") -> dict:
        """Return a routing decision given objective hints."""
        providers = self.choose_providers(kind)
        return {"kind": kind, "target": target, "query": query,
                "providers": providers, "strategy": self._strategy(target)}

    def _strategy(self, target: str) -> str:
        if target == "code":
            return "github-first + repo crawl"
        if target == "documents":
            return "filetype-based search then fetch/parse docs"
        if target == "government":
            return "site-restricted search on official domains"
        if target == "news":
            return "news provider + freshness weighting"
        if target == "academic":
            return "arxiv/crossref then paper pages"
        return "web-first with source verification"

    def _configured(self, name: str) -> bool:
        try:
            p = self.providers.get(name)
            return p is not None and p.configured
        except Exception:
            return False

    def for_claim_verification(self) -> dict:
        """Strategy for verification: web + high-authority + academic."""
        return {"providers": self.choose_providers("web") +
                [p for p in self.choose_providers("paper") if p not in
                 self.choose_providers("web")],
                "search_style": "verification", "require_independent": True}
