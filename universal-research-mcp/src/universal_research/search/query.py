"""QueryEngine: generate / expand / refine / validate / rank / deduplicate,
plus multi-family query strategies (#11, #12)."""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Optional

from .operators import parse_query, operator_query

STOP = {"the", "and", "for", "how", "what", "best", "top", "with", "that",
        "this", "from", "are", "was", "you", "your", "its", "have", "has",
        "about", "into", "which", "does", "where", "when"}

FAMILIES = ["discovery", "exact", "technical", "implementation",
            "source_specific", "verification", "contradiction", "historical",
            "current", "alternative"]


def _words(topic: str) -> list[str]:
    return [w for w in re.findall(r"\w+", topic.lower())
            if w not in STOP and len(w) > 2]


class QueryEngine:
    """Deterministic, no-LLM query construction. Optionally an LLM may be used
    upstream to expand topics, but every planner path can run on this alone."""

    def __init__(self, settings=None):
        self.settings = settings

    # -- generation -----------------------------------------------------
    def generate(self, topic: str, family: str = "discovery",
                 n: int = 4, **ctx) -> list[str]:
        topic = topic.strip().strip('"')
        if family == "exact":
            return [f'"{topic}"']
        if family == "current":
            return [f"{topic} 2026", f"{topic} recent news", f"{topic} latest"]
        if family == "historical":
            return [f"{topic} history", f"{topic} origins", f"{topic} timeline"]
        if family == "alternative":
            return [f"{topic} alternatives", f"compare {topic}", f"vs {topic}"]
        if family == "contradiction":
            return [f"{topic} criticism", f"{topic} limitations",
                    f"{topic} problems", f"{topic} failure", f"{topic} issues"]
        if family == "verification":
            return [f"{topic} documentation", f"official {topic}",
                    f"{topic} source code"]
        if family == "source_specific":
            target = ctx.get("target") or ctx.get("domain") or ""
            st = ctx.get("site")
            if st:
                return [f"site:{st} {topic}"]
            if target == "code":
                return [f"site:github.com {topic}", f"github {topic} repository",
                        f"{topic} github"]
            if target == "documents":
                return [f'filetype:pdf {topic}', f'{topic} pdf',
                        f'filetype:docx {topic}']
            if target == "government":
                return [f'site:gov {topic}', f"government {topic}"]
            if target == "news":
                return [f"{topic} news"]
            return [f"{topic} official documentation"]
        if family == "technical":
            return [f"{topic} technical", f"{topic} architecture",
                    f"{topic} implementation details"]
        if family == "implementation":
            return [f"{topic} example", f"{topic} code example",
                    f"{topic} tutorial"]
        # discovery
        return [topic, f"{topic} open source", f"intitle:{topic}"][:n]

    # -- families ---------------------------------------------------------
    def strategy(self, topic: str, ctx: Optional[dict] = None) -> dict:
        ctx = ctx or {}
        out = {}
        for fam in FAMILIES:
            qs = self.generate(topic, fam, ctx=ctx)
            out[fam] = qs
        return out

    # -- expansion --------------------------------------------------------
    def expand(self, topic: str, terms: Optional[list] = None,
               synonyms: Optional[list] = None, n: int = 6) -> list[str]:
        base = _words(topic)
        pool = list(base)
        for t in (terms or []) + (synonyms or []):
            for w in _words(t):
                if w not in pool:
                    pool.append(w)
        variants = []
        for w in pool:
            variants.append(f"{topic} {w}")
        # return distinct
        seen = {topic}
        out = []
        for v in [topic] + variants:
            if v not in seen and len(out) < n:
                seen.add(v)
                out.append(v)
        return out

    # -- refinement -------------------------------------------------------
    def refine(self, query: str, *, domain: str = "", filetype: str = "",
               add_site: str = "", remove_terms: Optional[list] = None,
               exact: bool = False) -> str:
        parts = []
        terms = _words(query)
        remove = set(remove_terms or [])
        terms = [t for t in terms if t not in remove]
        if exact:
            parts.append(f'"{query.strip()}"')
        else:
            parts.extend(terms)
        if add_site or domain:
            parts.append(f"site:{add_site or domain}")
        if filetype:
            parts.append(f"filetype:{filetype}")
        return " ".join(parts)

    # -- validate ----------------------------------------------------------
    def validate(self, query: str) -> dict:
        pq = parse_query(query)
        issues = []
        if not pq.plain_terms and not pq.exact_phrases and not pq.include_sites:
            issues.append("query has no searchable terms")
        if len(query) > 500:
            issues.append("query too long")
        ok = not issues
        return {"valid": ok, "issues": issues, "parsed": pq.to_dict()}

    # -- dedupe/rank passthrough --------------------------------------------
    def deduplicate(self, queries: list[str]) -> list[str]:
        seen, out = set(), []
        for q in queries:
            key = q.lower().strip()
            if key not in seen:
                seen.add(key)
                out.append(q)
        return out


def combine_operators(query: str, **ops) -> str:
    """Append operator fields to an existing query string."""
    parts = [query]
    if ops.get("site"):
        parts.append(f"site:{ops['site']}")
    if ops.get("filetype"):
        parts.append(f"filetype:{ops['filetype']}")
    if ops.get("after"):
        parts.append(f"after:{ops['after']}")
    if ops.get("before"):
        parts.append(f"before:{ops['before']}")
    return " ".join([p for p in parts if p])
