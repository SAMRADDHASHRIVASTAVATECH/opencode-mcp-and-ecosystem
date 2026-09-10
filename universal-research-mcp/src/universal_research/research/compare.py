"""Comparison skills (#28, #70). compare_entities / compare_sources.

Deterministic research over dimensions (features, architecture, performance,
maintenance, ecosystem, docs, license, limitations) yielding per-entity
evidence rows plus a compact table.
"""
from __future__ import annotations

import re
from urllib.parse import urlparse


class ComparisonEngine:
    DIMENSIONS = ["features", "architecture", "performance", "maintenance",
                  "ecosystem", "documentation", "license", "limitations"]

    def __init__(self, search, sources_analysis=None):
        self.search = search
        self.source_analysis = sources_analysis

    def compare_entities(self, entities, *, dimensions=None,
                         target="auto", limit=4) -> dict:
        dims = dimensions or self.DIMENSIONS
        rows = {}
        seen = {}
        for entity in entities:
            e = entity if isinstance(entity, str) else entity.get("name")
            key = entity if isinstance(entity, str) else entity.get("url", entity.get("name"))
            # search discovery for this entity
            out = self.search.search(f"{e}", kind="web", limit=limit)
            res = out["results"]
            rows[e] = {"entity": e, "dimensions": {}, "sources": []}
            for r in res[:6]:
                ana = {}
                if self.source_analysis:
                    ana = self.source_analysis(r.url, title=r.title, snippet=r.snippet)
                rows[e]["sources"].append({"url": r.url, "title": r.title,
                                           "snippet": r.snippet,
                                           "analysis": ana})
            # per-dimension targeted searches fill 'dimensions'
            for dim in dims:
                q = f"{e} {dim}"
                dout = self.search.search(q, kind="web", limit=2)
                evidence = [{"url": x.url,
                             "note": (x.snippet or "")[:180]}
                            for x in dout["results"][:2]]
                rows[e]["dimensions"][dim] = evidence
        return {"entities": list(rows), "dimensions": dims,
                "rows": rows}

    def compare_sources(self, urls, *, provider_fallback="web") -> dict:
        """Compare a set of source URLs by analysis only (no re-fetch heavy)."""
        out = []
        for u in urls:
            ana = {}
            if self.source_analysis:
                ana = self.source_analysis(u)
            host = (urlparse(u).netloc or "").lower().removeprefix("www.")
            out.append({"url": u, "domain": host, "analysis": ana})
        return {"sources": out}
