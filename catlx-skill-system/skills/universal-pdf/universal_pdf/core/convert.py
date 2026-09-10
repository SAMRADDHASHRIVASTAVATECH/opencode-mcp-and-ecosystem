"""PDF -> other formats (requirement 15, read direction).

Faithful conversions are produced where reliable tools exist; lossy or
unsupported directions are reported as documented limitations (graceful
degradation). Creation direction (TXT/MD/HTML/Images/-> PDF) lives in
:mod:`universal_pdf.core.create`.

  PDF -> TXT       text layer extraction
  PDF -> Markdown  TOC headings + per-page text (kept simple & faithful)
  PDF -> HTML      text blocks wrapped with TOC-linked structure
  PDF -> JSON      full structural profile + per-page text
  PDF -> CSV/XLSX  via the tables engine
  PDF -> Images    via the render engine
  PDF -> DOCX      only when a markdown-to-docx converter (e.g. pandoc) exists;
                   otherwise degrades (PyMuPDF cannot author DOCX natively)
"""
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Optional

from ..result import Outcome
from ..tools import adapter
from ..core import validation as V


def pdf_to_text(path: str, output: str, password=None) -> Outcome:
    from ..core import extract as ex
    out = Outcome(skill="pdf-convert")
    pages = ex.extract_per_page(path, password)
    with open(output, "w", encoding="utf-8") as fh:
        for i, p in enumerate(pages, 1):
            fh.write(f"\n\n===== PAGE {i} =====\n\n")
            fh.write(p)
    out.output_path = output
    out.ok = True
    out.status = "completed"
    out.data = {"pages": len(pages)}
    out.check("output_exists", True, V.file_exists(output).passed, True)
    return out


def pdf_to_markdown(path: str, output: str, password=None) -> Outcome:
    import pymupdf
    out = Outcome(skill="pdf-convert")
    doc = pymupdf.open(path)
    if password and doc.needs_pass:
        doc.authenticate(password)
    toc = doc.get_toc()
    pages_text = [doc[i].get_text("text") for i in range(doc.page_count)]
    doc.close()
    lines = []
    lines.append("# Extracted text\n")
    # headings derived from TOC to preserve document structure
    for lvl, title, pno in toc:
        lines.append(f"\n{'#' * min(lvl + 1, 6)} {title}  _(p.{pno})_\n")
    prev_toc_pages = set(p for _, _, p in toc)
    for i, p in enumerate(pages_text, 1):
        if i not in prev_toc_pages:
            for para in p.split("\n\n"):
                para = para.strip()
                if para:
                    lines.append("")
                    lines.append(_md_escape(para))
    with open(output, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines))
    out.output_path = output
    out.ok = True
    out.status = "completed"
    out.check("output_exists", True, V.file_exists(output).passed, True)
    return out


def _md_escape(s):
    return s


def pdf_to_html(path: str, output: str, password=None) -> Outcome:
    from ..core import extract as ex
    import html
    out = Outcome(skill="pdf-convert")
    pages = ex.extract_per_page(path, password)
    parts = ["<!DOCTYPE html><html><head><meta charset='utf-8'>",
             f"<title>{Path(path).stem}</title>",
             "<style>body{font-family:sans-serif;max-width:900px;"
             "margin:40px auto;line-height:1.5} "
             ".page{page-break-before:always;border-top:1px solid #ddd;"
             "padding-top:10px} h2{color:#333}</style></head><body>"]
    for i, p in enumerate(pages, 1):
        parts.append(f"<section class='page'><h2>Page {i}</h2><div>")
        for para in p.split("\n\n"):
            t = para.strip()
            if not t:
                continue
            parts.append(f"<p>{html.escape(t).replace(chr(10), '<br>')}</p>")
        parts.append("</div></section>")
    parts.append("</body></html>")
    with open(output, "w", encoding="utf-8") as fh:
        fh.write("\n".join(parts))
    out.output_path = output
    out.ok = True
    out.status = "completed"
    out.check("output_exists", True, V.file_exists(output).passed, True)
    return out


def pdf_to_json(path: str, output: str, password=None) -> Outcome:
    from ..core import inspect as ins
    from ..core import extract as ex
    out = Outcome(skill="pdf-convert")
    prof = ins.inspect(path, password)
    pages = ex.extract_per_page(path, password)
    payload = {
        "profile": prof.data if prof.ok else {},
        "pages": [{"page": i + 1, "text": t} for i, t in enumerate(pages)],
    }
    with open(output, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, indent=2, default=str)
    out.output_path = output
    out.ok = True
    out.status = "completed"
    out.check("output_exists", True, V.file_exists(output).passed, True)
    return out


def pdf_to_images(path: str, output_dir: str, fmt: str = "png", dpi: int = 150,
                  password=None) -> Outcome:
    from ..core import images as img
    return img.render_pages(path, output_dir, fmt=fmt, dpi=dpi,
                            password=password)


def pdf_to_docx(path: str, output: str, password=None) -> Outcome:
    """PDF -> DOCX. Reliable conversion needs a converter that understands PDF
    layout; without LibreOffice/pandoc we cannot author a faithful DOCX from
    arbitrary PDFs. We route through Markdown and convert only if ``pandoc`` is
    installed, otherwise report a clear limitation.
    """
    out = Outcome(skill="pdf-convert")
    if not adapter.backend_available("docx"):
        # no python-docx guaranteed; check pandoc CLI
        import shutil
        if shutil.which("pandoc"):
            import subprocess, tempfile
            md = pdf_to_markdown(path, tempfile.mktemp(suffix=".md"), password)
            r = subprocess.run(["pandoc", md.output_path, "-o", output],
                               capture_output=True, text=True)
            if r.returncode == 0:
                out.output_path = output
                out.ok = True
                out.data = {"via": "pandoc"}
                return out
        out.ok = False
        out.degraded = True
        out.status = "degraded"
        out.messages.append(
            "PDF->DOCX not available here. Install pandoc (preferred) or "
            "LibreOffice. A faithful DOCX cannot be authored by the current "
            "backends.")
        return out
    # python-docx path: minimal text import
    try:
        import docx
        pages = pdf_to_text(path, None)
        d = docx.Document()
        for line in str(pages.data).splitlines():
            d.add_paragraph(line)
        d.save(output)
        out.output_path = output
        out.ok = True
        out.status = "completed"
        out.degraded = True
        out.warnings.append("DOCX produced as plain text import (no layout)")
        return out
    except Exception as exc:  # noqa: BLE001
        out.ok = False
        out.status = "failed"
        out.messages.append(str(exc))
        return out


def convert_pdf(path: str, output: str, to_format: str,
                password=None) -> Outcome:
    """General dispatcher. to_format: txt|markdown|html|json|images|docx
    |csv|xlsx."""
    fmt = to_format.lower()
    if fmt in ("txt", "text"):
        return pdf_to_text(path, output, password)
    if fmt in ("md", "markdown"):
        return pdf_to_markdown(path, output, password)
    if fmt in ("html", "htm"):
        return pdf_to_html(path, output, password)
    if fmt in ("json",):
        return pdf_to_json(path, output, password)
    if fmt in ("docx",):
        return pdf_to_docx(path, output, password)
    if fmt in ("png", "jpg", "jpeg", "images"):
        return pdf_to_images(path, output, fmt="png" if fmt != "jpg" else "jpg",
                             password=password)
    if fmt in ("csv", "xlsx", "xls"):
        from ..core import tables as tb
        tab = tb.extract_tables(path, password=password)
        if not tab.ok:
            return tab
        tables = tab.data["tables"]
        if fmt == "csv":
            return tb.tables_to_csv(tables, output)
        if fmt == "xlsx":
            return tb.tables_to_xlsx(tables, output)
    out = Outcome(skill="pdf-convert")
    out.ok = False
    out.status = "failed"
    out.messages.append(f"unsupported target format: {to_format}")
    return out
