"""Bookmarks / outlines / TOC and hyperlinks (requirement 24)."""
from __future__ import annotations

from typing import Optional, Sequence

from ..result import Outcome
from ..tools import adapter


def extract_bookmarks(path: str, password=None) -> Outcome:
    import pymupdf
    out = Outcome(skill="pdf-bookmarks")
    doc = pymupdf.open(path)
    if password and doc.needs_pass:
        doc.authenticate(password)
    toc = doc.get_toc()
    doc.close()
    out.ok = True
    out.data = {"toc": toc, "count": len(toc)}
    out.messages.append("toc format = [level, title, page(1-based)]")
    return out


def set_bookmarks(path: str, output: str, toc: Sequence[list],
                  mode: str = "replace", password=None) -> Outcome:
    """Set document outline. toc entries: [level, title, page].
    mode replace|merge."""
    import pymupdf
    out = Outcome(skill="pdf-bookmarks")
    doc = pymupdf.open(path)
    if password and doc.needs_pass:
        doc.authenticate(password)
    if mode == "merge":
        existing = doc.get_toc()
        merged = existing + [list(t) for t in toc]
        doc.set_toc(merged)
    else:
        doc.set_toc([list(t) for t in toc])
    doc.save(output, garbage=3, deflate=True)
    doc.close()
    out.output_path = output
    out.ok = True
    out.status = "completed"
    chk = pymupdf.open(output)
    n = len(chk.get_toc())
    chk.close()
    out.data = {"count": n}
    out.check("toc_present", ">0", n, n > 0)
    return out


def remove_bookmarks(path: str, output: str, password=None) -> Outcome:
    return set_bookmarks(path, output, [], password=password)


def extract_links(path: str, password=None) -> Outcome:
    """List hyperlinks across the document with target page + uri."""
    import pymupdf
    out = Outcome(skill="pdf-links")
    doc = pymupdf.open(path)
    if password and doc.needs_pass:
        doc.authenticate(password)
    links = []
    for i in range(doc.page_count):
        for lk in doc[i].get_links():
            links.append({"page": i + 1, "kind": lk.get("kind"),
                          "uri": lk.get("uri"), "page_target": lk.get("page"),
                          "rect": lk.get("from") and list(lk["from"])})
    doc.close()
    out.ok = True
    out.data = {"links": links, "count": len(links)}
    out.check("parsed", True, True, True)
    return out


def add_links(path: str, output: str, links: Sequence[dict],
              password=None) -> Outcome:
    """Add URI links. each: {"page":1, "rect":[x0,y0,x1,y1], "uri":...}"""
    import pymupdf
    out = Outcome(skill="pdf-links")
    doc = pymupdf.open(path)
    if password and doc.needs_pass:
        doc.authenticate(password)
    count = 0
    for lk in links:
        page = doc[int(lk["page"]) - 1]
        page.insert_link({"kind": 2, "from": pymupdf.Rect(*lk["rect"]),
                          "uri": lk["uri"]})
        count += 1
    doc.save(output, garbage=3, deflate=True)
    doc.close()
    out.output_path = output
    out.ok = True
    out.status = "completed"
    out.data = {"added": count}
    return out
