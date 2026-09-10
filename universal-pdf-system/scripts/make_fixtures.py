#!/usr/bin/env python3
"""Generate the small committed test/demo fixture PDFs into tests/fixtures.

Kept fixtures (text + table + forms) give deterministic quick inputs for the
test suite and examples without building documents at test time.
Usage: python scripts/make_fixtures.py
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from universal_pdf.core import create  # noqa: E402

FIX = ROOT / "tests" / "fixtures"
FIX.mkdir(parents=True, exist_ok=True)


def build_text():
    content = [
        {"type": "cover", "title": "Sample Text Fixture", "subtitle": "tests",
         "author": "QA", "date": "2026-09-06"},
        {"type": "heading", "text": "Chapter One", "level": 1},
        {"type": "para", "text": ("A paragraph with a unique needle phrase "
                                  "alpha_needle_77 and confidential code "
                                  "ACME-7788 for redaction tests.")},
        {"type": "pagebreak"},
        {"type": "heading", "text": "Chapter Two", "level": 1},
        {"type": "para", "text": "Second page content for page-based tests."},
    ]
    o = create.create_pdf({"output": str(FIX / "sample_text.pdf"),
                           "metadata": {"title": "Sample Text",
                                        "author": "QA"}}, content)
    return o


def build_table():
    content = [
        {"type": "heading", "text": "Sales Table", "level": 1},
        {"type": "table", "rows": [
            ["Region", "Q1", "Q2", "Q3"],
            ["North", 120, 130, 90],
            ["South", 80, 95, 110],
            ["West", 55, 60, 75]]},
    ]
    return create.create_pdf({"output": str(FIX / "sample_table.pdf")}, content)


def build_form():
    """A simple AcroForm for form fill/flatten tests (reportlab field API)."""
    from reportlab.pdfgen import canvas
    p = FIX / "sample_form.pdf"
    c = canvas.Canvas(str(p))
    c.drawString(70, 760, "Name:")
    c.acroForm.textfield(name="name", x=130, y=750, width=200, height=18)
    c.drawString(70, 720, "Subscribe:")
    c.acroForm.checkbox(name="subscribe", x=130, y=710, size=14)
    c.drawString(70, 680, "Email:")
    c.acroForm.textfield(name="email", x=130, y=670, width=200, height=18)
    c.save()
    return None


def main():
    build_text(); print("wrote", FIX / "sample_text.pdf")
    build_table(); print("wrote", FIX / "sample_table.pdf")
    build_form();  print("wrote", FIX / "sample_form.pdf")


if __name__ == "__main__":
    main()
