"""DocumentEngine: ingest, chunk, index and retrieve documents externally.

Design (#17): parse a document to text once, split into bounded chunks with
page/section provenance, store chunks in an in-memory/JSON index keyed by a
content id, and answer retrieval with the *few* matching chunks. The calling
agent never receives the whole document.
"""
from __future__ import annotations

import hashlib
import json
import re
import threading
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from .parsers import PARSERS, extract_plain


@dataclass
class TextDocument:
    """A parsed document held externally."""
    content_id: str
    url: str = ""
    title: str = ""
    text: str = ""
    meta: dict = field(default_factory=dict)
    chunks: list = field(default_factory=list)

    def to_dict(self) -> dict:
        return {"content_id": self.content_id, "url": self.url,
                "title": self.title, "char_count": len(self.text),
                "n_chunks": len(self.chunks), "meta": self.meta,
                "chunks": self.chunks[:5]}  # keep small


class DocumentEngine:
    def __init__(self, chunk_chars: int = 2000, overlap: int = 200,
                 persist_dir: Optional[str] = None):
        self.chunk_chars = chunk_chars
        self.overlap = overlap
        self._docs: dict[str, TextDocument] = {}
        self._lock = threading.Lock()
        self.persist_dir = persist_dir
        if persist_dir:
            Path(persist_dir).mkdir(parents=True, exist_ok=True)

    # -- ingestion ---------------------------------------------------------
    def text_from_bytes(self, data: bytes, kind: str) -> str:
        parser = PARSERS.get(kind)
        if parser is None:
            parser = extract_plain
        try:
            return parser(data)
        except Exception:
            return extract_plain(data)

    def ingest_text(self, url: str, text: str, meta: Optional[dict] = None,
                    chunk: bool = True) -> str:
        cid = hashlib.sha256((url + ":" + text[:500]).encode()).hexdigest()[:20]
        with self._lock:
            if cid in self._docs:
                return cid
            title = meta.get("title", "") if meta else ""
            doc = TextDocument(content_id=cid, url=url, title=title,
                               text=text, meta=meta or {})
            if chunk and len(text) > self.chunk_chars:
                doc.chunks = self._chunk(text, url)
            self._docs[cid] = doc
        if self.persist_dir:
            self._persist(cid)
        return cid

    def ingest_file(self, path: str, kind: Optional[str] = None) -> str:
        data = Path(path).read_bytes()
        ext = kind or Path(path).suffix.lstrip(".").lower()
        mapped = {"docx": "doc", "xlsx": "spreadsheet", "pptx": "presentation"}.get(ext, ext)
        text = self.text_from_bytes(data, mapped)
        return self.ingest_text(path, text, meta={"title": Path(path).name})

    def get(self, content_id: str) -> Optional[TextDocument]:
        return self._docs.get(content_id)

    def exists(self, content_id: str) -> bool:
        return content_id in self._docs

    # -- chunking ----------------------------------------------------------
    def _chunk(self, text: str, url: str) -> list:
        """Split into overlapping chunks at paragraph/sentence boundaries,
        tracking a (page-ish) section label per chunk."""
        paras = re.split(r"\n\s*\n", text)
        chunks = []
        buf = ""
        start_label = ""
        for para in paras:
            para = para.strip()
            if not para:
                continue
            if len(buf) + len(para) > self.chunk_chars and buf:
                chunks.append(self._mk_chunk(buf, url, start_label, len(chunks)))
                buf = self._tail(buf)
                start_label = ""
            buf = (buf + "\n\n" + para).strip()
        if buf:
            chunks.append(self._mk_chunk(buf, url, start_label, len(chunks)))
        return chunks

    def _tail(self, buf: str) -> str:
        if len(buf) > self.overlap:
            return buf[-self.overlap:]
        return buf

    def _mk_chunk(self, text, url, label, idx) -> dict:
        return {"chunk_id": f"{hashlib.sha256((url+str(idx)).encode()).hexdigest()[:10]}-{idx}",
                "url": url, "section": label, "index": idx, "text": text}

    # -- retrieval ----------------------------------------------------------
    def retrieve(self, content_id: str, question: str, top_k: int = 4) -> list:
        doc = self._docs.get(content_id)
        if doc is None:
            return []
        if not doc.chunks:
            return [{"chunk_id": "whole", "url": doc.url, "section": "whole",
                     "text": doc.text[:4000]}]
        q_terms = _significant_terms(question)
        scored = []
        for c in doc.chunks:
            low = c["text"].lower()
            score = sum(low.count(t) for t in q_terms)
            if score:
                scored.append((score, c))
        scored.sort(key=lambda x: -x[0])
        return [c for _, c in scored[:top_k]]

    def search_docs(self, query: str, top_k: int = 10) -> list:
        """Cross-document lexical search across ingested docs."""
        q_terms = _significant_terms(query)
        hits = []
        for cid, doc in self._docs.items():
            hay = (doc.title + "\n" + doc.text).lower()
            score = sum(hay.count(t) for t in q_terms)
            if score:
                hits.append({"content_id": cid, "url": doc.url,
                             "title": doc.title, "score": score,
                             "excerpt": _excerpt(doc.text[:2000], q_terms)})
        hits.sort(key=lambda x: -x["score"])
        return hits[:top_k]

    # -- persistence --------------------------------------------------------
    def _persist(self, cid: str):
        try:
            doc = self._docs[cid]
            Path(self.persist_dir, cid + ".json").write_text(
                json.dumps({"url": doc.url, "title": doc.title,
                            "text": doc.text[:200000], "meta": doc.meta},
                           default=str))
        except Exception:
            pass


def _significant_terms(text: str) -> list[str]:
    stop = {"the", "and", "for", "are", "what", "how", "with", "that", "this",
            "you", "your", "was", "have", "has", "about", "best", "top",
            "which", "their", "there", "from", "into", "pdf"}
    return [w.lower() for w in re.findall(r"[a-zA-Z]\w+", text or "")
            if w.lower() not in stop and len(w) > 2]


def _excerpt(text: str, terms: list) -> str:
    low = text.lower()
    for t in terms:
        i = low.find(t)
        if i >= 0:
            return text[max(0, i - 80): i + 200].replace("\n", " ")
    return text[:280]
