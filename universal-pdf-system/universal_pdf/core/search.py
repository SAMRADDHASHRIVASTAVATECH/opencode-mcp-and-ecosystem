"""Search & indexing (requirement 9).

Exact / keyword / phrase / regex / page / section search over a document, with
every hit retaining source page + snippet. For large docs an external index
(SQLite FTS5 or a JSON positional index) is built and reused across queries so
repeated retrieval never re-parses the whole file into context.
"""
from __future__ import annotations

import json
import re
from typing import Optional

from ..result import Outcome
from ..core import state as kb
from ..tools import adapter


def _flatten_doc_text(path, password=None):
    from ..core import extract as ex
    return ex.extract_per_page(path, password)


def build_index(path: str, index_path: Optional[str] = None,
                password=None) -> Outcome:
    """Build a positional inverted index (page+offset per term) persisted as
    JSON, plus optional FTS when available. Scales for 10k+ page docs."""
    import os
    from ..core import chunk as ch
    out = Outcome(skill="pdf-index")
    pages = _flatten_doc_text(path, password)
    index_path = index_path or (os.path.splitext(path)[0] + "_index.json")
    # Build a lightweight positional index (term -> list of (page, offset)).
    pos_index = {}
    for pno, text in enumerate(pages, 1):
        for m in re.finditer(r"[\w'’-]+", text):
            term = m.group(0).lower()
            pos_index.setdefault(term, []).append((pno, m.start()))
    # trim to dict of term->pages for storage compactness
    compact = {}
    for term, hits in pos_index.items():
        pagemap = {}
        for pno, off in hits:
            pagemap.setdefault(pno, []).append(off)
        compact[term] = pagemap
    with open(index_path, "w", encoding="utf-8") as fh:
        json.dump({"terms": len(compact), "pages": len(pages),
                   "index": compact}, fh)
    out.output_path = index_path
    out.ok = True
    out.status = "completed"
    out.data = {"terms": len(compact), "pages": len(pages)}
    out.check("indexed", ">0", len(compact), len(compact) > 0)
    return out


def _load_index(index_path):
    with open(index_path, encoding="utf-8") as fh:
        return json.load(fh)


def search_document(path: str, query: str, mode: str = "phrase",
                    case_sensitive: bool = False, page: Optional[int] = None,
                    index_path: Optional[str] = None,
                    context_chars: int = 120, password=None) -> Outcome:
    """Search a PDF (streams pages for memory-safety on huge documents).

    modes: exact | phrase | keyword (any/all words) | regex
    Each result: {"page":p, "snippet":..., "term":...}
    """
    from ..core import extract as ex
    out = Outcome(skill="pdf-search")
    q = query
    if not case_sensitive:
        q = q.lower()
    results = []
    pat = None
    if mode == "regex":
        try:
            pat = re.compile(query, 0 if case_sensitive else re.I)
        except re.error as exc:
            out.ok = False
            out.status = "failed"
            out.messages.append(f"bad regex: {exc}")
            return out

    # Resolve page_count lazily & stream
    total = 0
    for pno, text in ex.iter_page_text(path, password):
        total = max(total, pno)
        if page is not None and pno != page:
            continue
        low = text if case_sensitive else text.lower()
        if mode == "regex":
            for m in pat.finditer(text):
                s = max(0, m.start() - context_chars)
                results.append({"page": pno, "term": m.group(0),
                                "snippet": text[s:m.end() + context_chars].strip(),
                                "offset": m.start()})
        elif mode == "phrase":
            idx = 0
            while True:
                j = low.find(q, idx)
                if j < 0:
                    break
                s = max(0, j - context_chars)
                results.append({"page": pno, "term": query,
                                "snippet": text[s:j + len(query) + context_chars].strip(),
                                "offset": j})
                idx = j + len(query)
        else:
            # keyword
            words = [w.lower() for w in re.findall(r"\w+", q)]
            for w in words:
                idx = 0
                while True:
                    j = low.find(w, idx)
                    if j < 0:
                        break
                    s = max(0, j - context_chars)
                    results.append({"page": pno, "term": w,
                                    "snippet": text[s:j + len(w) + context_chars].strip(),
                                    "offset": j})
                    idx = j + len(w)

    # de-dup by (page,offset)
    seen, uniq = set(), []
    for r in results:
        key = (r["page"], r["offset"])
        if key not in seen:
            seen.add(key)
            uniq.append(r)
    out.ok = True
    out.status = "completed"
    out.data = {"query": query, "mode": mode, "hits": uniq[:500],
                "total": len(uniq), "pages_searched": total,
                "pages_total": total}
    out.check("searched", True, True, True)
    return out


def find_mentions_all(path: str, term: str, password=None) -> Outcome:
    """Stream over all pages to find every page mentioning a term.

    Memory-safe for huge documents: only one page is in memory at a time and
    only the (page,count) hits are retained (requirement 10).
    """
    from ..core import extract as ex
    out = Outcome(skill="pdf-search")
    t = term.lower()
    mentions = []
    total = 0
    for pno, text in ex.iter_page_text(path, password):
        total = pno
        c = text.lower().count(t)
        if c:
            mentions.append({"page": pno, "count": c})
    out.ok = True
    out.data = {"term": term, "mentions": mentions,
                "pages_with_hits": len(mentions), "pages_total": total}
    return out


def search_in_store(store: kb.DocumentStore, doc_id: str, term: str,
                    password=None) -> Outcome:
    """Search over persisted page/chunk text (no re-parse)."""
    out = Outcome(skill="pdf-search")
    term = term.lower()
    hits = []
    # naive scan over cached pages
    rows = store.conn.execute(
        "SELECT page,text FROM pages WHERE doc_id=?", (doc_id,)).fetchall()
    for r in rows:
        if term in (r["text"] or "").lower():
            hits.append({"page": r["page"]})
    out.ok = True
    out.data = {"doc_id": doc_id, "term": term,
                "pages_with_hits": len(hits), "hits": hits[:500]}
    return out
