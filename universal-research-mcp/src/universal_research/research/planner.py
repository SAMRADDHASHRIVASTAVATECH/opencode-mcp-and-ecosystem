"""ResearchPlanner (#32, #33, #46): decompose an objective into steps.

Produces an ordered plan of actions (each action references a registered
skill/tool and carries concrete parameters). Works deterministically; an
optional LLM may refine scope but the default path is self-sufficient.
"""
from __future__ import annotations

from typing import Optional

from ..search.query import QueryEngine


class ResearchPlanner:
    def __init__(self, settings=None, query_engine: Optional[QueryEngine] = None,
                 llm=None):
        self.settings = settings
        self.query = query_engine or QueryEngine(settings)
        self.llm = llm

    # --- intent heuristics -------------------------------------------------
    def classify(self, objective: str) -> str:
        o = objective.lower()
        if any(w in o for w in ["compare", "versus", " vs ", "alternative",
                                "which is better"]):
            return "comparison"
        if any(w in o for w in ["error", "bug", "fail", "exception", "crash"]):
            return "error_investigation"
        if any(w in o for w in ["verify", "is it true", "fact check", "true?",
                                "confirm"]):
            return "verification"
        if any(w in o for w in ["architecture", "system", "pipeline", "stack",
                                "best", "framework", "approach"]):
            return "technical"
        return "general"

    def plan(self, objective: str, *, depth: str = "normal",
             budget: Optional[dict] = None) -> dict:
        """Return {'objective', 'kind', 'steps': [step...]}.

        A step: {"skill": "...", "tool": "...", "question": "...",
                 "query": "...", "kind": "...", "target": "..."}
        """
        kind = self.classify(objective)
        q = self.query
        base_q = self._base_queries(q, objective, kind)
        steps = []
        for fam_q in base_q:
            steps.append(self._mkstep("search_web", "discovery", fam_q,
                                      kind, "web"))
        # discovery sources -> deeper: read, docs, github, academic etc.
        if kind in ("technical", "general", "comparison"):
            steps.append(self._mkstep("search_web", "source_specific",
                                      q.generate(objective, "source_specific",
                                                 target="documents")[0],
                                      kind, "documents"))
            steps.append(self._mkstep("search_github", "code",
                                      q.generate(objective, "discovery")[0],
                                      kind, "code"))
            steps.append(self._mkstep("search_academic", "paper",
                                      objective, kind, "academic"))
            steps.append(self._mkstep("search_community", "community",
                                      objective, kind, "community"))
            steps.append(self._mkstep("crawl_web", "explore", objective,
                                      kind, "crawl"))
        # verification + contradiction always, anti-confirmation (#48)
        steps.append(self._mkstep("find_contradictions", "contradiction",
                                  objective, kind, "web"))
        steps.append(self._mkstep("verify_claim", "verification", objective,
                                  kind, "web"))
        return {"objective": objective, "kind": kind,
                "steps": self._truncate(steps, budget)}

    def _base_queries(self, q, objective, kind) -> list[str]:
        fams = ["discovery", "technical", "implementation"]
        if kind == "comparison":
            fams = ["discovery", "alternative"]
        if kind == "error_investigation":
            return [objective]
        if kind == "verification":
            fams = ["discovery", "verification"]
        out = []
        for f in fams:
            out.extend(q.generate(objective, f, n=2))
        return out

    def _mkstep(self, tool, family, query, kind, target) -> dict:
        return {"tool": tool, "family": family, "query": query,
                "kind": kind, "target": target, "question": _as_question(query)}

    def _truncate(self, steps, budget) -> list:
        if budget and budget.get("max_iterations"):
            return steps[: int(budget["max_iterations"])]
        return steps[:16]


def _as_question(query: str) -> str:
    q = query.strip()
    return q + "?"
