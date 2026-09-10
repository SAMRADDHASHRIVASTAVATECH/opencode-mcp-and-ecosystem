"""Fact-checking skill (#27): verified / partially verified / uncertain /
contradicted / unknown with evidence."""
from __future__ import annotations

from typing import Optional

from .engine import VerificationEngine


class FactChecker:
    def __init__(self, verification: VerificationEngine):
        self.verification = verification

    VOCAB = {"verified": "verified", "partially_verified": "partially verified",
             "uncertain": "uncertain", "contradicted": "contradicted",
             "unknown": "unknown"}

    def check(self, statement: str, *, phrases: Optional[list] = None) -> dict:
        v = self.verification.verify(statement, phrases=phrases)
        label = self.VOCAB.get(v["status"], "unknown")
        return {
            "statement": statement,
            "verdict": label,
            "confidence": v["confidence"],
            "supporting": v["supporting_evidence"],
            "contradicting": v["contradicting_evidence"],
            "independent_support": v["independent_support"],
            "independent_contradiction": v["independent_contradiction"],
            "evidence_basis": "source-signal heuristic (deterministic)",
        }
