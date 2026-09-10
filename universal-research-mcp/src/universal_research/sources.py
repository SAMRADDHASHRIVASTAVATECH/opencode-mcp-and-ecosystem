"""Source analysis skill (#23): classify source type, authority, freshness,
relevance, independence."""
from __future__ import annotations

import re
from urllib.parse import urlparse

_SUFFIX_AUTHORITY = [
    (".gov.in", "official_government"), (".gov.uk", "official_government"),
    (".gov", "official_government"), (".ac.in", "academic_institution"),
    (".ac.uk", "academic_institution"), (".edu", "academic_institution"),
    ("arxiv.org", "academic_preprint"), ("readthedocs.io", "official_docs"),
]
_HOST_AUTHORITY = {
    "ieee.org": "publisher", "acm.org": "publisher",
    "springer.com": "publisher", "nature.com": "publisher",
    "science.org": "publisher", "wikipedia.org": "encyclopedia",
    "github.com": "primary_source_code",
    "stackoverflow.com": "community",
    "reddit.com": "community",
}
_SYNDICATED_HOSTS = {"feeds", "feedburner", "flipboard.com", "msn.com",
                     "news.google.com"}


def _authority(host: str) -> tuple[str, int]:
    for suf, label in _SUFFIX_AUTHORITY:
        if host.endswith(suf):
            return label, _authority_level(label)
    for h, label in _HOST_AUTHORITY.items():
        if host == h or host.endswith("." + h):
            return label, _authority_level(label)
    return "web", _authority_level("web")


def _authority_level(authority) -> int:
    levels = {"official_government": 5, "official_docs": 4, "publisher": 5,
              "academic_institution": 4, "academic_preprint": 3,
              "encyclopedia": 3, "primary_source_code": 4,
              "community": 2, "web": 1, "unknown": 0}
    return levels.get(authority, 1)


def analyze_source(url: str, *, title: str = "", headings: list = None,
                   date: str = "", snippet: str = "", provider: str = "") -> dict:
    host = (urlparse(url).netloc or "").lower().removeprefix("www.")
    authority, alevel = _authority(host)
    source_type = _type_of(host, url)
    freshness = _freshness(date)
    independence = _independence(host)
    is_primary = source_type in ("official_government", "academic",
                                 "primary_code", "official")
    return {
        "url": url, "domain": host, "source_type": source_type,
        "primary_source": is_primary, "secondary_source": not is_primary,
        "authority": authority, "authority_level": alevel,
        "freshness": freshness, "independence": independence,
        "relevance": round(0.7 if (title or snippet or headings) else 0.5, 2),
    }


def _type_of(host, url) -> str:
    if host in ("github.com", "gitlab.com", "bitbucket.org") or \
            host.endswith(".github.io"):
        return "primary_code"
    if host.endswith((".gov.in", ".gov", ".gov.uk", ".mil")):
        return "official_government"
    if host.endswith((".edu", ".ac.in", ".ac.uk")) or host == "arxiv.org":
        return "academic"
    if any(n in host for n in ("news",)) or host in (
            "reuters.com", "apnews.com", "bbc.co.uk", "cnn.com"):
        return "news"
    if host.endswith(("reddit.com", "stackoverflow.com", "stackexchange.com")):
        return "community"
    low = url.lower()
    if low.endswith(".pdf"):
        return "document"
    return "web"


def _freshness(date) -> str:
    m = re.search(r"(20\d{2})", date or "")
    if not m:
        return ""
    y = int(m.group(1))
    if y >= 2025:
        return "current"
    if y >= 2023:
        return "recent"
    return "dated"


def _independence(host) -> str:
    if host == "github.com" or host.endswith(".github.io"):
        return "primary"
    if any(s in host for s in _SYNDICATED_HOSTS):
        return "syndicated"
    return "independent"


def is_syndicated(host: str) -> bool:
    return _independence(host) == "syndicated"
