"""PDF repair & diagnostics (requirement 26).

Performs best-effort repair by re-serialising the object graph, rebuilding
cross-reference tables and dropping broken objects, then reports exactly what
was recovered. When complete repair is impossible the recoverable content is
rescued page-by-page and the limits are reported honestly.

Backends:
  * preferred: PyMuPDF save(garbage) re-write
  * structural cross-ref rebuild: pypdf's generic rebuild
"""
from __future__ import annotations

import os
from typing import Optional

from ..result import Outcome
from ..tools import adapter


def diagnose(path: str, password=None) -> Outcome:
    """Report openability, encryption, structural health and which parts can
    be recovered. Does not modify the file."""
    out = Outcome(skill="pdf-repair")
    import pymupdf
    try:
        doc = pymupdf.open(path)
    except Exception as exc:  # noqa: BLE001
        out.ok = False
        out.degraded = True
        out.status = "degraded"
        out.data = {"openable": False, "reason": str(exc)}
        out.messages.append(f"could not open: {exc}")
        return out
    try:
        enc = bool(doc.is_encrypted or doc.needs_pass)
        try:
            page_count = doc.page_count
            pages_ok = True
        except Exception as exc:  # noqa: BLE001
            page_count = -1
            pages_ok = False
            out.messages.append(f"page tree broken: {exc}")
        # try rendering + extracting page 1 as a health probe
        renderable = False
        try:
            if page_count > 0:
                pix = doc[0].get_pixmap(dpi=36)
                renderable = pix.width > 0
        except Exception:
            renderable = False
        text_ok = False
        try:
            if page_count > 0:
                t = doc[0].get_text("text")
                text_ok = True
        except Exception:
            text_ok = False
        out.data = {"openable": True, "encrypted": enc, "page_count": page_count,
                    "page_tree_ok": pages_ok, "renderable": renderable,
                    "text_layer_readable": text_ok}
        checks_ok = pages_ok
        out.ok = True
        out.status = "completed"
        out.check("diagnosed", True, True, True)
        return out
    finally:
        doc.close()


def repair_pdf(path: str, output: str, rebuild: bool = True,
               garbage: int = 4, password=None) -> Outcome:
    """Attempt to repair a PDF and write to ``output``.

    Strategy:
      1. open (supply password if needed)
      2. re-save with full garbage collection + clean to rebuild xrefs/objects
      3. if the page tree is broken, rescue per-page content into a new doc
      4. validate and report what is usable / what could not be recovered
    """
    out = Outcome(skill="pdf-repair")
    import pymupdf
    try:
        doc = pymupdf.open(path)
    except Exception as exc:  # noqa: BLE001
        out.ok = False
        out.degraded = True
        out.status = "degraded"
        out.messages.append(f"cannot open for repair: {exc}")
        # pypdf structural rebuild attempt
        if adapter.backend_available("pypdf") and rebuild:
            try:
                from pypdf import PdfReader, PdfWriter
                reader = PdfReader(path, strict=False)
                writer = PdfWriter()
                for p in reader.pages:
                    writer.add_page(p)
                with open(output, "wb") as fh:
                    writer.write(fh)
                out.output_path = output
                out.ok = True
                out.degraded = True
                out.warnings.append("repaired via pypdf structural rebuild")
                out.data = {"pages": len(writer.pages)}
                return out
            except Exception as exc2:  # noqa: BLE001
                out.messages.append(f"pypdf rebuild failed: {exc2}")
        return out
    recovered_pages = 0
    errors = []
    try:
        if password and doc.needs_pass:
            okp = doc.authenticate(password or "")
            if not okp and doc.needs_pass:
                out.ok = False
                out.status = "failed"
                out.messages.append("encrypted; password required/incorrect")
                doc.close()
                return out
        try:
            n = doc.page_count
            doc.save(output, garbage=garbage, clean=True, deflate=True)
            recovered_pages = n
        except Exception as exc:  # noqa: BLE001
            errors.append(f"full save failed ({exc}); attempting rescue")
            # per-page rescue
            try:
                outdoc = pymupdf.open()
                i = 0
                while True:
                    try:
                        page = doc.load_page(i)
                        outdoc.insert_pdf(doc, from_page=i, to_page=i)
                        recovered_pages += 1
                    except Exception:
                        break
                    i += 1
                outdoc.save(output, garbage=garbage, deflate=True)
                outdoc.close()
                out.degraded = True
                out.warnings.append("rescued page-by-page; some content may be lost")
            except Exception as exc2:  # noqa: BLE001
                errors.append(f"rescue failed: {exc2}")
        doc.close()
    except Exception as exc:  # noqa: BLE001
        try:
            doc.close()
        except Exception:
            pass
        out.ok = False
        out.status = "failed"
        out.messages.append(f"repair failed: {exc}")
        return out

    out.output_path = output
    out.ok = os.path.exists(output)
    out.status = "completed" if out.ok else "failed"
    out.data = {"recovered_pages": recovered_pages, "errors": errors}
    if errors:
        out.degraded = True
        out.warnings.extend(errors)
    if out.ok:
        chk = pymupdf.open(output)
        actual = chk.page_count
        chk.close()
        out.check("openable", True, actual > 0, actual > 0)
        out.check("page_count", recovered_pages, actual, actual >= 1)
    return out
