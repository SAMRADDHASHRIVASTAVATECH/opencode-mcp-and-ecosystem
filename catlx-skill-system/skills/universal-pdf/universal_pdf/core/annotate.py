"""Watermark / stamp / header / footer / page numbers / annotations / redaction.

Preferred tool: PyMuPDF vector drawing (text and shape annotations are placed
as real annotations or overlaid content so they render and search correctly).
True content-bearing redaction removes underlying text (PyMuPDF ``add_redact_annot``
+ ``apply_redactions``) rather than merely painting over it.
"""
from __future__ import annotations

from typing import Optional, Sequence

from ..result import Outcome
from ..tools import adapter
from ..core import validation as V


def _open(path, password=None):
    import pymupdf
    doc = pymupdf.open(path)
    if password and doc.needs_pass:
        doc.authenticate(password)
    return doc


def _pc(path):
    import pymupdf
    d = pymupdf.open(path)
    n = d.page_count
    d.close()
    return n


# ----------------------------------------------------------------- watermark
def add_watermark(path: str, output: str, text: Optional[str] = None,
                  image: Optional[str] = None, rotation: float = 45.0,
                  opacity: float = 0.2, pages: Optional[list] = None,
                  fontsize: float = 60, color: tuple = (0.6, 0.6, 0.6),
                  scale_to_fit: bool = True, password=None) -> Outcome:
    """Add diagonal text or image watermark across selected pages.

    The overlay is authored with reportlab (arbitrary-angle canvas rotation)
    and stamped onto each page via PyMuPDF at the requested opacity.
    """
    out = Outcome(skill="pdf-watermark")
    doc = _open(path, password)
    total = doc.page_count
    pageset = set(pages) if pages else set(range(1, total + 1))
    overlay_path = _make_watermark_page(doc, text, image, rotation, fontsize,
                                        color, scale_to_fit)
    if overlay_path is None:
        doc.close()
        out.ok = False
        out.status = "failed"
        out.messages.append("provide text or image watermark")
        return out
    import os
    import pymupdf
    overlay_doc = None
    try:
        overlay_doc = pymupdf.open(overlay_path)
        for pno in sorted(pageset):
            target = doc[pno - 1]
            target.show_pdf_page(target.rect, overlay_doc, 0, overlay=opacity)
        doc.save(output, garbage=3, deflate=True)
        doc.close()
        out.output_path = output
        out.ok = True
        out.status = "completed"
        out.data = {"pages": sorted(pageset)}
        out.check("page_count", total, _pc(output), _pc(output) == total)
        return out
    except Exception as exc:  # noqa: BLE001
        try:
            doc.close()
        except Exception:
            pass
        out.ok = False
        out.status = "failed"
        out.messages.append(f"watermark failed: {exc}")
        return out
    finally:
        if overlay_doc:
            overlay_doc.close()
        try:
            os.remove(overlay_path)
        except Exception:
            pass


def _make_watermark_page(doc, text, image, rotation, fontsize, color,
                         scale_to_fit):
    """Author a single-page overlay watermark PDF using reportlab canvas so
    arbitrary (e.g. 45 degree) rotation is possible."""
    import os, tempfile
    from reportlab.pdfgen import canvas as rlcanvas
    from reportlab.lib.units import inch
    r = doc[0].rect
    w, h = r.width, r.height
    tmp = tempfile.NamedTemporaryFile(suffix=".pdf", delete=False)
    tmp.close()
    c = rlcanvas.Canvas(tmp.name, pagesize=(w, h))
    if text:
        from reportlab.lib.colors import Color
        if color and max(color) > 1:
            color = tuple(v / 255.0 for v in color)
        col = Color(*color) if color else Color(0.6, 0.6, 0.6)
        fs = fontsize
        # rough fit: scale so watermark spans document nicely
        if scale_to_fit:
            fs = min(fs, max(14, (w * 0.5) / max(8, len(text)) * 4))
        c.saveState()
        c.translate(w / 2, h / 2)
        c.rotate(rotation)
        c.setFillColor(col)
        c.setFont("Helvetica", fs)
        tw = c.stringWidth(text, "Helvetica", fs)
        c.drawCentredString(0, 0, text)
        c.restoreState()
    if image:
        c.drawImage(image, w * 0.15, h * 0.40, width=w * 0.7,
                    height=h * 0.2, preserveAspectRatio=True, mask="auto")
    c.showPage()
    c.save()
    return tmp.name


def add_stamp(path: str, output: str, text: str,
              position: str = "center", pages: Optional[list] = None,
              fontsize: float = 48, color: tuple = (1, 0, 0),
              opacity: float = 0.4, rotation: float = 0,
              stamp_type: str = "text", password=None) -> Outcome:
    """Add a (usually opaque) stamp overlay, e.g. APPROVED / CONFIDENTIAL."""
    import pymupdf
    out = Outcome(skill="pdf-watermark")
    doc = _open(path, password)
    total = doc.page_count
    pageset = set(pages) if pages else set(range(1, total + 1))
    boxmap = {"center": (0.3, 0.42), "topleft": (0.05, 0.05),
              "topright": (0.7, 0.05), "bottomleft": (0.05, 0.8),
              "bottomright": (0.7, 0.8)}
    try:
        for pno in sorted(pageset):
            page = doc[pno - 1]
            fr = page.rect
            xf, yf = boxmap.get(position, boxmap["center"])
            fs = fontsize
            # red bordered stamp
            x = fr.x0 + fr.width * xf
            y = fr.y0 + fr.height * yf
            page.insert_textbox(pymupdf.Rect(x, y, x + fr.width * 0.35,
                                             y + fr.height * 0.15),
                                text, fontsize=fs, fontname="hebo",
                                color=color, rotate=int(rotation),
                                align=pymupdf.TEXT_ALIGN_CENTER)
        doc.save(output, garbage=3, deflate=True)
        doc.close()
        out.output_path = output
        out.ok = True
        out.status = "completed"
        out.data = {"position": position, "pages": sorted(pageset)}
        out.check("page_count", total, _pc(output), _pc(output) == total)
        return out
    except Exception as exc:  # noqa: BLE001
        try:
            doc.close()
        except Exception:
            pass
        out.ok = False
        out.status = "failed"
        out.messages.append(f"stamp failed: {exc}")
        return out


# ---------------------------------------------------------- header/footer/pn
def add_header_footer(path: str, output: str, header: Optional[str] = None,
                      footer: Optional[str] = None, page_numbers: bool = True,
                      start_number: int = 1, skip_first: bool = False,
                      pages: Optional[list] = None, fontsize: float = 9,
                      color: tuple = (0.35, 0.35, 0.35), password=None) -> Outcome:
    """Overlay running headers/footers and page numbers on selected pages."""
    out = Outcome(skill="pdf-header-footer")
    doc = _open(path, password)
    total = doc.page_count
    pageset = set(pages) if pages else set(range(1, total + 1))
    try:
        for pno in sorted(pageset):
            if skip_first and pno == 1:
                continue
            page = doc[pno - 1]
            fr = page.rect
            m = 28  # 10pt margin
            if header:
                page.insert_text((m, fr.y0 + m), header,
                                 fontsize=fontsize, fontname="helv",
                                 color=color)
            if page_numbers:
                num = start_number + (pno - 1)
                page.insert_text((fr.x1 - m - 20, fr.y1 - m), str(num),
                                 fontsize=fontsize, fontname="helv",
                                 color=color)
            if footer:
                page.insert_text((m, fr.y1 - m), footer,
                                 fontsize=fontsize, fontname="helv",
                                 color=color)
        doc.save(output, garbage=3, deflate=True)
        doc.close()
        out.output_path = output
        out.ok = True
        out.status = "completed"
        out.data = {"header": header, "footer": footer,
                    "page_numbers": page_numbers}
        out.check("page_count", total, _pc(output), _pc(output) == total)
        return out
    except Exception as exc:  # noqa: BLE001
        try:
            doc.close()
        except Exception:
            pass
        out.ok = False
        out.status = "failed"
        out.messages.append(f"header/footer failed: {exc}")
        return out


# ---------------------------------------------------------------- annotations
ANNOT_TYPES = {"highlight", "underline", "strikeout", "text", "freetext",
               "square", "circle", "line", "arrow", "stamp", "link", "squiggly"}


def add_annotations(path: str, output: str, annotations: list[dict],
                    password=None) -> Outcome:
    """Add annotations.

    Each annotation dict:
      {"type": "highlight", "page":1, "rect":[x0,y0,x1,y1],
       "color":(1,1,0), "text": ...}
      {"type":"text", "page":1, "rect":[..], "text":"note"}
      {"type":"freetext","page":1,"rect":[..],"text":"..."}
      {"type":"square|circle|line|arrow", "page":1, "rect":[...], "color":..}
      {"type":"link","page":1,"rect":[...],"uri":"..."}
    """
    out = Outcome(skill="pdf-annotate")
    doc = _open(path, password)
    try:
        count = 0
        for a in annotations:
            at = a.get("type")
            if at not in ANNOT_TYPES:
                continue
            page = doc[int(a.get("page", 1)) - 1]
            rect = a.get("rect")
            if rect:
                from pymupdf import Rect as R
                r = R(*rect)
            if at in ("highlight", "underline", "strikeout", "squiggly"):
                annot = page.add_highlight_annot(r) if at == "highlight" else \
                        page.add_underline_annot(r) if at == "underline" else \
                        page.add_strikeout_annot(r) if at == "strikeout" else \
                        page.add_squiggly_annot(r)
                annot.set_colors(stroke=a.get("color", (1, 1, 0)))
                if a.get("text"):
                    annot.set_info(content=a["text"])
                annot.update()
            elif at == "text":
                annot = page.add_text_annot(r.tl, a.get("text", ""))
                annot.update()
            elif at == "freetext":
                annot = page.add_freetext_annot(r, a.get("text", ""),
                                                fontsize=a.get("fontsize", 12),
                                                text_color=a.get("color", (0, 0, 0)))
                annot.update()
            elif at in ("square", "circle"):
                annot = (page.add_rect_annot(r) if at == "square"
                         else page.add_circle_annot(r))
                annot.set_colors(stroke=a.get("color", (1, 0, 0)),
                                 fill=a.get("fill", None))
                annot.update()
            elif at in ("line", "arrow"):
                pt1 = (r.x0, r.y0)
                pt2 = (r.x1, r.y1)
                annot = (page.add_line_annot(pt1, pt2) if at == "line"
                         else page.add_polyline_annot([pt1, pt2]))
                if at == "arrow":
                    annot.set_border(width=1.2)
                annot.set_colors(stroke=a.get("color", (0, 0, 1)))
                annot.update()
            elif at == "link":
                page.insert_link({"kind": 2, "from": r,
                                  "uri": a.get("uri", "")})
            count += 1
        doc.save(output, garbage=3, deflate=True)
        doc.close()
        out.output_path = output
        out.ok = True
        out.status = "completed"
        out.data = {"added": count}
        out.check("added", len(annotations), count, count > 0)
        return out
    except Exception as exc:  # noqa: BLE001
        try:
            doc.close()
        except Exception:
            pass
        out.ok = False
        out.status = "failed"
        out.messages.append(f"annotate failed: {exc}")
        return out


# ------------------------------------------------------------------ redaction
def redact_text(path: str, output: str, terms: Optional[list[str]] = None,
                rects: Optional[list[dict]] = None,
                fill: tuple = (0, 0, 0), remove_metadata: bool = True,
                password=None) -> Outcome:
    """True redaction: remove underlying text (and optionally regions), not
    merely paint over. ``terms`` = case-insensitive strings to wipe from the
    text layer. ``rects`` = [{"page":1,"rect":[x0,y0,x1,y1]}].
    After applying, validation re-checks that the terms can no longer be
    extracted (requirement 35 redaction verification).
    """
    out = Outcome(skill="pdf-redact")
    doc = _open(path, password)
    found = 0
    try:
        # 1) region redaction
        for rspec in (rects or []):
            page = doc[int(rspec["page"]) - 1]
            from pymupdf import Rect as R
            page.add_redact_annot(R(*rspec["rect"]), fill=fill)
        # 2) text redaction via searching (covers all occurrences & wrapped text)
        hits = []
        if terms:
            for i in range(doc.page_count):
                page = doc[i]
                for term in terms:
                    # search_for is case-insensitive and returns every occurrence
                    rl = page.search_for(term, quads=False)
                    for r in rl:
                        page.add_redact_annot(r, fill=fill)
                        hits.append(r)
                        found += 1
        for pno in range(doc.page_count):
            doc[pno].apply_redactions()
        # metadata strip
        if remove_metadata:
            doc.set_metadata({})
        doc.save(output, garbage=3, deflate=True)
        doc.close()

        # validation: ensure terms no longer extractable
        out.output_path = output
        check_ok = True
        leaked = []
        if terms:
            d2 = _open(output)
            full = "".join(d2[i].get_text() for i in range(d2.page_count)).lower()
            d2.close()
            for term in terms:
                if term.lower() in full:
                    check_ok = False
                    leaked.append(term)
        out.ok = True
        out.status = "completed"
        out.data = {"terms_redacted": len(terms or []),
                    "regions_redacted": len(rects or []),
                    "hits": found, "leaked_terms": leaked}
        out.check("underlying_content_removed", "no leak", not leaked,
                  not leaked, f"leaked={leaked}")
        return out
    except Exception as exc:  # noqa: BLE001
        try:
            doc.close()
        except Exception:
            pass
        out.ok = False
        out.status = "failed"
        out.messages.append(f"redaction failed: {exc}")
        return out
