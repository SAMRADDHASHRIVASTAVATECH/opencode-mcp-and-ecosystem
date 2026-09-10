"""Domain-specific legitimate API adapters: GitHub, arXiv, Crossref,
Google News (RSS), Hacker News (Algolia). All are public/open APIs; none
requires bypassing access controls."""
from __future__ import annotations

import urllib.parse
import xml.etree.ElementTree as ET
from datetime import datetime
from typing import Optional

from .. import network
from ..errors import ProviderError
from ..models import SearchResult
from .base import Adapter, ProviderCapabilities


def _guard(resp, provider):
    if resp.status_code != 200:
        raise ProviderError(f"{provider} HTTP {resp.status_code}")
    return resp


class GithubAdapter(Adapter):
    capabilities = frozenset({ProviderCapabilities.CODE,
                              ProviderCapabilities.COMMUNITY})
    name = "github"

    def __init__(self, settings):
        super().__init__(settings)
        self.token = __import__("os").environ.get("UR_GITHUB_TOKEN", "")

    def configured(self) -> bool:
        return True  # repo/issues work without token

    def search(self, query: str, *, limit: int = 10,
               opts: Optional[dict] = None) -> list[SearchResult]:
        opts = opts or {}
        scope = opts.get("scope", "repositories")
        hd = {}
        if self.token:
            hd["Authorization"] = f"token {self.token}"
        base = "https://api.github.com"
        if scope == "repositories":
            url = f"{base}/search/repositories?{urllib.parse.urlencode({'q': query, 'per_page': limit})}"
        elif scope in ("code",):
            if not self.token:
                raise ProviderError("GitHub code search requires UR_GITHUB_TOKEN")
            url = f"{base}/search/code?{urllib.parse.urlencode({'q': query, 'per_page': limit})}"
        elif scope in ("issues", "discussions"):
            url = f"{base}/search/issues?{urllib.parse.urlencode({'q': query, 'per_page': limit})}"
        elif scope == "commits":
            url = f"{base}/search/commits?{urllib.parse.urlencode({'q': query, 'per_page': limit})}"
        elif scope == "repository":
            # query is owner/repo
            url = f"{base}/repos/{query}"
            try:
                resp = network.fetch(url, headers=hd)
                _guard(resp, "github")
                d = resp.json()
                return [SearchResult(title=d.get("full_name", ""),
                                     url=d.get("html_url", ""),
                                     snippet=d.get("description", ""),
                                     provider=self.name, rank=1, kind="code",
                                     date=d.get("updated_at"),
                                     extra={"stars": d.get("stargazers_count"),
                                            "license": (d.get("license") or {}).get("spdx_id"),
                                            "language": d.get("language"),
                                            "topics": d.get("topics", []),
                                            "open_issues": d.get("open_issues_count")})]
            except ProviderError:
                raise
            except Exception as exc:
                raise ProviderError(f"github repository error: {exc}")
        else:
            url = f"{base}/search/repositories?{urllib.parse.urlencode({'q': query, 'per_page': limit})}"
        try:
            resp = network.fetch(url, headers=hd)
            _guard(resp, "github")
            data = resp.json()
        except ProviderError:
            raise
        except Exception as exc:
            raise ProviderError(f"github error: {exc}")
        results = []
        for i, item in enumerate(data.get("items", []), 1):
            if scope == "repositories":
                results.append(SearchResult(
                    title=item.get("full_name", ""), url=item.get("html_url", ""),
                    snippet=item.get("description", ""), provider=self.name,
                    rank=i, kind="code", date=item.get("updated_at"),
                    extra={"stars": item.get("stargazers_count"),
                           "language": item.get("language"),
                           "license": (item.get("license") or {}).get("spdx_id"),
                           "topics": item.get("topics", []),
                           "fork": item.get("fork")}))
            elif scope in ("issues", "discussions"):
                results.append(SearchResult(
                    title=item.get("title", ""), url=item.get("html_url", ""),
                    snippet=(item.get("body") or "")[:300], provider=self.name,
                    rank=i, kind="community", date=item.get("created_at"),
                    extra={"state": item.get("state"), "repo": (item.get("repository_url") or "")}))
            else:
                results.append(SearchResult(
                    title=item.get("name", ""), url=item.get("html_url", ""),
                    snippet=item.get("path", ""), provider=self.name, rank=i,
                    kind="code",
                    extra={"repo": (item.get("repository") or {}).get("full_name")}))
        return results

    def releases(self, repo: str, limit: int = 5) -> list[SearchResult]:
        url = f"https://api.github.com/repos/{repo}/releases?per_page={limit}"
        try:
            resp = network.fetch(url)
            _guard(resp, "github")
            data = resp.json()
        except Exception as exc:
            raise ProviderError(f"github releases error: {exc}")
        out = []
        for i, r in enumerate(data, 1):
            out.append(SearchResult(title=r.get("name") or r.get("tag_name", ""),
                                    url=r.get("html_url", ""),
                                    snippet=(r.get("body") or "")[:300],
                                    provider=self.name, rank=i, kind="community",
                                    date=r.get("published_at")))
        return out


class ArxivAdapter(Adapter):
    capabilities = frozenset({ProviderCapabilities.PAPER})
    name = "arxiv"

    def search(self, query: str, *, limit: int = 10,
               opts: Optional[dict] = None) -> list[SearchResult]:
        url = ("http://export.arxiv.org/api/query?" +
               urllib.parse.urlencode({"search_query": f"all:{query}",
                                       "start": 0, "max_results": limit,
                                       "sortBy": "relevance"}))
        try:
            resp = network.fetch(url)
        except Exception as exc:
            raise ProviderError(f"arxiv error: {exc}")
        try:
            root = ET.fromstring(resp.content)
        except Exception:
            raise ProviderError("arxiv returned non-XML")
        ns = {"a": "http://www.w3.org/2005/Atom"}
        results = []
        for i, e in enumerate(root.findall("a:entry", ns), 1):
            title = " ".join((e.findtext("a:title", default="", namespaces=ns)
                              or "").split())
            summary = " ".join((e.findtext("a:summary", default="",
                                           namespaces=ns) or "").split())
            link = e.find("a:id", ns)
            published = e.findtext("a:published", default="", namespaces=ns)
            results.append(SearchResult(title=title,
                                        url=(link.text if link is not None else ""),
                                        snippet=summary[:500], provider=self.name,
                                        rank=i, kind="paper", date=published))
        return results


class CrossrefAdapter(Adapter):
    capabilities = frozenset({ProviderCapabilities.PAPER})
    name = "crossref"

    def search(self, query: str, *, limit: int = 10,
               opts: Optional[dict] = None) -> list[SearchResult]:
        sel = "DOI,title,author,container-title,published,URL,issued"
        url = ("https://api.crossref.org/works?" +
               urllib.parse.urlencode({"query": query, "rows": limit,
                                       "select": sel}))
        try:
            resp = network.fetch(url)
            _guard(resp, "crossref")
            data = resp.json()
        except ProviderError:
            raise
        except Exception as exc:
            raise ProviderError(f"crossref error: {exc}")
        out = []
        for i, w in enumerate(data.get("message", {}).get("items", []), 1):
            title = (w.get("title") or [""])[0]
            authors = ", ".join(
                f"{a.get('given','')} {a.get('family','')}".strip()
                for a in w.get("author", [])[:3])
            year = ""
            issued = w.get("issued", {}).get("date-parts")
            if issued and issued[0]:
                year = issued[0][0]
            out.append(SearchResult(title=title,
                                    url=w.get("URL", "") or
                                    f"https://doi.org/{w.get('DOI','')}",
                                    snippet=f"{authors} ({year})",
                                    provider=self.name, rank=i, kind="paper",
                                    date=str(year),
                                    extra={"doi": w.get("DOI"),
                                           "journal": (w.get("container-title") or [""])[0]}))
        return out


class GoogleNewsAdapter(Adapter):
    capabilities = frozenset({ProviderCapabilities.NEWS})
    name = "googlenews"

    def search(self, query: str, *, limit: int = 10,
               opts: Optional[dict] = None) -> list[SearchResult]:
        opts = opts or {}
        lang = opts.get("language", "en")
        region = opts.get("region", "US")
        url = "https://news.google.com/rss/search?"
        params = {"q": query, "hl": lang, "gl": region, "ceid": f"{region}:{lang}"}
        try:
            resp = network.fetch(url + urllib.parse.urlencode(params))
            root = ET.fromstring(resp.content)
        except Exception as exc:
            raise ProviderError(f"googlenews error: {exc}")
        out = []
        for i, it in enumerate(root.findall(".//item"), 1):
            title = it.findtext("title", default="")
            link = it.findtext("link", default="")
            pub = it.findtext("pubDate", default="")
            src = it.findtext("source", default="")
            out.append(SearchResult(title=title, url=link, snippet=f"[{src}]",
                                    provider=self.name, rank=i, kind="news",
                                    date=pub,
                                    extra={"source": src, "retrieval_date":
                                           datetime.utcnow().isoformat() + "Z"}))
        return out[:limit]


class HackerNewsAdapter(Adapter):
    capabilities = frozenset({ProviderCapabilities.COMMUNITY})
    name = "hackernews"

    def search(self, query: str, *, limit: int = 10,
               opts: Optional[dict] = None) -> list[SearchResult]:
        params = {"query": query, "hitsPerPage": limit}
        if (opts or {}).get("points_min"):
            params["numericFilters"] = f"points>{opts['points_min']}"
        url = "https://hn.algolia.com/api/v1/search?" + urllib.parse.urlencode(params)
        try:
            resp = network.fetch(url)
            _guard(resp, "hackernews")
            data = resp.json()
        except ProviderError:
            raise
        except Exception as exc:
            raise ProviderError(f"hackernews error: {exc}")
        out = []
        for i, h in enumerate(data.get("hits", []), 1):
            url = h.get("url") or f"https://news.ycombinator.com/item?id={h.get('objectID')}"
            out.append(SearchResult(title=h.get("title", ""), url=url,
                                    snippet=(h.get("story_text") or "")[:300],
                                    provider=self.name, rank=i, kind="community",
                                    date=h.get("created_at"),
                                    extra={"points": h.get("points"),
                                           "comments": h.get("num_comments"),
                                           "author": h.get("author")}))
        return out
