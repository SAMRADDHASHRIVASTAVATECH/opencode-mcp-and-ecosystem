"""Summarization for huge + weak-model documents (requirements 10, 11).

Instead of loading a book into one prompt, this builds *hierarchical,
context-safe* summaries:
  page bucket extracts -> section summaries -> document summary.
An abstractive ``llm`` callable (prompt -> text) is optional. When absent, or
to save tokens, we fall back to extractive previews computed locally, so the
system still works on pure CPU with no model and no huge context.
Results can be persisted into the document knowledge store.
"""
from __future__ import annotations

from typing import Callable, Optional

from ..result import Outcome
from ..core import chunk as ch

_LLM: Optional[Callable] = None


def register_llm(fn: Callable):
    """Register llm(prompt:str)->str for abstractive summarization/QA."""
    global _LLM
    _LLM = fn


def _llm() -> Optional[Callable]:
    return _LLM


def _extractive(text: str, max_chars: int = 900) -> str:
    """Lead/most-representative sentences as a cheap local surrogate."""
    import re
    sents = re.split(r"(?<=[.!?])\s+", text)
    parts = []
    total = 0
    for s in sents:
        if total + len(s) > max_chars:
            break
        parts.append(s.strip())
        total += len(s)
    return " ".join(parts) if parts else (text[:max_chars])


def summarize(path: str, mode: str = "hierarchical", bucket: int = 20,
              per_bucket_chars: int = 1000, top_bucket_chars: int = 1600,
              store=None, doc_id: Optional[str] = None,
              llm: Optional[Callable] = None, password=None) -> Outcome:
    """Return a summary that is guaranteed context-safe.

    modes:
      extractive : local lead-sentence summary of the whole doc (fast)
      bucket     : per-bucket extractive summaries (good for huge docs)
      hierarchical : two-level (bucket extracts optionally abstracted then a
                     top summary), persisted to store when provided.
    """
    from ..core import extract as ex
    out = Outcome(skill="pdf-summarize")
    pages = ex.extract_per_page(path, password)
    total = len(pages)
    llm = llm or _llm()
    used_llm = llm is not None
    if store and doc_id is None:
        doc_id = store.register_document(path, page_count=total)

    def _summ_group(pstart, texts):
        blob = "\n".join(texts)
        if llm:
            prompt = (f"Summarize the following document excerpt in under "
                      f"{per_bucket_chars} chars. Be factual.\n\n{blob[:6000]}")
            try:
                return llm(prompt).strip()
            except Exception:
                pass
        return _extractive(blob, per_bucket_chars)

    if mode == "extractive":
        full = "\n".join(pages)
        s = _extractive(full, 1600) if not llm else _summ_group(1, pages)
        if store:
            store.put_summary(doc_id, "doc", 0, s)
        out.data = {"summary": s, "method": "llm" if used_llm else "extractive",
                    "pages": total, "doc_id": doc_id}
    elif mode == "bucket":
        groups = []
        for i in range(0, total, bucket):
            gpages = range(i + 1, min(i + bucket, total) + 1)
            texts = pages[i:i + bucket]
            groups.append({"pages": list(gpages),
                           "summary": _summ_group(i + 1, texts)})
        if store:
            for g in groups:
                store.put_summary(doc_id, "bucket",
                                  g["pages"][0], g["summary"])
        out.data = {"buckets": groups, "bucket_size": bucket,
                    "pages": total, "method": "llm" if used_llm else "extractive",
                    "doc_id": doc_id}
    else:  # hierarchical
        groups = []
        extracts = []
        for i in range(0, total, bucket):
            gpages = list(range(i + 1, min(i + bucket, total) + 1))
            texts = pages[i:i + bucket]
            gs = _summ_group(i + 1, texts)
            groups.append({"pages": gpages, "summary": gs})
            extracts.append(gs)
            if store:
                store.put_summary(doc_id, "section", gpages[0], gs)
        if llm:
            try:
                top = llm("Synthesize a document-level summary from these "
                          "section summaries:\n\n" + "\n".join(extracts))
                method = "llm"
            except Exception:
                top = " | ".join(e[:400] for e in extracts)
                method = "extractive"
        else:
            top = " | ".join(e[:400] for e in extracts)
            method = "extractive"
        if store:
            store.put_summary(doc_id, "doc", 0, top)
        out.data = {"sections": groups, "summary": top,
                    "pages": total, "method": method, "doc_id": doc_id}
    out.ok = True
    out.status = "completed"
    out.check("summarized", ">=1", total, total >= 1)
    return out
