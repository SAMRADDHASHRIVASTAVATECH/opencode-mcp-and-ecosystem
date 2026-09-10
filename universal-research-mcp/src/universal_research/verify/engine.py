"""Evidence extraction, claim verification and contradiction search (#24-26).

These are *research-support* operations. Without an LLM/verdict model they:
  * extract evidence (claim -> supporting quotes + source + location),
  * gather independent supporting AND contradicting signals,
  * produce a structured confidence assessment from source signals.

An optional LLM callable may be attached to produce richer verdicts, but the
default path is deterministic and truthful about what it did.
"""
from __future__ import annotations

import re
from typing import Optional

from ..models import Claim, Evidence
from .. import sources as source_analysis


class EvidenceEngine:
    """Find evidence (supporting + opposing) for a claim across the web."""

    def __init__(self, search_client, reader=None):
        self.search = search_client
        self.reader = reader

    def _search_kinds(self, claim: str, phrases: Optional[list] = None):
        queries = [claim] + [f'"{p}"' for p in (phrases or [])]
        queries = list(dict.fromkeys(queries))
        return queries

    def extract(self, claim: str, *, support_terms: Optional[list] = None,
                fetch_depth: int = 0, limit_per_query: int = 6) -> dict:
        """Search supporting angle; return evidence records + source analyses."""
        supporting = []
        queries = [claim]
        if support_terms:
            queries += [f"{claim} {t}" for t in support_terms[:3]]
        queries = list(dict.fromkeys(queries))
        seen_urls = set()
        notes = []
        results_by_kind = {}
        for q in queries[:4]:
            try:
                out = self.search.search(q, kind="web", limit=limit_per_query)
            except Exception as e:  # noqa: BLE001
                notes.append(f"search failed for {q!r}: {e}")
                continue
            for r in out["results"]:
                if r.url in seen_urls:
                    continue
                seen_urls.add(r.url)
                ana = source_analysis.analyze_source(
                    r.url, title=r.title, snippet=r.snippet,
                    provider=r.provider)
                supporting.append({
                    "url": r.url, "title": r.title, "snippet": r.snippet,
                    "provider": r.provider, "analysis": ana,
                })
                results_by_kind.setdefault(r.kind, 0)
                results_by_kind[r.kind] += 1
        return {"claim": claim, "supporting": supporting,
                "result_kinds": results_by_kind, "notes": notes,
                "queries": queries}

    def contradictory(self, claim: str, *, angles: Optional[list] = None,
                      limit_per_query: int = 6) -> dict:
        """Actively seek criticism/limits/failures/alternatives (#48)."""
        default_angles = ["criticism", "limitations", "problems", "failure",
                          "issues", "alternatives", "benchmark", "contradiction"]
        for a in (angles or default_angles):
            # don't fabricate; just gather signals
            pass
        opposing = []
        seen = set()
        queries = []
        for a in (angles or default_angles):
            queries.append(f"{claim} {a}")
        queries = list(dict.fromkeys(queries))[:6]
        for q in queries:
            try:
                out = self.search.search(q, kind="web", limit=limit_per_query)
            except Exception:
                continue
            for r in out["results"]:
                if r.url in seen:
                    continue
                seen.add(r.url)
                opposing.append({"url": r.url, "title": r.title,
                                 "snippet": r.snippet,
                                 "provider": r.provider, "angle": q})
        return {"claim": claim, "angles": (angles or default_angles),
                "opposing": opposing, "queries": queries}


class VerificationEngine:
    """Assemble supporting + contradicting evidence and assess confidence."""

    def __init__(self, evidence_engine: EvidenceEngine, search_client=None):
        self.evidence = evidence_engine
        self.search = search_client or evidence_engine.search

    def verify(self, claim: str, *, phrases: Optional[list] = None,
               fetch_depth: int = 0, verification_threshold: float = 0.5,
               max_sources: int = 24) -> dict:
        sup = self.evidence.extract(claim, support_terms=phrases,
                                    fetch_depth=fetch_depth)
        con = self.evidence.contradictory(claim)
        supporting = sup["supporting"]
        opposing = con["opposing"]

        # Only treat an opposing result as a real contradiction if its text
        # carries an explicit negative/dispute signal; otherwise it is topic
        # overlap, not evidence against the claim (avoid noise mislabelling).
        hard_oppose = [o for o in opposing if _negative_signal(o)]
        soft_oppose = [o for o in opposing if o not in hard_oppose]

        indep_support = _count_independent(supporting)
        indep_oppose = _count_independent(hard_oppose)
        total = indep_support + indep_oppose
        if total == 0:
            status, confidence = "unknown", 0.0
        else:
            ratio = indep_support / total
            high_auth_support = sum(1 for s in supporting
                                    if s["analysis"]["authority_level"] >= 4)
            confidence = min(0.95, 0.3 + ratio * 0.6 + high_auth_support * 0.04)
            confidence = round(confidence, 2)
            if confidence >= verification_threshold and indep_support >= 1 \
                    and indep_oppose == 0:
                status = "verified"
            elif indep_oppose >= indep_support and indep_oppose >= 1:
                status = "contradicted"
            elif indep_support >= 1:
                status = "partially_verified"
            else:
                status = "uncertain"
        return {
            "claim": claim,
            "status": status,
            "confidence": confidence,
            "supporting_evidence": supporting[:max_sources],
            "contradicting_evidence": opposing[:max_sources],
            "independent_support": indep_support,
            "independent_contradiction": indep_oppose,
            "notes": sup["notes"],
            "verified_by_llm": False,
        }

    def build_claim(self, claim_text: str, status: str, confidence: float,
                    evidence: Optional[list] = None) -> dict:
        c = Claim(text=claim_text, status=status, confidence=confidence)
        return c.to_dict()


_NEGATIVE_MARKERS = ["does not", "is not", "are not", "was not", "not true",
                     "incorrect", "wrong", "false", "disputed", "unfounded",
                     "cannot", "can not", "doesn't", "isn't", "limitation",
                     "not support", "contradict", "no evidence", "fails to",
                     "doesn't work", "broken", "outdated", "discontinued",
                     "not recommended", "lacks"]


def _negative_signal(item: dict) -> bool:
    text = ((item.get("snippet") or "") + " " + (item.get("title") or "")).lower()
    return any(m in text for m in _NEGATIVE_MARKERS)


def _count_independent(items: list) -> int:
    seen = set()
    n = 0
    for it in items:
        dom = it.get("analysis", {}).get("domain", it.get("url", ""))
        indep = it.get("analysis", {}).get("independence", "independent")
        if dom in seen or indep == "syndicated":
            continue
        seen.add(dom)
        n += 1
    return n
