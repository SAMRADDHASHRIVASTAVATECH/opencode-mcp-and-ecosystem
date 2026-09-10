"""Chunking for huge-document + small-context handling (requirements 10, 11).

Divides a document into small context-safe chunks that keep page & block
boundaries, so any given model only ever receives the few chunks it needs.
Results can be persisted to the knowledge store for later retrieval.
"""
from __future__ import annotations

from typing import Optional

from .. import config
from ..result import Outcome
from ..core import state as kb
from ..tools import adapter


def chunk_text(text: str, max_chars: int = None,
               overlap: int = None) -> list[str]:
    """Naive word-boundary chunker for a blob of text."""
    max_chars = max_chars or config.default_profile().chunk_chars
    overlap = overlap if overlap is not None else \
        config.default_profile().chunk_overlap_chars
    words = text.split()
    chunks, cur = [], []
    curlen = 0
    for w in words:
        if curlen + len(w) + 1 > max_chars and cur:
            chunks.append(" ".join(cur))
            # overlap tail
            keep = " ".join(cur)
            tail = keep[-overlap:] if overlap and len(keep) > overlap else ""
            cur = tail.split() if tail else []
            curlen = sum(len(x) + 1 for x in cur)
        cur.append(w)
        curlen += len(w) + 1
    if cur:
        chunks.append(" ".join(cur))
    return chunks


def chunk_document(path: str, per_page: bool = False,
                   max_chars: int = None, store_doc_id: Optional[str] = None,
                   page_store: Optional[kb.DocumentStore] = None,
                   password=None) -> Outcome:
    """Chunk a document.

    ``per_page=True`` => one chunk per page (good for paged provenance).
    Otherwise a rolling chunker over page text with page tags is used.
    When ``store_doc_id`` + ``page_store`` are given, chunks are persisted and
    page text cached so later retrieval needs no re-parse.
    """
    from ..core import extract as ex
    out = Outcome(skill="pdf-chunk")
    profile = config.default_profile()
    max_chars = max_chars or profile.chunk_chars
    pages_text = ex.extract_per_page(path, password)
    chunks = []
    store = page_store
    doc_id = store_doc_id
    try:
        if store is not None and doc_id is None:
            doc_id = store.register_document(path, page_count=len(pages_text))
        for idx, page_text in enumerate(pages_text, 1):
            if per_page:
                cid = f"chunk-{idx:05d}"
                chunks.append({"chunk_id": cid, "page": idx,
                               "start": 0, "text": page_text})
                if store:
                    store.put_page(doc_id, idx, page_text)
                    store.put_chunk(doc_id, cid, idx, 0, page_text)
            else:
                pieces = chunk_text(page_text, max_chars=max_chars,
                                    overlap=profile.chunk_overlap_chars)
                pos = 0
                for p in pieces:
                    cid = f"chunk-p{idx:03d}-{pos:06d}"
                    chunks.append({"chunk_id": cid, "page": idx,
                                   "start": pos, "text": p})
                    if store:
                        store.put_page(doc_id, idx, page_text)
                        store.put_chunk(doc_id, cid, idx, pos, p)
                    pos += len(p)
        if store and doc_id:
            store.mark(doc_id, "chunk", "completed", f"{len(chunks)} chunks")
        out.ok = True
        out.status = "completed"
        out.data = {"chunks": len(chunks), "per_page": per_page,
                    "pages": len(pages_text), "doc_id": doc_id}
        out.check("chunks", ">=1", len(chunks), len(chunks) >= 1)
        return out
    except Exception as exc:  # noqa: BLE001
        out.ok = False
        out.status = "failed"
        out.messages.append(f"chunking failed: {exc}")
        return out


def summarize_by_pages(pages_text: list[str], bucket: int = 20,
                       max_chars_per_summary: int = 1200) -> list[dict]:
    """Group pages into buckets and produce short extractive summaries that are
    context-safe (a surrogate for hierarchical summaries used by the LLM layer,
    which does the actual abstractive summarization on top of these).
    """
    summaries = []
    for i in range(0, len(pages_text), bucket):
        group = pages_text[i:i + bucket]
        pstart = i + 1
        text = "\n".join(group)
        # heuristic extractive: leading sentence(s) of each page + first line
        firsts = []
        for pg in group:
            lines = [l.strip() for l in pg.splitlines() if l.strip()]
            if lines:
                firsts.append(lines[0][:180])
        preview = " | ".join(firsts)
        summaries.append({"pages": list(range(pstart, i + len(group) + 1)),
                          "page_start": pstart, "char_count": len(text),
                          "preview": preview})
    return summaries
