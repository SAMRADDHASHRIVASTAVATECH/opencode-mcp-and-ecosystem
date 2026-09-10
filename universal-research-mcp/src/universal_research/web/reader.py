"""WebReader: fetch a URL and extract readable content (#15).

Returned as a Source whose heavy content lives in an external content_id and is
chunked/indexed; the model only gets compact fields + a short excerpt.
Handles HTML (main content + headings + links), plain text, markdown, and
delegates office/PDF documents to the documents engine by content type.
"""
from __future__ import annotations

import hashlib
import re
import urllib.parse
from typing import Optional

from .. import network, security
from ..errors import ProviderError
from ..models import Source


def _clean(t) -> str:
    return re.sub(r"\s+", " ", (t or "")).strip()


class WebReader:
    def __init__(self, settings=None, cache=None, doc_engine=None,
                 offline: bool = False):
        self.settings = settings
        self.cache = cache
        self.doc_engine = doc_engine
        self.offline = offline

    def fetch(self, url: str, *, timeout: Optional[int] = None) -> Source:
        s = self.settings
        if self.offline:
            return self._mock_fetch(url)
        cache_key = f"fetch:{url}"
        if self.cache:
            hit = self.cache.get(cache_key, ns="source")
            if hit:
                return self._source_from_cache(hit)
        security.validate_url(url, s)
        resp = network.fetch_capped(url, timeout=timeout)
        if resp.status_code != 200:
            raise ProviderError(f"HTTP {resp.status_code} for {url}")
        final_url = resp.url or url
        ctype = resp.headers.get("content-type", "")
        raw = resp.read_capped()
        source = Source(url=url, final_url=final_url, status=resp.status_code,
                        content_type=ctype.split(";")[0].strip().lower(),
                        size_bytes=len(raw))
        # classify may need content sniffing when ctype generic
        source.source_type = self._classify(final_url, ctype, raw)
        text = self._extract(source, raw)
        source.analysis["char_count"] = len(text)
        source.analysis["excerpt"] = _clean(text)[:800]
        # external storage via doc engine
        if self.doc_engine is not None:
            cid = self.doc_engine.ingest_text(url, text, meta={"title": source.title})
            source.content_id = cid
            source.analysis["content_indexed"] = True
        else:
            source.content_id = hashlib.sha256(text.encode()).hexdigest()[:16]
            source.analysis["content_indexed"] = False
        if self.cache:
            self.cache.put(cache_key, source.to_dict(include_heavy=False),
                           ns="source")
        return source

    def _mock_fetch(self, url: str) -> Source:
        """Deterministic offline fetch used when UR_OFFLINE=1 (no network)."""
        import re as _re
        host = re.sub(r"[^A-Za-z0-9]", " ", url).strip() or "page"
        source = Source(url=url, final_url=url, status=200,
                        content_type="text/html",
                        size_bytes=0)
        source.source_type = "web"
        source.title = f"Mock {host.title()} (offline)"
        text = (f"This is deterministic offline content generated for the URL "
                f"{url}. It is produced by the mock reader so that fetching and "
                f"verification work without network access in offline mode.")
        source.analysis["char_count"] = len(text)
        source.analysis["excerpt"] = text[:800]
        source.headings = [f"Mock Heading for {url}"]
        source.content_id = hashlib.sha256(url.encode()).hexdigest()[:16]
        return source

    def _text_of(self, source: Source) -> str:
        return source.analysis.get("excerpt", "") or ""

    def _classify(self, url, ctype, raw) -> str:
        k = security.classify_url_type(url, ctype)
        if k != "web":
            return k
        # sniff
        head = raw[:512].lower()
        if b"%pdf" in head:
            return "pdf"
        if raw[:4] == b"PK\x03\x04":
            # could be docx/xlsx/pptx - refine later
            return "doc"
        return "web"

    def _extract(self, source: Source, raw: bytes) -> str:
        try:
            if source.source_type == "pdf":
                return self._read_pdf(raw)
            if source.source_type in ("doc", "spreadsheet", "presentation"):
                if self.doc_engine is not None:
                    return self.doc_engine.text_from_bytes(raw, source.source_type)
                return ""
            if source.source_type == "web":
                return self._read_html(source, raw)
            # data/plain
            return self._read_plain(source, raw)
        except Exception as exc:  # noqa: BLE001
            source.analysis["warning"] = f"parse issue: {exc}"
            return ""

    def _read_html(self, source, raw: bytes) -> str:
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(raw, "lxml")
        for tag in soup(["script", "style", "noscript", "svg", "nav",
                         "form", "iframe"]):
            tag.decompose()
        if soup.title:
            source.title = _clean(soup.title.get_text())
        canon = soup.find("link", rel="canonical")
        if canon and canon.get("href"):
            source.canonical_url = canon["href"]
        am = soup.find("meta", attrs={"name": "author"})
        if am and am.get("content"):
            source.author = am["content"]
        dm = soup.find("meta", attrs={"name": "date"}) or \
            soup.find("meta", attrs={"property": "article:published_time"})
        if dm and dm.get("content"):
            source.date = dm["content"]
        for tag in ("h1", "h2", "h3"):
            for h in soup.find_all(tag)[:30]:
                t = _clean(h.get_text())
                if t:
                    source.headings.append(t)
        links, seen = [], set()
        for a in soup.find_all("a", href=True):
            href = a["href"]
            if not href or href.startswith(("#", "javascript:", "mailto:")):
                continue
            try:
                abs_url = urllib.parse.urljoin(source.url, href)
            except Exception:
                continue
            if abs_url in seen:
                continue
            seen.add(abs_url)
            if len(links) >= 200:
                break
            links.append({"url": abs_url, "text": _clean(a.get_text())[:80]})
        source.links = links
        article = soup.find("article") or soup.body or soup
        return article.get_text("\n", strip=True)[:40000]

    def _read_plain(self, source, raw: bytes) -> str:
        try:
            text = raw.decode("utf-8", errors="replace")
        except Exception:
            text = ""
        lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
        if lines:
            source.title = source.title or lines[0][:200]
            source.headings = lines[1:20][:20]
        return text[:40000]

    def _read_pdf(self, raw: bytes) -> str:
        import io
        import pypdf
        reader = pypdf.PdfReader(io.BytesIO(raw))
        out = []
        for pg in reader.pages:
            try:
                out.append(pg.extract_text() or "")
            except Exception:
                continue
        return "\n".join(out)

    def _source_from_cache(self, d: dict) -> Source:
        src = Source(url=d.get("url", ""))
        for k in ("title", "canonical_url", "domain", "source_type",
                  "content_type", "author", "date", "retrieval_date",
                  "status", "final_url", "size_bytes", "content_id"):
            if k in d:
                setattr(src, k, d[k])
        src.headings = d.get("headings", [])
        src.analysis = d.get("analysis", {})
        return src
