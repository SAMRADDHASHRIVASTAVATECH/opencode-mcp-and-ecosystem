"""General web search adapters: Bing, DuckDuckGo, SearXNG, Brave.

These are *best-effort, legitimate* providers. None attempts to bypass bot
protection: DuckDuckGo's bot-check page (HTTP 202) is treated as a provider
failure so the router falls back rather than circumventing it. Brave requires
an operator API key. SearXNG requires an operator-run instance.
"""
from __future__ import annotations

import urllib.parse
from typing import Optional

from .. import network, security
from ..errors import ProviderError
from ..models import SearchResult
from .base import Adapter, ProviderCapabilities


class BingAdapter(Adapter):
    capabilities = frozenset({ProviderCapabilities.WEB})
    name = "bing"

    def configured(self) -> bool:
        return self.settings.bing_enabled

    def search(self, query: str, *, limit: int = 10,
               opts: Optional[dict] = None) -> list[SearchResult]:
        from bs4 import BeautifulSoup
        url = "https://www.bing.com/search?" + urllib.parse.urlencode({"q": query})
        try:
            resp = network.fetch(url)
        except ProviderError:
            raise
        except Exception as exc:  # network issues
            raise ProviderError(f"bing network error: {exc}")
        if resp.status_code != 200:
            raise ProviderError(f"bing HTTP {resp.status_code}")
        soup = BeautifulSoup(resp.text, "lxml")
        results = []
        for i, li in enumerate(soup.select("li.b_algo"), 1):
            a = li.select_one("h2 a")
            if not a:
                continue
            href = self._decode(a.get("href") or "")
            title = a.get_text(" ", strip=True)
            snippet = _snippet(li)
            results.append(SearchResult(title=title, url=href, snippet=snippet,
                                        provider=self.name, rank=i, kind="web"))
            if len(results) >= limit:
                break
        if not results:
            raise ProviderError("bing returned no parseable results")
        return results

    @staticmethod
    def _decode(href: str) -> str:
        import base64
        if "ck/a" not in href:
            return href
        q = urllib.parse.parse_qs(urllib.parse.urlparse(href).query)
        u = q.get("u", [""])[0]
        if u.startswith("a1"):
            try:
                return base64.urlsafe_b64decode(u[2:] + "==").decode()
            except Exception:
                return href
        return href


class DuckDuckGoAdapter(Adapter):
    capabilities = frozenset({ProviderCapabilities.WEB})
    name = "duckduckgo"

    def configured(self) -> bool:
        return self.settings.duckduckgo_enabled

    def search(self, query: str, *, limit: int = 10,
               opts: Optional[dict] = None) -> list[SearchResult]:
        from bs4 import BeautifulSoup
        headers = {"User-Agent": self.settings.user_agent}
        # DuckDuckGo bot check returns 202 "anomaly". We do NOT circumvent it.
        url = "https://lite.duckduckgo.com/lite/?"
        try:
            resp = network.client().post(url, data={"q": query}, headers=headers,
                                         follow_redirects=True,
                                         timeout=self.settings.default_timeout)
        except Exception as exc:
            raise ProviderError(f"duckduckgo network error: {exc}")
        if resp.status_code in (202, 403, 429):
            raise ProviderError(
                f"duckduckgo blocked request (HTTP {resp.status_code}); "
                "not bypassing bot protection")
        if resp.status_code != 200:
            raise ProviderError(f"duckduckgo HTTP {resp.status_code}")
        soup = BeautifulSoup(resp.text, "lxml")
        results = []
        # lite results are table rows with class 'result'
        for i, tr in enumerate(soup.select("tr.result"), 1):
            a = tr.select_one("a")
            if not a or not a.get("href"):
                continue
            sn = tr.select_one("td.result-snippet")
            results.append(SearchResult(title=a.get_text(" ", strip=True) or a["href"],
                                        url=a["href"],
                                        snippet=sn.get_text(" ", strip=True)
                                        if sn else "",
                                        provider=self.name, rank=i, kind="web"))
            if len(results) >= limit:
                break
        if not results:
            raise ProviderError("duckduckgo returned no parseable results")
        return results


class SearxAdapter(Adapter):
    capabilities = frozenset({ProviderCapabilities.WEB})
    name = "searxng"

    def __init__(self, settings):
        super().__init__(settings)
        self.base = (settings.searxng_base_url or "").rstrip("/")

    def configured(self) -> bool:
        return bool(self.base)

    def search(self, query: str, *, limit: int = 10,
               opts: Optional[dict] = None) -> list[SearchResult]:
        import json as _json
        url = f"{self.base}/search?{urllib.parse.urlencode({'q': query, 'format': 'json'})}"
        try:
            resp = network.fetch(url)
        except Exception as exc:
            raise ProviderError(f"searxng error: {exc}")
        if resp.status_code != 200:
            raise ProviderError(f"searxng HTTP {resp.status_code}")
        try:
            data = resp.json()
        except Exception:
            raise ProviderError("searxng did not return JSON (format=json "
                                "likely disabled on instance)")
        results = []
        for i, r in enumerate(data.get("results", []), 1):
            results.append(SearchResult(title=r.get("title", ""),
                                        url=r.get("url", ""),
                                        snippet=r.get("content", ""),
                                        provider=self.name, rank=i, kind="web"))
        return results[:limit]


class BraveAdapter(Adapter):
    capabilities = frozenset({ProviderCapabilities.WEB})
    name = "brave"

    def __init__(self, settings):
        super().__init__(settings)
        self.key = settings.brave_api_key

    def configured(self) -> bool:
        return bool(self.key)

    def search(self, query: str, *, limit: int = 10,
               opts: Optional[dict] = None) -> list[SearchResult]:
        url = "https://api.search.brave.com/res/v1/web/search?" + \
            urllib.parse.urlencode({"q": query, "count": limit})
        resp = network.fetch(url, headers={"X-Subscription-Token": self.key})
        if resp.status_code != 200:
            raise ProviderError(f"brave HTTP {resp.status_code}")
        data = resp.json()
        results = []
        for i, r in enumerate(data.get("web", {}).get("results", []), 1):
            results.append(SearchResult(title=r.get("title", ""),
                                        url=r.get("url", ""),
                                        snippet=r.get("description", ""),
                                        provider=self.name, rank=i, kind="web"))
        return results


def _snippet(li) -> str:
    for sel in ("p", ".b_caption p", ".b_lineclamp2", ".b_lineclamp3"):
        el = li.select_one(sel)
        if el and el.get_text(" ", strip=True):
            return el.get_text(" ", strip=True)[:400]
    return ""
