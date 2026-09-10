"""Search result ranking + deduplication (#8, #49)."""
from __future__ import annotations

import re
from urllib.parse import urlparse

from ..models import SearchResult

_SYNDICATORS = {"feeds", "feedburner", "ap.org", "reuters.com", "bloomberg.com",
                "yahoo.com", "msn.com", "google.com", "bing.com", "flipboard.com"}


def _norm_url(url: str) -> str:
    p = urlparse(url)
    host = (p.netloc or "").lower()
    if host.startswith("www."):
        host = host[4:]
    # drop common tracking
    return f"{host}{p.path}".rstrip("/")


def deduplicate(results: list[SearchResult]) -> list[SearchResult]:
    seen = {}
    out = []
    for r in results:
        key = _norm_url(r.url)
        if key in seen:
            # keep highest-ranked / more snippet
            continue
        seen[key] = r
        out.append(r)
    return out


def rank_results(results: list[SearchResult], query: str) -> list[SearchResult]:
    """Score by keyword overlap (title>snippet), provider best-effort penalty,
    and original rank."""
    terms = [t.lower() for t in re.findall(r"\w+", query)
             if len(t) > 2 and t.lower() not in
             {"the", "and", "for", "how", "what", "best", "top", "with",
              "that", "this", "from"}]
    penalize = {"duckduckgo", "bing", "mock"}  # best-effort/hybrid sources

    def score(r: SearchResult) -> float:
        s = 0.0
        title = r.title.lower()
        snip = r.snippet.lower()
        for t in terms:
            if t in title:
                s += 3.0
            elif t in snip:
                s += 1.5
        # freshness bonus if date present
        if r.date:
            s += 0.3
        if r.provider in penalize:
            s -= 0.2
        # prefer earlier ranks slightly
        s -= (r.rank or 0) * 0.05
        return s

    scored = sorted(results, key=lambda r: (-score(r), r.rank or 0))
    for i, r in enumerate(scored, 1):
        r.rank = i
    return scored


def group_independence(results: list[SearchResult]) -> dict:
    """Heuristic source-independence grouping (#49): group by root domain and
    flag likely syndicated/duplicate provenance."""
    groups = {}
    for r in results:
        host = (urlparse(r.url).netloc or "").lower().removeprefix("www.")
        root = ".".join(host.split(".")[-2:]) if host.count(".") >= 1 else host
        groups.setdefault(root, []).append(r.url)
    return groups


def is_syndicated(host: str) -> bool:
    host = (host or "").lower().removeprefix("www.")
    return any(s in host for s in _SYNDICATORS) or host in _SYNDICATORS
