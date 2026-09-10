"""Core data models shared across the whole system.

All models serialise to compact dicts (JSON-safe) so the calling agent
receives small structured payloads regardless of how large the underlying
sources are.
"""
from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field, asdict
from typing import Any, Optional


def _now() -> float:
    return time.time()


def new_id(prefix: str) -> str:
    return f"{prefix}_{uuid.uuid4().hex[:12]}"


@dataclass
class SearchResult:
    """A normalized single result from any provider."""
    title: str
    url: str
    snippet: str = ""
    provider: str = ""
    rank: int = 0
    kind: str = "web"          # web | code | paper | news | community | doc
    date: Optional[str] = None  # best-known publication date
    extra: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {"title": self.title, "url": self.url, "snippet": self.snippet,
                "provider": self.provider, "rank": self.rank, "kind": self.kind,
                "date": self.date, "extra": self.extra}


@dataclass
class Source:
    """A fetched source (page/doc) with parsed content stored externally."""
    url: str
    title: str = ""
    canonical_url: str = ""
    domain: str = ""
    source_type: str = "web"     # web|pdf|doc|code|paper|news|community
    content_type: str = "html"
    author: str = ""
    date: str = ""
    retrieval_date: float = field(default_factory=_now)
    status: int = 0
    final_url: str = ""
    headings: list = field(default_factory=list)
    links: list = field(default_factory=list)
    size_bytes: int = 0
    # heavy content is held externally (id into doc index / cache) not in the
    # message to the model.
    content_id: Optional[str] = None
    analysis: dict = field(default_factory=dict)

    def to_dict(self, include_heavy: bool = False) -> dict:
        d = {"url": self.url, "title": self.title,
             "canonical_url": self.canonical_url, "domain": self.domain,
             "source_type": self.source_type,
             "content_type": self.content_type, "author": self.author,
             "date": self.date, "retrieval_date": self.retrieval_date,
             "status": self.status, "final_url": self.final_url,
             "headings": self.headings[:20],
             "size_bytes": self.size_bytes, "analysis": self.analysis}
        if include_heavy:
            d["links"] = self.links
        return d


@dataclass
class Claim:
    """A proposition extracted from or given to the research system."""
    id: str = field(default_factory=lambda: new_id("claim"))
    text: str = ""
    status: str = "unassessed"   # verified|partially_verified|uncertain|contradicted|unknown|unassessed
    confidence: float = 0.0
    assessment: str = ""
    evidences: list = field(default_factory=list)   # list of Evidence dicts
    source_text: str = ""       # originating question or claim context
    created: float = field(default_factory=_now)

    def to_dict(self) -> dict:
        return {"id": self.id, "text": self.text, "status": self.status,
                "confidence": self.confidence, "assessment": self.assessment,
                "evidence": self.evidences, "created": self.created}


@dataclass
class Evidence:
    """One piece of evidence linking a claim to a source location."""
    claim_id: str = ""
    source_url: str = ""
    source_title: str = ""
    quote: str = ""
    location: str = ""          # page/section/heading reference
    method: str = ""            # how obtained (search/read/crawl)
    independence: str = "unknown"  # independent|derived|syndicated|unknown
    confidence: float = 0.0
    retrieved_at: float = field(default_factory=_now)

    def to_dict(self) -> dict:
        return {"claim_id": self.claim_id, "source_url": self.source_url,
                "source_title": self.source_title, "quote": self.quote,
                "location": self.location, "method": self.method,
                "independence": self.independence, "confidence": self.confidence,
                "retrieved_at": self.retrieved_at}


@dataclass
class Finding:
    """A resolved sub-question / finding in a research task."""
    question: str
    answer: str = ""
    claims: list = field(default_factory=list)     # Claim dicts
    sources: list = field(default_factory=list)    # Source urls/titles
    confidence: float = 0.0
    gaps: list = field(default_factory=list)

    def to_dict(self) -> dict:
        return {"question": self.question, "answer": self.answer,
                "claims": self.claims, "sources": self.sources,
                "confidence": self.confidence, "gaps": self.gaps}


@dataclass
class Node:
    """Knowledge-graph node."""
    id: str = ""
    kind: str = ""             # question|subquestion|claim|evidence|source|entity|term
    label: str = ""
    data: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {"id": self.id, "kind": self.kind, "label": self.label,
                "data": self.data}


@dataclass
class Edge:
    """Knowledge-graph edge with a typed relation."""
    src: str
    dst: str
    rel: str                   # supports|contradicts|references|depends_on|implements|derived_from|targets|from
    weight: float = 1.0
    data: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {"src": self.src, "dst": self.dst, "rel": self.rel,
                "weight": self.weight, "data": self.data}


class ResearchStates:
    CREATED = "CREATED"
    PLANNING = "PLANNING"
    DISCOVERING = "DISCOVERING"
    SEARCHING = "SEARCHING"
    READING = "READING"
    EXTRACTING = "EXTRACTING"
    VERIFYING = "VERIFYING"
    CHALLENGING = "CHALLENGING"
    SYNTHESIZING = "SYNTHESIZING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


# Relationship vocab
RELATIONS = {"supports", "contradicts", "references", "depends_on",
             "implements", "derived_from", "targets", "from"}
