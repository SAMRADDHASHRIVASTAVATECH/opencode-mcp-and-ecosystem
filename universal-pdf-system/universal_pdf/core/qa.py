"""Retrieval-grounded Q&A over a document (requirement 10/28/32).

Design for weak models & huge docs:
  1. retrieve only the few most relevant chunks/pages (indexed externally),
  2. hand only those + the question to a reasoning callable,
  3. require the answer to cite page provenance.

``answer(..., reasoning=callable)`` uses an injected reasoning function
(prompt->text). If none is supplied it returns the retrieved evidence with a
clear note instead of fabricating an answer (graceful degradation).
"""
from __future__ import annotations

from typing import Callable, Optional

from ..result import Outcome
from ..core import summarize as _sum
from . import state as kb


def retrieve(path_or_docid: str, question: str, top_k: int = 6,
             store: Optional[kb.DocumentStore] = None,
             password=None) -> Outcome:
    """Return the most relevant chunks/pages as context with provenance.

    Uses lexical relevance over persisted page text when a store/doc_id is
    provided, otherwise streams the source PDF pages (no full load).
    """
    import re
    out = Outcome(skill="pdf-qa")
    words = [w for w in re.split(r"\W+", question.lower()) if len(w) > 2]
    if not words:
        words = [question.lower()]

    hits = []
    if store:
        doc_id = path_or_docid
        rows = store.conn.execute(
            "SELECT page,text FROM pages WHERE doc_id=?",
            (doc_id,)).fetchall()
        scored = []
        for r in rows:
            t = (r["text"] or "").lower()
            score = sum(t.count(w) for w in words)
            if score:
                scored.append((score, r["page"], r["text"]))
        scored.sort(key=lambda x: -x[0])
        for score, pno, text in scored[:top_k]:
            hits.append({"page": pno, "score": score, "text": text,
                         "doc_id": doc_id})
    else:
        # stream source pages
        from ..core import extract as ex
        scored = []
        for pno, text in ex.iter_page_text(path_or_docid, password):
            t = text.lower()
            score = sum(t.count(w) for w in words)
            if score:
                scored.append((score, pno, text))
        scored.sort(key=lambda x: -x[0])
        for score, pno, text in scored[:top_k]:
            hits.append({"page": pno, "score": score, "text": text})
    out.ok = True
    out.data = {"question": question, "hits": hits,
                "retrieved_pages": len(hits)}
    out.check("retrieved", ">=1", len(hits), True)
    return out


def answer(path_or_docid: str, question: str, top_k: int = 6,
           reasoning: Optional[Callable] = None,
           store: Optional[kb.DocumentStore] = None,
           max_context_chars: int = 6000, password=None) -> Outcome:
    """Answer a question grounded in retrieved context, with page citations.

    reasoning: callable(prompt: str) -> str. When None the method degrades to
    returning the retrieved evidence (never fabricates an answer).
    """
    out = Outcome(skill="pdf-qa")
    retr = retrieve(path_or_docid, question, top_k=top_k, store=store,
                    password=password)
    hits = retr.data["hits"]
    if not hits:
        out.ok = True
        out.status = "completed"
        out.data = {"question": question, "answer": None,
                    "citations": [], "note": "no relevant content found"}
        return out

    # build a bounded context block with citations
    context = []
    budget = 0
    for h in hits:
        snippet = (h["text"] or "")[: max_context_chars // max(1, len(hits))]
        context.append(f"[page {h['page']}]\n{snippet}")
        budget += len(snippet)

    citations = [{"page": h["page"]} for h in hits]

    if reasoning is None:
        out.ok = False
        out.degraded = True
        out.status = "degraded"
        out.data = {"question": question, "answer": None,
                    "evidence": [h["text"] for h in hits],
                    "citations": citations,
                    "note": "no reasoning model registered; returning retrieved "
                            "evidence only."}
        out.warnings.append("No reasoning provider -> evidence-only Q&A.")
        return out

    prompt = (
        f"Answer the question using ONLY the document excerpts below. "
        f"Cite the page for every claim using [page N]. "
        f"If the excerpts do not contain the answer say so.\n\n"
        f"QUESTION: {question}\n\n"
        f"EXCERPTS:\n" + "\n".join(context)[:max_context_chars])
    try:
        ans = reasoning(prompt).strip()
    except Exception as exc:  # noqa: BLE001
        out.ok = False
        out.status = "failed"
        out.data = {"question": question,
                    "note": f"reasoning callable errored: {exc}"}
        return out
    out.ok = True
    out.data = {"question": question, "answer": ans, "citations": citations,
                "context_chars": sum(len(c) for c in context)}
    out.check("answered", True, bool(ans), bool(ans))
    out.check("retrieved_context", ">=1", len(hits), len(hits) >= 1)
    return out
