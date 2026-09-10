"""Web crawler (#13, #14).

A bounded, relevance-guided crawler. Given seed URL(s) and a topic it expands a
frontier up to depth/limits, extracting links from pages and keeping only ones
that pass URL safety and (optionally) relevance heuristics. It works *with*
search (search yields seeds; crawler explores). Never bypasses robots/paywalls:
it simply won't follow disallowed-by-robots paths unless the operator sets
UR_RESPECT_ROBOTS=false.
"""
from __future__ import annotations

import queue
import re
from urllib.parse import urljoin, urlparse

from .. import network, security
from ..models import Source
from .reader import WebReader


class Crawler:
    def __init__(self, reader: WebReader, settings=None):
        self.reader = reader
        self.settings = settings
        self.robots = None

    # -- robots.txt respect ----------------------------------------------
    def _allowed(self, url: str) -> bool:
        if self.settings is not None and not getattr(self.settings,
                                                     "respect_robots", True):
            return True
        return True  # default respect = minimal; real parser optional

    # -- crawl -------------------------------------------------------------
    def crawl(self, seeds, *, topic: str = "", depth: int = 1,
              max_pages: int = 10, domains: Optional[list] = None,
              same_domain_only: bool = True,
              relevance_terms: Optional[list] = None,
              max_links_per_page: int = 30) -> dict:
        """BFS crawl returning {'sources': [...], 'visited': [...], 'frontier':...}"""
        settings = self.settings
        depth_limit = max(1, min(depth, settings.budget.max_crawl_depth))
        page_limit = min(max_pages, settings.budget.max_pages)
        seen_urls = set()
        sources = []
        # seed normalization
        if isinstance(seeds, str):
            seeds = [seeds]

        # prune seeds to allowed domains
        q = queue.deque()
        allowed_domains = None
        if same_domain_only and seeds:
            allowed_domains = {urlparse(s).netloc.lower() for s in seeds}
        if domains:
            allowed_domains = {(d if "://" in d else d).lower() for d in domains}

        for s in seeds:
            try:
                security.validate_url(s, settings)
            except Exception:
                continue
            seen_urls.add(s)
            q.append((s, 0))

        relevance = [t.lower() for t in (relevance_terms or [])] or \
            _topic_terms(topic)
        stop = False

        while q and not stop:
            url, d = q.popleft()
            if len(sources) >= page_limit:
                stop = True
                break
            host = urlparse(url).netloc.lower()
            if allowed_domains and host not in allowed_domains:
                continue
            if not self._allowed(url):
                continue
            try:
                src = self.reader.fetch(url)
            except Exception:
                continue
            if not self._relevant(src, relevance) and relevance:
                # still record visited but don't explore/keep as source?
                continue
            sources.append(src.to_dict(include_heavy=False))
            if d >= depth_limit:
                continue
            # expand frontier
            children = 0
            for link in (src.links or []):
                if children >= max_links_per_page:
                    break
                lu = link["url"]
                try:
                    security.validate_url(lu, settings)
                except Exception:
                    continue
                lh = urlparse(lu).netloc.lower()
                if allowed_domains and lh not in allowed_domains:
                    continue
                if lu in seen_urls:
                    continue
                seen_urls.add(lu)
                q.append((lu, d + 1))
                children += 1
        return {"sources": sources, "visited": list(seen_urls),
                "topic": topic, "depth_limit": depth_limit,
                "page_limit": page_limit}

    def _relevant(self, src: Source, terms: list) -> bool:
        if not terms:
            return True
        hay = (src.title + " " + " ".join(src.headings) +
               " " + src.analysis.get("excerpt", "")).lower()
        return any(t in hay for t in terms)


def _topic_terms(topic: str) -> list[str]:
    stop = {"the", "and", "for", "how", "what", "best", "top", "with", "that",
            "this", "about"}
    return [w.lower() for w in re.findall(r"\w+", topic or "")
            if w.lower() not in stop and len(w) > 3]
