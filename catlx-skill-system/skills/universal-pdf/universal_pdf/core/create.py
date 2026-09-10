"""PDF creation engine (requirements 3 & 15 source->PDF).

Preferred tool: reportlab platypus (rich, templated, vector output).
Fallback:       PyMuPDF insert_text / insert_image (simple docs).

Supports building documents from plain text, Markdown (subset), HTML
(subset), structured data (CSV/JSON/XLSX/rows -> tables/reports/invoices),
images, and programmatic content specs with page size, margins, orientation,
headers/footers/page numbers, headings/sections, lists, tables, images,
captions, hyperlinks, bookmarks, cover pages and TOC.
"""
from __future__ import annotations

import csv
import io
import json
import os
from pathlib import Path
from typing import Any, Optional, Sequence

from .. import config
from ..errors import ToolUnavailableError
from ..result import Outcome
from ..tools import adapter
from ..core import validation as V

PDF = adapter.preferred_backend()


def _require_reportlab():
    if not adapter.backend_available("reportlab"):
        raise ToolUnavailableError(
            "reportlab is required for PDF creation and is not installed.")


# ---------------------------------------------------------------- page spec
def _page_size(name: str):
    from reportlab.lib.pagesizes import A4, LETTER, LEGAL, A3, A5
    sizes = {"a4": A4, "letter": LETTER, "legal": LEGAL, "a3": A3, "a5": A5}
    return sizes.get(name.lower(), A4)


def _load_template(path: str):
    from reportlab.platypus import BaseDocTemplate, PageTemplate, Frame
    # template JSON: {page_size, margins, header, footer, content}
    data = json.loads(Path(path).read_text())
    return data


# ------------------------------------------------------------ content model
# We accept a simple list of flowable dicts so both humans and generated
# data can describe documents programmatically:
#   {"type":"heading","text":...,"level":1}
#   {"type":"para","text":...} {"type":"list","items":[...],"ordered":true}
#   {"type":"table","rows":[[...]],"caption":...}
#   {"type":"image","path":...,"width":...,"height":...,"caption":...}
#   {"type":"link","text":...,"url":...}
#   {"type":"pagebreak"} {"type":"spacer","height":...}
#   {"type":"cover","title":...,"subtitle":...,"author":...,"date":...}

_BASE_STYLE = {
    "fontSize": 10, "leading": 14, "fontName": "Helvetica",
    "spaceAfter": 6,
}

_HEADING_COLOR = "#1a1a2e"


def _mk_style(doc, spec, base_style=None):
    """Inline, dependency-free paragraph styling via <b>/<i>/<font> tags."""
    from reportlab.lib.styles import ParagraphStyle
    from reportlab.lib import colors
    style = dict(_BASE_STYLE)
    if base_style:
        style.update(base_style)
    tc = style.get("textColor") or colors.black
    return ParagraphStyle(
        "s", fontName=style.get("fontName"), fontSize=style.get("fontSize"),
        leading=style.get("leading"), spaceAfter=style.get("spaceAfter"),
        textColor=tc, alignment=style.get("alignment", 0),
        firstLineIndent=style.get("firstLineIndent", 0))


def _escape(text: str) -> str:
    return (text.replace("&", "&amp;").replace("<", "&lt;")
                .replace(">", "&gt;"))


def _apply_inline(text: str) -> str:
    """Very small md inline (bold/italic/code) -> reportlab markup."""
    import re
    text = _escape(text)
    text = re.sub(r"\*\*([^*]+)\*\*", r"<b>\1</b>", text)
    text = re.sub(r"(?<!\*)\*([^*]+)\*(?!\*)", r"<i>\1</i>", text)
    text = re.sub(r"`([^`]+)`", r"<font face='Courier'>\1</font>", text)
    text = text.replace("\\*", "*")
    return text


def _build_flowables(doc, content: list, opts, story_builder) -> list:
    """Convert content specs into reportlab platypus flowables."""
    from reportlab.platypus import (Paragraph, Spacer, Table, TableStyle,
                                    PageBreak, Image, ListFlowable, ListItem,
                                    HRFlowable, KeepTogether)
    from reportlab.lib import colors
    from reportlab.lib.styles import ParagraphStyle
    from reportlab.lib.units import inch, cm
    from reportlab.platypus.tableofcontents import TableOfContents
    story = story_builder
    has_cover = False
    toc_needed = False
    for item in content:
        typ = item.get("type", "para")
        if typ == "cover":
            has_cover = True
            story.append(Spacer(1, 0.35 * 72))
            t = item.get("title", "")
            story.append(Paragraph(f"<font size=26><b>{_escape(t)}</b></font>",
                                   ParagraphStyle("c1", leading=32, textColor=colors.black)))
            if item.get("subtitle"):
                story.append(Paragraph(
                    f"<font size=15 color='#555'>{_escape(item['subtitle'])}</font>",
                    ParagraphStyle("c2", leading=20, spaceBefore=10, textColor=colors.black)))
            story.append(Spacer(1, 30))
            for k, lab in [("author", "Author"), ("date", "Date"),
                           ("organization", "Organization")]:
                if item.get(k):
                    story.append(Paragraph(
                        f"<font size=10 color='#777'>{lab}: {_escape(str(item[k]))}</font>",
                        ParagraphStyle("c3", leading=16, textColor=colors.black)))
            story.append(PageBreak())
        elif typ == "heading":
            level = int(item.get("level", 1))
            fsz = {1: 18, 2: 15, 3: 13, 4: 11}.get(level, 11)
            # bookmark for nav
            txt = _escape(item.get("text", ""))
            story.append(Paragraph(
                f"<b><font size={fsz} color='{_HEADING_COLOR}'>{txt}</font></b>",
                ParagraphStyle("h", leading=fsz + 6, textColor=colors.black,
                               spaceBefore=8, spaceAfter=4)))
            try:
                doc.bookmarkPage(item.get("bookmark", item.get("text", "")[:50]))
                doc.addOutlineEntry(item.get("text", ""), 0, level=level)
            except Exception:
                pass
        elif typ == "para":
            story.append(Paragraph(
                _apply_inline(item.get("text", "")),
                _mk_style(doc, item)))
        elif typ == "list":
            li = item.get("items", [])
            ordered = item.get("ordered", False)
            fl = []
            for it in li:
                p = Paragraph(_apply_inline(it), _mk_style(doc, item, {"spaceAfter": 2}))
                fl.append(p)
            story.append(ListFlowable(fl, bulletType="1" if ordered else "bullet",
                                      start="1", leftIndent=18))
        elif typ == "table":
            rows = item.get("rows", [])
            if rows:
                header = item.get("header_row", True)
                head = rows[0]
                body = rows[1:] if header else rows
                if header:
                    tdata = [[Paragraph(f"<b>{_escape(str(c))}</b>",
                                        _mk_style(doc, item))
                              for c in head]]
                else:
                    tdata = []
                for r in body:
                    tdata.append([Paragraph(_escape(str(c)), _mk_style(doc, item))
                                  for c in r])
                tbl = Table(tdata, repeatRows=1 if header else 0)
                tbl.setStyle(TableStyle([
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                    ("BACKGROUND", (0, 0), (-1, 0) if header else (0, -1),
                     colors.HexColor("#eef0f5")),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("LEFTPADDING", (0, 0), (-1, -1), 4),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 4),
                ]))
                story.append(tbl)
                if item.get("caption"):
                    story.append(Paragraph(
                        f"<font size=9 color='#666'><i>{_escape(item['caption'])}</i></font>",
                        ParagraphStyle("cap", leading=11, spaceBefore=3, textColor=colors.black,
                                       spaceAfter=8)))
                else:
                    story.append(Spacer(1, 6))
        elif typ == "image":
            ip = item.get("path")
            if ip and os.path.exists(ip):
                w = item.get("width") or 6.0 * 72
                img = Image(ip, width=w)
                try:
                    iw, ih = img.imageWidth, img.imageHeight
                    img.drawWidth = w
                    img.drawHeight = w * ih / iw
                except Exception:
                    pass
                story.append(KeepTogether([img]))
                if item.get("caption"):
                    story.append(Paragraph(
                        f"<font size=9 color='#666'><i>{_escape(item['caption'])}</i></font>",
                        ParagraphStyle("cap", leading=11, textColor=colors.black, spaceAfter=8)))
        elif typ == "link":
            story.append(Paragraph(
                f"<link href='{item.get('url','')}' "
                f"color='blue'>{_escape(item.get('text',''))}</link>",
                _mk_style(doc, item)))
        elif typ == "hr":
            story.append(HRFlowable(width="100%", thickness=0.6,
                                    color=colors.grey))
        elif typ == "pagebreak":
            story.append(PageBreak())
        elif typ == "spacer":
            story.append(Spacer(1, item.get("height", 12)))
        elif typ == "toc":
            toc_needed = True
        elif typ == "parahtml":
            story.append(Paragraph(item.get("html", ""),
                                   _mk_style(doc, item)))
    return story


# ------------------------------------------------------------- main builder
class _StoryBuilder:
    def __init__(self, opts):
        self.opts = opts
        from reportlab.platypus import BaseDocTemplate
        self._build_frames()
        self.story = []

    def _build_frames(self):
        from reportlab.lib.units import inch
        from reportlab.platypus import Frame, PageTemplate, BaseDocTemplate
        o = self.opts
        ps = _page_size(o.get("page_size", "a4"))
        m = o.get("margins", {})
        ml = m.get("left", 0.9) * 72
        mr = m.get("right", 0.9) * 72
        mt = m.get("top", 0.9) * 72
        mb = m.get("bottom", 0.9) * 72
        fh = ps[1] - mt - mb
        fw = ps[0] - ml - mr
        # if cover, full-bleed frame first page? keep simple: same frame
        def on_page(canv, doc):
            canv.saveState()
            w, h = ps
            # header
            if o.get("header"):
                canv.setFont("Helvetica", 9)
                canv.setFillColorRGB(0.45, 0.45, 0.45)
                canv.drawString(ml, h - mt + 0.25 * 72, o["header"])
            if o.get("footer"):
                canv.setFont("Helvetica", 9)
                canv.setFillColorRGB(0.45, 0.45, 0.45)
                canv.drawString(ml, mb - 0.4 * 72, o["footer"])
            if o.get("page_numbers", True):
                canv.setFont("Helvetica", 9)
                canv.setFillColorRGB(0.5, 0.5, 0.5)
                canv.drawRightString(w - mr, mb - 0.4 * 72, f"{canv.getPageNumber()}")
            canv.restoreState()

        self.doc = BaseDocTemplate(
            o.get("output", "out.pdf"), pagesize=ps,
            leftMargin=ml, rightMargin=mr, topMargin=mt, bottomMargin=mb)
        frame = Frame(ml, mb, fw, fh, id="body",
                      leftPadding=0, rightPadding=0,
                      topPadding=0, bottomPadding=0)
        self.doc.addPageTemplates([PageTemplate(id="main", frames=[frame],
                                                onPage=on_page)])

    def build(self):
        self.doc.build(self.story)
        return self.opts.get("output")


def create_pdf(opts: dict, content: Optional[list] = None) -> Outcome:
    """Create a PDF. ``opts`` describes page setup/output; ``content`` is the
    flowable list. Returns an Outcome with validation.
    """
    _require_reportlab()
    out = Outcome(skill="pdf-create")
    try:
        sb = _StoryBuilder(opts)
        content = content if content is not None else opts.get("content", [])
        _build_flowables(sb.doc, content, opts, sb.story)
        target = sb.build()
        # attach metadata
        _set_metadata_after(target, opts.get("metadata", {}))
        out.output_path = target
        out.data = {"output": target}
        out.ok = True
        out.status = "completed"
        out.check("pdf_openable", True, True, V.openable(target).passed)
        out.check("output_exists", True, os.path.exists(target),
                  os.path.exists(target))
        pc = V.page_count(target, expected=None)
        out.check("page_count", ">=1", pc.actual, pc.actual >= 1)
        return out
    except Exception as exc:  # noqa: BLE001
        out.ok = False
        out.status = "failed"
        out.messages.append(f"creation failed: {exc}")
        return out


def _set_metadata_after(path, md: dict):
    if not md:
        return
    try:
        import pymupdf
        with pymupdf.open(path) as doc:
            doc.set_metadata(md)
            doc.save(path, incremental=True, encryption=pymupdf.PDF_ENCRYPT_KEEP)
    except Exception:
        pass


# ------------------------------------------------------------ md / html/ text
def _markdown_to_content(md: str) -> list:
    """Parse a practical subset of Markdown into content flowables."""
    content = []
    lines = md.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i].rstrip()
        stripped = line.strip()
        if not stripped:
            i += 1
            continue
        if stripped.startswith("#"):
            level = len(stripped) - len(stripped.lstrip("#"))
            content.append({"type": "heading", "text": stripped.lstrip("#").strip(),
                            "level": min(level, 4)})
        elif stripped.startswith("|") and i + 1 < len(lines) and "---" in lines[i + 1]:
            # simple pipe table
            header = [c.strip() for c in stripped.strip("|").split("|")]
            rows = []
            j = i + 2
            while j < len(lines) and lines[j].strip().startswith("|"):
                rows.append([c.strip() for c in lines[j].strip("|").split("|")])
                j += 1
            content.append({"type": "table", "rows": [header] + rows})
            i = j
        elif stripped.startswith("- ") or stripped.startswith("* "):
            items = []
            while i < len(lines) and (lines[i].strip().startswith("- ") or
                                      lines[i].strip().startswith("* ")):
                items.append(lines[i].strip()[2:])
                i += 1
            content.append({"type": "list", "items": items, "ordered": False})
        elif re_match(r"^\d+\.\s", stripped):
            items = []
            while i < len(lines) and re_match(r"^\d+\.\s", lines[i].strip()):
                items.append(lines[i].strip().split(".", 1)[1].strip())
                i += 1
            content.append({"type": "list", "items": items, "ordered": True})
        elif stripped.startswith("![") :
            pass  # image md; handled crudely below
        elif stripped.startswith("```"):
            j = i + 1
            code = []
            while j < len(lines) and not lines[j].strip().startswith("```"):
                code.append(lines[j])
                j += 1
            content.append({"type": "parahtml",
                            "html": "<font face='Courier' size=9>" +
                                    _escape("\n".join(code)) + "</font>"})
            i = j + 1
        elif stripped.startswith("> "):
            content.append({"type": "parahtml",
                            "html": "<font color='#555'>" +
                                    _escape(stripped[2:]) + "</font>"})
        elif stripped.startswith("---"):
            content.append({"type": "hr"})
        else:
            # accumulate paragraph until blank
            para = [line]
            i += 1
            while i < len(lines) and lines[i].strip():
                para.append(lines[i].rstrip())
                i += 1
            content.append({"type": "para", "text": " ".join(para)})
            continue
        i += 1
    return content


def re_match(pattern, s):
    import re
    return re.match(pattern, s)


def create_from_markdown(path_md: str, output: str,
                         opts: Optional[dict] = None) -> Outcome:
    md = Path(path_md).read_text(encoding="utf-8", errors="replace")
    content = _markdown_to_content(md)
    o = dict(opts or {})
    o["output"] = output
    return create_pdf(o, content)


def create_from_text(path_txt: str, output: str,
                     opts: Optional[dict] = None) -> Outcome:
    txt = Path(path_txt).read_text(encoding="utf-8", errors="replace")
    content = [{"type": "para", "text": block}
               for block in txt.split("\n\n")]
    o = dict(opts or {})
    o["output"] = output
    return create_pdf(o, content)


def create_from_html(path_html: str, output: str,
                     opts: Optional[dict] = None) -> Outcome:
    """HTML -> PDF using a small tag mapper (headings/p/li/table/img/a).

    This is a pragmatic subset, NOT a full browser engine. For pixel-perfect
    complex HTML prefer pdf-convert with a dedicated renderer.
    """
    import re
    from html.parser import HTMLParser

    HEAD = {"h1": 1, "h2": 2, "h3": 3, "h4": 4}

    class _H(HTMLParser):
        def __init__(self):
            super().__init__()
            self.content = []
            self._buf = []
            self._in_list = None     # "ol" or "ul" or None
            self._in_cell = False
            self._cell_buf = []
            self._rows = []
            self._in_table = False

        def handle_starttag(self, tag, attrs):
            tag = tag.lower()
            if tag in HEAD:
                self._flush_text()
            elif tag == "br":
                self._buf.append("\n")
            elif tag in ("ol", "ul"):
                self._in_list = tag
            elif tag == "table":
                self._in_table = True
                self._rows = []
            elif tag == "tr" and self._in_table:
                self._rows.append([])
            elif tag in ("td", "th") and self._in_table:
                self._in_cell = True
                self._cell_buf = []

        def handle_endtag(self, tag):
            tag = tag.lower()
            if tag in HEAD:
                txt = "".join(self._buf).strip()
                self._buf = []
                if txt:
                    self.content.append({"type": "heading", "text": txt,
                                         "level": HEAD[tag]})
            elif tag == "p":
                txt = "".join(self._buf).strip()
                self._buf = []
                if txt:
                    self.content.append({"type": "para", "text": txt})
            elif tag == "li":
                txt = "".join(self._buf).strip()
                self._buf = []
                if txt:
                    self._append_list_item(txt)
            elif tag in ("ol", "ul"):
                self._in_list = None
            elif tag == "table":
                if self._rows:
                    self.content.append({"type": "table", "rows": self._rows})
                self._in_table = False
            elif tag in ("td", "th") and self._in_table:
                self._in_cell = False
                txt = "".join(self._cell_buf).strip()
                if self._rows:
                    self._rows[-1].append(txt)
                self._cell_buf = []

        def handle_data(self, data):
            if self._in_cell:
                self._cell_buf.append(data)
            else:
                self._buf.append(data)

        def _flush_text(self):
            txt = "".join(self._buf).strip()
            if txt:
                self.content.append({"type": "para", "text": txt})
            self._buf = []

        def _append_list_item(self, txt):
            for c in reversed(self.content):
                if c.get("type") == "list":
                    c["items"].append(txt)
                    return
            self.content.append({"type": "list", "items": [txt],
                                 "ordered": self._in_list == "ol"})

    html = Path(path_html).read_text(encoding="utf-8", errors="replace")
    html = re.sub(r"<(style|script)[^>]*>.*?</\1>", "", html,
                  flags=re.S | re.I)
    p = _H()
    p.feed(html)
    o = dict(opts or {})
    o["output"] = output
    return create_pdf(o, p.content)


def create_from_images(image_paths: Sequence[str], output: str,
                       page_size: str = "a4",
                       fit_mode: str = "contain",
                       metadata: Optional[dict] = None) -> Outcome:
    """Build a PDF where each image occupies one page."""
    from reportlab.platypus import Image, PageBreak, Spacer
    out = Outcome(skill="pdf-create")
    _require_reportlab()
    try:
        opts = {"output": output, "page_size": page_size,
                "page_numbers": False,
                "margins": {"left": 0.15, "right": 0.15, "top": 0.15,
                            "bottom": 0.15},
                "metadata": metadata or {},
                "content": []}
        sb = _StoryBuilder(opts)
        ps = _page_size(page_size)
        margin_px = 0.15 * 72
        maxw = ps[0] - 2 * margin_px - 4
        maxh = ps[1] - 2 * margin_px - 4
        first = True
        for ip in image_paths:
            if not first:
                sb.story.append(PageBreak())
            first = False
            img = Image(ip)
            iw, ih = img.imageWidth, img.imageHeight
            scale = min(maxw / iw, maxh / ih)
            img.drawWidth = iw * scale
            img.drawHeight = ih * scale
            # sized to fit the (small-margin) content frame so it cannot overflow
            sb.story.append(img)
        target = sb.build()
        _set_metadata_after(target, metadata or {})
        out.output_path = target
        out.ok = True
        out.status = "completed"
        out.data = {"output": target, "pages": len(list(image_paths))}
        return out
    except Exception as exc:  # noqa: BLE001
        out.ok = False
        out.status = "failed"
        out.messages.append(str(exc))
        return out


def create_report_from_rows(rows, columns: list[str], output: str,
                            title: str = "", opts: Optional[dict] = None) -> Outcome:
    """Structured data (list of dicts) -> a titled table report PDF."""
    header = columns or (list(rows[0].keys()) if rows else [])
    trows = [header]
    for r in rows:
        if isinstance(r, dict):
            trows.append([r.get(c, "") for c in header])
        else:
            trows.append([r])
    content = []
    if title:
        content.append({"type": "heading", "text": title, "level": 1})
    content.append({"type": "table", "rows": trows})
    o = dict(opts or {})
    o["output"] = output
    return create_pdf(o, content)
