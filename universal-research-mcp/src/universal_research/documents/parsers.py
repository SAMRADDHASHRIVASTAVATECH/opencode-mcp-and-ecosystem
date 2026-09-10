"""Text extraction from office/PDF document formats.

Each function returns plain text. Optional libraries degrade gracefully.
"""
from __future__ import annotations

import io


def extract_pdf(data: bytes) -> str:
    import pypdf
    r = pypdf.PdfReader(io.BytesIO(data))
    out = []
    for pg in r.pages:
        try:
            out.append(pg.extract_text() or "")
        except Exception:
            continue
    return "\n".join(out)


def extract_docx(data: bytes) -> str:
    import docx
    d = docx.Document(io.BytesIO(data))
    parts = [p.text for p in d.paragraphs]
    for t in d.tables:
        for row in t.rows:
            parts.append(" | ".join(c.text for c in row.cells))
    return "\n".join(parts)


def extract_xlsx(data: bytes) -> str:
    import openpyxl
    wb = openpyxl.load_workbook(io.BytesIO(data), data_only=True)
    out = []
    for ws in wb.worksheets:
        out.append(f"== Sheet: {ws.title} ==")
        for row in ws.iter_rows(values_only=True):
            vals = ["" if v is None else str(v) for v in row]
            if any(vals):
                out.append(" | ".join(vals))
    return "\n".join(out)


def extract_pptx(data: bytes) -> str:
    from pptx import Presentation
    prs = Presentation(io.BytesIO(data))
    out = []
    for i, slide in enumerate(prs.slides, 1):
        out.append(f"== Slide {i} ==")
        for shape in slide.shapes:
            if shape.has_text_frame:
                for para in shape.text_frame.paragraphs:
                    txt = "".join(run.text for run in para.runs)
                    if txt.strip():
                        out.append(txt)
            if getattr(shape, "has_table", False):
                for row in shape.table.rows:
                    out.append(" | ".join(c.text for c in row.cells))
    return "\n".join(out)


def extract_plain(data: bytes) -> str:
    try:
        return data.decode("utf-8", errors="replace")
    except Exception:
        return ""


# content-type / extension -> parser
PARSERS = {
    "pdf": extract_pdf,
    "doc": extract_docx,
    "docx": extract_docx,
    "spreadsheet": extract_xlsx,
    "xlsx": extract_xlsx,
    "presentation": extract_pptx,
    "pptx": extract_pptx,
    "text": extract_plain,
}
