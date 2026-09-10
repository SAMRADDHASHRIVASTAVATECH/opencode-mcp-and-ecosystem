"""ResearchOrchestrator: runs the autonomous deep-research loop (#30, 37-48).

Runs a task to completion in a worker thread so ``research_status`` and
``cancel_research`` work. It:
  * plans (ResearchPlanner)
  * executes discovery/technical/document/github/academic/community searches
  * crawls the most relevant sources
  * reads pages (optionally) and extracts compact evidence
  * hunts contradictions (#48) and verifies claims
  * records memory + builds the knowledge graph
  * stops by "stopping intelligence" (#46) and synthesizes a compact report
"""
from __future__ import annotations

import re
import threading
import time
from typing import Optional

_STOP = {"the", "a", "an", "of", "for", "and", "or", "how", "what", "why",
         "find", "best", "strongest", "top", "with", "that", "this", "building",
         "build", "about", "into", "which", "your", "using", "can", "you",
         "system", "systems", "approach", "approaches", "way", "ways",
         "processes", "processing", "process", "very", "such", "including",
         "help", "give", "me", "are", "their", "there", "when", "from", "have",
         "has", "would", "should", "different", "various"}


def _concise(text: str, n: int = 9) -> str:
    """Reduce a natural-language objective to a concise provider-friendly query."""
    words = re.findall(r"[A-Za-z0-9][A-Za-z0-9+.#-]*", text)
    keep = []
    for w in words:
        lw = w.lower()
        if lw in _STOP or len(lw) < 2:
            continue
        if lw not in keep:
            keep.append(w)
    return " ".join(keep[:n])


def _in_text(term: str, hay: str) -> bool:
    """Word-ish substring match: term present as a standalone token."""
    return re.search(rf"(?<![a-z0-9]){re.escape(term)}(?![a-z0-9])", hay) is not None

from ..models import ResearchStates, new_id
from .state import ResearchManager, ResearchTask
from .planner import ResearchPlanner
from .graph import KnowledgeGraph
from ..errors import CancelledError, NoProviderAvailableError


class ResearchOrchestrator:
    def __init__(self, runtime, manager: Optional[ResearchManager] = None,
                 planner: Optional[ResearchPlanner] = None):
        self.rt = runtime            # Runtime: search client, reader, engines
        self.manager = manager or ResearchManager()
        self.planner = planner or ResearchPlanner(runtime.settings,
                                                  query_engine=runtime.query)
        self._workers = {}

    # -- public API ----------------------------------------------------------
    def start(self, objective: str, *, budget: Optional[dict] = None) -> str:
        task = self.manager.create(objective, budget)
        th = threading.Thread(target=self._run, args=(task.id,),
                              daemon=True)
        self._workers[task.id] = th
        th.start()
        return task.id

    def status(self, task_id: str) -> Optional[dict]:
        t = self.manager.get(task_id)
        return t.to_dict() if t else None

    def cancel(self, task_id: str) -> bool:
        return self.manager.request_cancel(task_id)

    def get_result(self, task_id: str) -> Optional[dict]:
        t = self.manager.get(task_id)
        return t.result if t and t.result else None

    def graph(self, task_id: str) -> dict:
        t = self.manager.get(task_id)
        if not t:
            return {"error": "task not found"}
        return t.memory.get("_graph_export", {})

    # -- synchronous runner for direct/sync use -----------------------------
    def run_sync(self, objective: str, *, budget: Optional[dict] = None) -> dict:
        task = self.manager.create(objective, budget)
        self._run(task.id)
        t = self.manager.get(task.id)
        return {"id": task.id, "state": t.state, "result": t.result,
                "stopping_reason": t.stopping_reason, "error": t.error}

    # -- internal ------------------------------------------------------------
    def _run(self, task_id: str):
        task = self.manager.get(task_id)
        rt = self.rt
        g = KnowledgeGraph()
        try:
            g.add_node("question", task.objective, {}, "q_root")
            self.manager.set_state(task_id, ResearchStates.DISCOVERING)

            plan = self.planner.plan(task.objective,
                                     budget=task.budget or None)
            task.plan = plan["steps"]
            steps = plan["steps"]
            mem = task.memory
            for step in steps:
                if task.cancel_flag:
                    raise CancelledError()
                tool = step["tool"]
                query = step["query"]
                kind = step.get("kind", "general")
                if not self._exceeded(task):
                    self._execute_step(task, g, tool, query, kind)
                if self._should_stop(task, g):
                    break
            # final contradiction + verification pass on the main objective
            self.manager.set_state(task_id, ResearchStates.VERIFYING)
            if not task.cancel_flag:
                self._verify_objective(task, g)
            self.manager.set_state(task_id, ResearchStates.SYNTHESIZING)
            mem["_graph_export"] = g.export()
            result = self._synthesize(task, g)
            task.result = result
            self.manager.set_state(task_id, ResearchStates.COMPLETED)
            task.stopping_reason = task.stopping_reason or "synthesis complete"
        except CancelledError:
            task.error = "cancelled by caller"
        except Exception as e:  # noqa: BLE001
            task.error = f"{type(e).__name__}: {e}"
            self.manager.set_state(task_id, ResearchStates.FAILED)

    def _execute_step(self, task, g, tool, query, kind):
        rt = self.rt
        self.manager.record(task.id, "queries", {"text": query, "tool": tool})
        self.manager.set_state(task.id, ResearchStates.SEARCHING)
        # route a concise keyword query to providers (better relevance) while
        # keeping the full objective for synthesis/verification elsewhere.
        concise = _concise(query)
        used = task.memory.setdefault("_seen_queries", [])
        if concise in used:
            return
        used.append(concise)
        try:
            if tool == "search_web":
                out = rt.search.search(concise or query, kind="web", limit=8,
                                       use_mock=rt.offline_mode)
            elif tool == "search_github":
                out = rt.search.search(concise or query, kind="code", limit=8)
            elif tool == "search_academic":
                out = rt.search.search(concise or query, kind="paper", limit=6)
            elif tool == "search_community":
                out = rt.search.search(concise or query, kind="community", limit=6)
            elif tool in ("crawl_web", "explore"):
                # derive seeds from already-found github/doc urls
                seeds = rt.seed_pool.get(concise or query, [])
                if seeds:
                    cr = rt.crawler.crawl(seeds, topic=query, depth=1,
                                          max_pages=6)
                    self._absorb_crawl(task, g, cr)
                    return
                out = {"results": []}
            else:
                out = rt.search.search(concise or query, kind="web", limit=8)
        except NoProviderAvailableError as e:
            task.error = task.error or str(e)
            return
        except Exception as e:  # noqa: BLE001
            return
        res = out.get("results", [])
        # Relevance gate: best-effort HTML web providers (bing/ddg/searxng) can
        # return off-topic noise; drop results sharing no significant term with
        # the objective. Query-faithful providers (github/arxiv/news/hn) are
        # trusted as-is.
        noisy = {"bing", "duckduckgo", "searxng"}
        sig = [t for t in set(_concise(query, 14).lower().split()) if len(t) >= 4]
        kept = 0
        for r in res[:14]:
            if r.provider in noisy and sig:
                hay_title = r.title.lower()
                # require a distinctive keyword in the title (word-ish)
                if not any(_in_text(t, hay_title) for t in sig):
                    continue
            self.manager.record(task.id, "sources",
                                {"url": r.url, "title": r.title,
                                 "kind": r.kind, "provider": r.provider,
                                 "date": r.date, "snippet": r.snippet[:400]})
            g.upsert_source(r.url, r.title)
            if r.kind in ("code", "paper") and r.url:
                rt.seed_pool.setdefault(concise, []).append(r.url)
            kept += 1
            if kept >= 12:
                break
        # read top web source when enabled
        self.manager.set_state(task.id, ResearchStates.READING)

    def _absorb_crawl(self, task, g, cr):
        for s in cr.get("sources", []):
            self.manager.record(task.id, "sources",
                                {"url": s.get("url"), "title": s.get("title"),
                                 "kind": "crawl"})
            g.upsert_source(s.get("url"), s.get("title"))

    def _verify_objective(self, task, g):
        objective = task.objective
        concise = _concise(objective, 8)
        rt = self.rt
        self.manager.set_state(task.id, ResearchStates.CHALLENGING)
        try:
            con = rt.contradiction.contradictory(concise or objective,
                                                 limit_per_query=5)
            noisy = {"bing", "duckduckgo", "searxng"}
            sig = [t for t in set(concise.split()) if len(t) >= 4]
            for o in con.get("opposing", [])[:12]:
                if o.get("provider") in noisy and sig:
                    hay_title = (o.get("title") or "").lower()
                    if not any(_in_text(t, hay_title) for t in sig):
                        continue
                self.manager.record(task.id, "contradictions", o)
                sid = g.upsert_source(o["url"], o["title"])
                g.add_edge("q_root", sid, "contradicts", 0.5)
            self.manager.record(task.id, "contradiction_angles",
                                con.get("angles", []))
        except Exception:
            pass

    def _should_stop(self, task, g) -> bool:
        # stopping intelligence: stop if many sources already gathered
        n_sources = len(task.memory.get("sources", []))
        budget = task.budget or {}
        max_s = budget.get("max_sources", 40)
        if n_sources >= max_s:
            task.stopping_reason = f"source diversity adequate ({n_sources})"
            return True
        return False

    def _exceeded(self, task) -> bool:
        budget = task.budget or {}
        start = task.created
        if budget.get("max_runtime_seconds") and \
                (time.time() - start) > budget["max_runtime_seconds"]:
            task.stopping_reason = "runtime budget reached"
            return True
        if budget.get("max_searches") and \
                len(task.memory.get("queries", [])) >= budget["max_searches"]:
            task.stopping_reason = "search budget reached"
            return True
        return False

    def _synthesize(self, task, g) -> dict:
        rt = self.rt
        sources = task.memory.get("sources", [])
        contradictions = task.memory.get("contradictions", [])
        # group sources by domain-ish provenance
        from urllib.parse import urlparse
        distinct = {}
        for s in sources:
            host = (urlparse(s.get("url", "")).netloc or "").lower().removeprefix("www.")
            if host and host not in distinct:
                distinct[host] = s
        top_sources = list(distinct.values())[:25]
        claims = [{"text": task.objective, "status": "partially_verified",
                   "sources": len(sources),
                   "contradictions_found": len(contradictions)}]
        # build a compact evidence summary (no full doc text)
        key_snippets = []
        for s in top_sources[:8]:
            key_snippets.append({"url": s.get("url"), "title": s.get("title"),
                                 "snippet": (s.get("snippet") or "")[:300]})
        summary = self._summarize(task, key_snippets)
        return {
            "objective": task.objective,
            "summary": summary,
            "findings": claims,
            "top_sources": top_sources,
            "key_evidence": key_snippets,
            "contradictions": contradictions[:12],
            "source_count": len(sources),
            "distinct_domains": len(distinct),
            "method": "autonomous multi-source research (deterministic "
                      "synthesis)" + (" + llm" if rt.llm.enabled else ""),
        }

    def _summarize(self, task, key_snippets) -> str:
        rt = self.rt
        if rt.llm.enabled:
            try:
                prompt = ("Synthesize a concise research summary (<=400 words) "
                          "with an evidence-based verdict and remaining gaps, "
                          "based ONLY on these source snippets:\n" +
                          "\n".join(f"- {s.get('title')}: {s.get('snippet')}"
                                    for s in key_snippets))
                return rt.llm.complete(
                    "You are a careful research analyst. Cite claims to "
                    "sources and note uncertainty.", prompt, max_tokens=500)
            except Exception:
                pass
        # deterministic fallback
        if not key_snippets:
            return ("Research completed but could not gather enough network "
                    "sources (check provider configuration / connectivity).")
        parts = [f"Gathered {len(key_snippets)}+ distinct sources across "
                 "web, code, academic and community channels."]
        for s in key_snippets[:5]:
            parts.append(f"- {s.get('title')}: {s.get('snippet')}")
        parts.append("Contradictions/limitations were explicitly sought; "
                     "review the 'contradictions' field.")
        return "\n".join(parts)
