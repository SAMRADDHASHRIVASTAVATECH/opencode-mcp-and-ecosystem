"""Search operator parsing and construction (#9, #10).

Understood operators (where the backing provider supports them):
  "exact phrase", site: (and -site:), OR, -word, intitle:, allintitle:,
  inurl:, allinurl:, filetype: (ext:), intext:, before:, after:.

We parse an expression so the engine can (a) pass an effective operator query
to providers that understand them, and (b) expose structured intent so the
router can auto-apply operators (e.g. site:github.com, filetype:pdf).
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Optional

_OPERATOR_RE = re.compile(
    r'(?P<op>site|filetype|ext|intitle|allintitle|inurl|allinurl|intext|'
    r'before|after):(?P<val>\S+)', re.I)


@dataclass
class ParsedQuery:
    raw: str
    plain_terms: list = field(default_factory=list)
    exact_phrases: list = field(default_factory=list)
    include_sites: list = field(default_factory=list)
    exclude_sites: list = field(default_factory=list)
    exclude_words: list = field(default_factory=list)
    intitle: list = field(default_factory=list)
    inurl: list = field(default_factory=list)
    filetype: str = ""
    before: str = ""
    after: str = ""
    has_or: bool = False

    @property
    def operator_hint(self) -> str:
        if self.filetype:
            return "documents" if self.filetype.lower() in (
                "pdf", "doc", "docx", "txt") else "filetype"
        if any("github" in s for s in self.include_sites) or \
                any("github" in s for s in self.exclude_sites):
            return "code"
        return ""

    def to_dict(self) -> dict:
        return {"raw": self.raw, "terms": self.plain_terms,
                "phrases": self.exact_phrases,
                "include_sites": self.include_sites,
                "exclude_sites": self.exclude_sites,
                "exclude_words": self.exclude_words,
                "intitle": self.intitle, "inurl": self.inurl,
                "filetype": self.filetype, "before": self.before,
                "after": self.after, "has_or": self.has_or,
                "operator_hint": self.operator_hint}


def parse_query(expression: str) -> ParsedQuery:
    expression = (expression or "").strip()
    parsed = ParsedQuery(raw=expression)

    # 1) exact phrases "…"
    phrases = re.findall(r'"([^"]+)"', expression)
    parsed.exact_phrases = [p.strip() for p in phrases if p.strip()]

    # 2) strip quoted phrases for further term analysis
    work = re.sub(r'"[^"]*"', " ", expression)

    # 3) OR
    if re.search(r"\bOR\b", work):
        parsed.has_or = True

    # 4) operators
    for m in _OPERATOR_RE.finditer(work):
        op, val = m.group("op").lower(), m.group("val").strip('"')
        neg = False
        # check preceding sign handled below via token scan instead
        if op == "site":
            if val.startswith("-"):
                parsed.exclude_sites.append(val[1:])
            else:
                parsed.include_sites.append(val)
        elif op == "filetype" or op == "ext":
            parsed.filetype = val.lstrip(".")
        elif op in ("intitle", "allintitle"):
            parsed.intitle.append(val)
        elif op in ("inurl", "allinurl"):
            parsed.inurl.append(val)
        elif op == "before":
            parsed.before = val
        elif op == "after":
            parsed.after = val
        elif op == "intext":
            parsed.plain_terms.append(val)

    # 5) remove operator tokens from term source
    work = _OPERATOR_RE.sub(" ", work)
    # 6) tokenize remaining into terms/exclusions
    tokens = re.findall(r"[^\s]+", work)
    for tok in tokens:
        low = tok
        if low.startswith("-"):
            parsed.exclude_words.append(low[1:].strip('"'))
        elif low.lower() != "or":
            parsed.plain_terms.append(low.strip('"'))
    return parsed


def effective_query(expression: str) -> str:
    """The query string to send to providers: original, lightly normalised.
    We keep operators in place because Bing understands most of them."""
    return (expression or "").strip()


def operator_query(**kw) -> str:
    """Construct an operator query from structured fields."""
    parts = []
    if kw.get("filetype"):
        parts.append(f"filetype:{kw['filetype']}")
    if kw.get("site"):
        for s in (kw["site"] if isinstance(kw["site"], list) else [kw["site"]]):
            parts.append(f"site:{s}")
    if kw.get("intitle"):
        parts.append(f"intitle:{kw['intitle']}")
    if kw.get("inurl"):
        parts.append(f"inurl:{kw['inurl']}")
    if kw.get("after"):
        parts.append(f"after:{kw['after']}")
    if kw.get("before"):
        parts.append(f"before:{kw['before']}")
    terms = kw.get("terms", [])
    if kw.get("phrase"):
        parts.append(f'"{kw["phrase"]}"')
    parts += [t for t in terms if not _contains_operator(t)]
    return " ".join(parts)


def _contains_operator(t: str) -> bool:
    return _OPERATOR_RE.search(t) is not None


def is_exact_phrase(expression: str) -> bool:
    return bool(re.search(r'"([^"]+)"', expression))


def domain_for_type(target: str, region: str = "") -> str:
    """Auto operator selection helper (#10): map a research target to an
    authoritative domain or extension."""
    mapping = {
        "github": "github.com",
        "official": "wikipedia.org",
        "news": "news",
    }
    if target == "government":
        # region-aware; default broad official gov domains
        tld = {"in": "gov.in", "us": "gov", "uk": "gov.uk", "ca": "gc.ca",
               "au": "gov.au", "eu": "europa.eu"}.get(region.lower(), "gov")
        return f".{tld}" if tld.startswith("gov") or tld.endswith(".eu") else tld
    if target == "academic":
        return "arxiv.org"
    if target == "official_docs":
        return ""
    return mapping.get(target, "")
