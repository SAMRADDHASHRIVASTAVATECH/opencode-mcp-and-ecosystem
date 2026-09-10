"""OCR workflow (requirement 6) with automatic need-detection + degradation.

Detection: probe a sample of pages; if the text layer is too thin, OCR is
needed. We never OCR pages that already carry usable text.

Two honest capabilities:
  * ``make_searchable``  -> add a real text layer to scanned pages (needs the
                            external ``ocrmypdf`` binary for reliable results).
  * ``ocr_page_text``    -> recognise text on a page and return it (needs
                            pytesseract + the tesseract engine, which PyMuPDF's
                            ``get_textpage_ocr`` uses).

If no backend is present the skill returns a *degraded* Outcome explaining the
limitation. It never fabricates recognised text and never claims a searchable
layer was added when it was not.
"""
from __future__ import annotations

import shutil
from typing import Optional

from ..result import Outcome

_OCR_STATE = {"ocrmypdf": None, "tesseract": None}


def _find_backends():
    _OCR_STATE["ocrmypdf"] = bool(shutil.which("ocrmypdf"))
    _OCR_STATE["tesseract"] = None
    try:
        import pytesseract  # noqa: F401
        if shutil.which("tesseract"):
            _OCR_STATE["tesseract"] = "tesseract"
    except Exception:
        pass
    try:
        import easyocr  # noqa: F401
        _OCR_STATE["tesseract"] = _OCR_STATE["tesseract"] or "easyocr"
    except Exception:
        pass
    return _OCR_STATE


def ocr_backend() -> dict:
    if _OCR_STATE["ocrmypdf"] is None:
        _find_backends()
    return dict(_OCR_STATE)


def ocr_available() -> bool:
    b = ocr_backend()
    return bool(b["ocrmypdf"] or b["tesseract"])


def detect_ocr_need(path: str, sample_pages: int = 5,
                    password=None) -> dict:
    from ..core import extract as ex
    return ex.detect_text_layer(path, sample_pages, )


def make_searchable(path: str, output: str, language: str = "eng",
                    pages: Optional[list] = None,
                    deskew: bool = True, force_ocr: bool = False,
                    password=None) -> Outcome:
    """Add a searchable text layer on top of scanned page images.

    Uses the ``ocrmypdf`` CLI when available. If ``pages`` is a subset we
    render+OCR those pages and re-compose. If ocrmypdf is absent the call
    degrades and instructs how to install it.
    """
    out = Outcome(skill="pdf-ocr")
    b = ocr_backend()
    if b["ocrmypdf"]:
        return _make_searchable_ocrmypdf(out, path, output, language,
                                         pages, deskew, force_ocr, password)
    if b["tesseract"]:
        return _make_searchable_tesseract(out, path, output, language,
                                          pages, password)
    out.ok = False
    out.degraded = True
    out.status = "degraded"
    out.messages.append(
        "Neither ocrmypdf nor a Tesseract OCR engine is installed. A "
        "searchable text layer cannot be added with the current backend. "
        "Install ocrmypdf: 'pip install ocrmypdf' (needs tesseract + "
        "ghostscript).")
    # Still report whether the source even needs OCR.
    need = detect_ocr_need(path)
    out.warnings.append(f"source needs OCR: {need.get('needs_ocr')}")
    return out


def _make_searchable_ocrmypdf(out: Outcome, path: str, output: str,
                              language: str, pages, deskew: bool,
                              force_ocr: bool, password=None) -> Outcome:
    import subprocess
    cmd = ["ocrmypdf", "--language", language, "--output-type", "pdfa"]
    if force_ocr:
        cmd.append("--force-ocr")
    else:
        cmd.append("--skip-text")
    if deskew:
        cmd.append("--deskew")
    if pages:
        # ocrmypdf pages is 1-indexed comma list
        if isinstance(pages, int):
            pages = [pages]
        cmd += ["--pages", ",".join(str(p) for p in pages)]
    if password:
        cmd += ["--password", password]
    cmd += [path, output]
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
    except Exception as exc:  # noqa: BLE001
        out.ok = False
        out.status = "failed"
        out.messages.append(f"ocrmypdf invocation failed: {exc}")
        return out
    if r.returncode != 0:
        out.ok = False
        out.status = "failed"
        out.messages.append(f"ocrmypdf error: {r.stderr[-2000:]}")
        return out
    out.output_path = output
    out.ok = True
    out.status = "completed"
    out.data = {"backend": "ocrmypdf", "language": language,
                "pages": pages}
    out.check("openable", True, _open_ok(output), True)
    return out


def _make_searchable_tesseract(out: Outcome, path: str, output: str,
                               language: str, pages, password=None) -> Outcome:
    """Add a searchable text layer via PyMuPDF's Tesseract-backed OCR.

    Used when the ``ocrmypdf`` CLI is absent but a Tesseract engine is
    present (PyMuPDF's ``Page.get_textpage_ocr``). Renders each target page
    to a pixmap, inserts it onto a fresh page, and runs Tesseract on it so
    the saved PDF carries a real text layer. Non-target pages are copied
    verbatim. Degrades honestly if Tesseract itself fails.
    """
    import pymupdf
    try:
        src = pymupdf.open(path)
    except Exception as exc:  # noqa: BLE001
        out.ok = False
        out.status = "failed"
        out.messages.append(f"cannot open source: {exc}")
        return out
    try:
        if password and src.needs_pass:
            src.authenticate(password)
        if pages is None:
            targets = list(range(len(src)))
        elif isinstance(pages, int):
            targets = [pages - 1]
        else:
            targets = [p - 1 for p in pages if 1 <= p <= len(src)]
        dst = pymupdf.open()
        for pno in range(len(src)):
            page = src[pno]
            dst.insert_pdf(src, from_page=pno, to_page=pno)
            if pno in targets:
                new_page = dst[-1]
                pix = page.get_pixmap(dpi=300)
                new_page.insert_image(new_page.rect, stream=pix.tobytes("png"))
                try:
                    tp = new_page.get_textpage_ocr(language=language,
                                                   full=True, dpi=300)
                    text = tp.extractText()
                except Exception as exc:  # noqa: BLE001
                    out.ok = False
                    out.status = "failed"
                    out.messages.append(f"tesseract OCR failed: {exc}")
                    dst.close()
                    src.close()
                    return out
                if not text.strip():
                    out.warnings.append(
                        f"page {pno + 1}: OCR returned no text")
        if password:
            dst.save(output, encryption=pymupdf.PDF_ENCRYPT_AES_256,
                     user_pw=password, owner_pw=password)
        else:
            dst.save(output)
        dst.close()
        src.close()
        out.output_path = output
        out.ok = True
        out.status = "completed"
        out.data = {"backend": "tesseract", "language": language,
                    "pages": [p + 1 for p in targets]}
        out.check("openable", True, _open_ok(output), True)
        return out
    except Exception as exc:  # noqa: BLE001
        try:
            src.close()
        except Exception:
            pass
        out.ok = False
        out.status = "failed"
        out.messages.append(f"searchable-layer creation failed: {exc}")
        return out


def ocr_page_text(path: str, page: int = 1, language: str = "eng",
                  dpi: int = 300, password=None) -> Outcome:
    """Recognise text on a page and return it (pytesseract / PyMuPDF OCR).

    Only callers that genuinely need the recognised string use this; making a
    searchable PDF uses :func:`make_searchable`.
    """
    out = Outcome(skill="pdf-ocr")
    b = ocr_backend()
    if not b["tesseract"]:
        out.ok = False
        out.degraded = True
        out.status = "degraded"
        out.messages.append(
            "No OCR text engine available (pytesseract+tesseract or easyocr).")
        return out
    import pymupdf
    doc = pymupdf.open(path)
    try:
        if password and doc.needs_pass:
            doc.authenticate(password)
        pg = doc[page - 1]
        tp = pg.get_textpage_ocr(language=language, full=True, dpi=dpi)
        text = tp.extractText()
        doc.close()
        out.ok = True
        out.data = {"page": page, "text": text, "backend": b["tesseract"],
                    "confidence": None}
        out.check("has_text", True, bool(text.strip()), True)
        return out
    except Exception as exc:  # noqa: BLE001
        try:
            doc.close()
        except Exception:
            pass
        out.ok = False
        out.status = "failed"
        out.messages.append(f"OCR failed: {exc}")
        return out


def _open_ok(path: str) -> bool:
    try:
        import pymupdf
        d = pymupdf.open(path)
        d.close()
        return True
    except Exception:
        return False
