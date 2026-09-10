"""Dedicated table processing (requirement 8).

Extraction preserves structure (rows/columns) rather than flattening text.
Preferred tool: pdfplumber (robust line+text analysis). Fallback: PyMuPDF
``page.find_tables``. Export helpers produce CSV / XLSX / JSON / Markdown.
"""
from __future__ import annotations

import csv
import json
from typing import Optional, Sequence

from ..result import Outcome
from ..tools import adapter


def extract_tables(path: str, pages: Optional[list] = None,
                   password=None) -> Outcome:
    """Extract tables preserving page provenance and cell structure.

    Returns data.tables = [ {"page":p, "n":i, "header":[...], "rows":[[..]]} ]
    """
    out = Outcome(skill="pdf-tables")
    use_plumber = adapter.backend_available("pdfplumber")
    try:
        if use_plumber:
            return _extract_pdfplumber(path, pages, password, out)
        return _extract_pymupdf(path, pages, password, out)
    except Exception as exc:  # noqa: BLE001
        out.ok = False
        out.status = "failed"
        out.messages.append(f"table extraction failed: {exc}")
        return out


def _extract_pdfplumber(path, pages, password, out):
    import pdfplumber
    tables = []
    with pdfplumber.open(path, password=password or "") as pdf:
        total = len(pdf.pages)
        plist = sorted(set(pages)) if pages else list(range(1, total + 1))
        for pno in plist:
            page = pdf.pages[pno - 1]
            for t in page.extract_tables():
                # drop fully-empty trailing rows
                rows = [_clean_row(r) for r in t]
                rows = [r for r in rows if any((c or "").strip() for c in r)]
                if rows:
                    tables.append({"page": pno, "n": len(tables) + 1,
                                   "header": rows[0], "rows": rows[1:]})
    out.ok = True
    out.data = {"tables": tables, "count": len(tables),
                "backend": "pdfplumber"}
    out.check("extracted", ">=0", len(tables), True)
    return out


def _extract_pymupdf(path, pages, password, out):
    import pymupdf
    tables = []
    doc = pymupdf.open(path)
    if password and doc.needs_pass:
        doc.authenticate(password)
    total = doc.page_count
    plist = sorted(set(pages)) if pages else list(range(1, total + 1))
    for pno in plist:
        page = doc[pno - 1]
        try:
            found = page.find_tables()
        except Exception:
            continue
        for t in found.tables:
            data = t.extract()
            rows = [_clean_row(r) for r in data]
            rows = [r for r in rows if any((c or "").strip() for c in r)]
            if rows:
                tables.append({"page": pno, "n": len(tables) + 1,
                               "header": rows[0], "rows": rows[1:]})
    doc.close()
    out.ok = True
    out.data = {"tables": tables, "count": len(tables), "backend": "pymupdf"}
    out.check("extracted", ">=0", len(tables), True)
    return out


def _clean_row(r):
    out_r = []
    for c in r:
        if c is None:
            out_r.append("")
        elif isinstance(c, dict):  # pdfplumber header object
            out_r.append(c.get("text") or "")
        else:
            out_r.append(str(c).strip())
    return out_r


def _flatten_headers(tables):
    """Merge header cells, returns list of list of lists? We just keep them."""


# ------------------------------------------------------------------ exporters
def tables_to_csv(tables: Sequence[dict], output: str,
                  one_file: bool = True) -> Outcome:
    out = Outcome(skill="pdf-tables")
    try:
        if one_file:
            with open(output, "w", newline="", encoding="utf-8") as fh:
                w = csv.writer(fh)
                wrote_any = False
                for ti, t in enumerate(tables):
                    header = ["_table", "_page"] + list(t.get("header", []))
                    if not wrote_any:
                        w.writerow(header)
                        wrote_any = True
                    for r in t.get("rows", []):
                        w.writerow([t.get("n", ti), t.get("page", ""), *r])
        else:
            import os
            base = os.path.splitext(output)[0]
            written = []
            for t in tables:
                fp = f"{base}_table{t.get('n', len(written)+1)}_p{t.get('page',1)}.csv"
                with open(fp, "w", newline="", encoding="utf-8") as fh:
                    w = csv.writer(fh)
                    w.writerow(t.get("header", []))
                    w.writerows(t.get("rows", []))
                written.append(fp)
            output = None
        out.output_path = output
        out.ok = True
        out.data = {"rows_written": sum(len(t.get("rows", [])) for t in tables)}
        out.check("written", True, True, True)
        return out
    except Exception as exc:  # noqa: BLE001
        out.ok = False
        out.status = "failed"
        out.messages.append(f"csv export failed: {exc}")
        return out


def tables_to_xlsx(tables: Sequence[dict], output: str) -> Outcome:
    from openpyxl import Workbook
    from openpyxl.styles import Font
    out = Outcome(skill="pdf-tables")
    try:
        wb = Workbook()
        ws0 = None
        for t in tables:
            name = f"T{t.get('n', 0)}"
            ws = wb.create_sheet(title=name[:31])
            ws.append(t.get("header", []))
            for c in ws[1]:
                c.font = Font(bold=True)
            for r in t.get("rows", []):
                ws.append(r)
        wb.remove(wb.active) if len(wb.sheetnames) > 1 and "Sheet" in wb.sheetnames else None
        if len(wb.sheetnames) == 0:
            wb.create_sheet("Sheet1")
        wb.save(output)
        out.output_path = output
        out.ok = True
        out.data = {"sheets": len(tables)}
        out.check("written", True, True, True)
        return out
    except Exception as exc:  # noqa: BLE001
        out.ok = False
        out.status = "failed"
        out.messages.append(f"xlsx export failed (install openpyxl): {exc}")
        return out


def tables_to_json(tables: Sequence[dict], output: str) -> Outcome:
    out = Outcome(skill="pdf-tables")
    try:
        with open(output, "w", encoding="utf-8") as fh:
            json.dump(list(tables), fh, indent=2)
        out.output_path = output
        out.ok = True
        out.data = {"tables": len(tables)}
        return out
    except Exception as exc:  # noqa: BLE001
        out.ok = False
        out.status = "failed"
        out.messages.append(str(exc))
        return out


def tables_to_markdown(tables: Sequence[dict], output: str) -> Outcome:
    out = Outcome(skill="pdf-tables")
    try:
        with open(output, "w", encoding="utf-8") as fh:
            for t in tables:
                header = t.get("header", [])
                fh.write("| " + " | ".join(str(h) for h in header) + " |\n")
                fh.write("| " + " | ".join("---" for _ in header) + " |\n")
                for r in t.get("rows", []):
                    fh.write("| " + " | ".join(str(c) for c in r) + " |\n")
                fh.write("\n")
        out.output_path = output
        out.ok = True
        return out
    except Exception as exc:  # noqa: BLE001
        out.ok = False
        out.status = "failed"
        out.messages.append(str(exc))
        return out


def validate_tables(tables: Sequence[dict]) -> Outcome:
    """Basic validation: consistent column counts per table."""
    out = Outcome(skill="pdf-tables")
    issues = []
    for t in tables:
        h = len(t.get("header", []))
        for r in t.get("rows", []):
            if len(r) != h:
                issues.append({"page": t.get("page"), "table": t.get("n"),
                               "expected": h, "got": len(r)})
    out.ok = len(issues) == 0
    out.status = "completed" if out.ok else "degraded"
    if issues:
        out.warnings.append(f"{len(issues)} ragged rows found")
    out.data = {"issues": issues[:20], "total_issues": len(issues),
                "tables": len(tables)}
    out.check("column_consistency", 0, len(issues), len(issues) == 0)
    return out
