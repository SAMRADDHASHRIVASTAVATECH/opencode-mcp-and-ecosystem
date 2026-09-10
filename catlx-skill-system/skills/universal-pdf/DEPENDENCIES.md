# Dependencies

## Python packages (required)
| Package | Version used | Needed for | Required? |
|---|---|---|---|
| `pymupdf` (imports as `pymupdf`, legacy `fitz`) | 1.28.x | inspect, extract, manipulate, annotate, security, forms, metadata, bookmarks, links, repair, render, compress, tables (fallback) | **required** (preferred backend) |
| `reportlab` | 5.x | PDF creation (vector, templated) | **required** for `pdf-create` |
| `pypdf` | 6.x | crypto/structural fallback | recommended |
| `pdfplumber` | 0.11.x | high-fidelity layout + table extraction | recommended |
| `pillow` (PIL) | 10.x | images (render/image ops/visual diff) | recommended |
| `openpyxl` | 3.x | table → XLSX export | optional (only `xlsx`) |
| `python-docx` | 1.x | minimal PDF→DOCX text import fallback | optional |
| `pytest` | 9.x | run the test suite | dev only |

## Optional external binaries / heavy engines
| Binary / lib | Enables | If absent |
|---|---|---|
| `ocrmypdf` (+ tesseract + ghostscript) | adding a **searchable text layer** over scanned pages | `pdf-ocr` degrades with instructions (never fakes) |
| `tesseract` + `pytesseract` | OCR page text via PyMuPDF `get_textpage_ocr` | `ocr_page_text` degrades |
| `easyocr` / `paddleocr` | OCR page text (heavier) | degrade |
| `pandoc` | faithful PDF→DOCX | `pdf-convert` DOCX reports a limitation |
| `ghostscript` / `qpdf` | extra repair & optimisation pass | structural repair still works via PyMuPDF/pypdf |

## Install
```bash
# core
pip install pymupdf reportlab pypdf pdfplumber pillow
# optional
pip install openpyxl python-docx
pip install ocrmypdf            # + system tesseract, ghostscript for OCR
pip install pytest              # dev
```

> The system **runs on `pymupdf` + `reportlab` alone**. Everything else is a
> progressive enhancement that the tool-abstraction layer uses only when
> present. Missing enhancements are reported, never faked.

## Version notes (verified 2026-09)
- PyMuPDF ≥ 1.28 moved `apply_redactions` and `widgets` to the **Page** object;
  the engine uses the page-level API, so it works on both current and legacy
  releases where those methods exist.
- `Document.rewrite_images(...)` is used when present for image recompression;
  otherwise `pdf-compress` degrades to structural-only cleanup and says so.
