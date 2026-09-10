"""Shared pytest fixtures.

Fixtures are generated in pytest's tmp dir (and auto-cleaned) so the committed
repository stays free of build artifacts while tests remain deterministic.
"""
import os
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import universal_pdf as up  # noqa: E402
from universal_pdf.core import create, tables, security  # noqa: E402


@pytest.fixture(scope="session")
def engine_root():
    return ROOT


def _text_content():
    return [
        {"type": "cover", "title": "Universal PDF Test Document",
         "subtitle": "Fixture", "author": "QA Bot",
         "date": "2026-09-06"},
        {"type": "heading", "text": "Introduction", "level": 1},
        {"type": "para", "text": ("This is the introduction paragraph. It "
                                  "contains a confidential secret code "
                                  "ACME-7788 and some repeated words: alpha "
                                  "beta alpha beta.")},
        {"type": "heading", "text": "Data & Tables", "level": 2},
        {"type": "table", "rows": [["Product", "Price", "Stock"],
                                   ["Widget", 12.5, 100],
                                   ["Gadget", 7.0, 250],
                                   ["Sprocket", 3.25, 999]]},
        {"type": "para", "text": "More content on a later page."},
        {"type": "pagebreak"},
        {"type": "heading", "text": "Second Chapter", "level": 1},
        {"type": "para", "text": ("Body of the second chapter, page two. "
                                  "Searchable phrase unique_needle_phrase here.")},
    ]


@pytest.fixture
def text_pdf(tmp_path):
    path = tmp_path / "text.pdf"
    o = create.create_pdf({"output": str(path), "page_size": "a4",
                           "header": "ACME", "footer": "private",
                           "metadata": {"title": "Test Doc"}},
                          _text_content())
    assert o.ok
    return str(path)


@pytest.fixture
def table_pdf(tmp_path):
    """A PDF where a table spans rows reliably for extraction."""
    path = tmp_path / "tabledoc.pdf"
    content = [{"type": "heading", "text": "Sales", "level": 1},
               {"type": "table", "rows": [
                   ["Region", "Q1", "Q2", "Q3", "Q4"],
                   ["North", 100, 120, 90, 140],
                   ["South", 80, 95, 110, 105],
                   ["East", 60, 70, 75, 80],
                   ["West", 50, 55, 60, 90]]}]
    o = create.create_pdf({"output": str(path)}, content)
    assert o.ok
    return str(path)


@pytest.fixture
def image_only_pdf(tmp_path):
    """A PDF with NO text layer (image-only) to exercise OCR degradation."""
    from PIL import Image, ImageDraw
    img = Image.new("RGB", (1200, 1600), "white")
    d = ImageDraw.Draw(img)
    d.text((80, 120), "SCANNED DOCUMENT - no text layer",
           fill="black", font=None)
    imgp = tmp_path / "s.png"
    img.save(imgp)
    path = tmp_path / "scanned.pdf"
    o = create.create_from_images([str(imgp)], str(path))
    assert o.ok
    return str(path)
