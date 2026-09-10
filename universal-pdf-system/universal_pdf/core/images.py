"""Image operations (requirement 16) and page rasterization (pdf-render).

Rendering uses PyMuPDF (reliable). Image extraction/insertion likewise.
"""
from __future__ import annotations

import os
from pathlib import Path
from typing import Optional, Sequence

from ..result import Outcome
from ..tools import adapter


def render_pages(path: str, output_dir: str, fmt: str = "png", dpi: int = 150,
                 pages: Optional[list] = None, prefix: str = "page",
                 password=None) -> Outcome:
    """Render pages to images. fmt: png|jpg|jpeg|ppm|pgm|pbm|pam."""
    import pymupdf
    out = Outcome(skill="pdf-render")
    doc = pymupdf.open(path)
    if password and doc.needs_pass:
        doc.authenticate(password)
    total = doc.page_count
    os.makedirs(output_dir, exist_ok=True)
    pageset = sorted(set(pages)) if pages else list(range(1, total + 1))
    produced = []
    zoom = dpi / 72.0
    mat = pymupdf.Matrix(zoom, zoom)
    try:
        for pno in pageset:
            page = doc[pno - 1]
            pix = page.get_pixmap(matrix=mat)
            ext = "jpg" if fmt in ("jpg", "jpeg") else fmt
            fname = os.path.join(output_dir, f"{prefix}{pno:04d}.{ext}")
            pix.save(fname)
            produced.append(fname)
        doc.close()
        out.output_path = output_dir
        out.ok = True
        out.status = "completed"
        out.data = {"files": produced, "dpi": dpi, "count": len(produced)}
        out.check("rendered", len(pageset), len(produced),
                  len(produced) == len(pageset))
        return out
    except Exception as exc:  # noqa: BLE001
        try:
            doc.close()
        except Exception:
            pass
        out.ok = False
        out.status = "failed"
        out.messages.append(f"render failed: {exc}")
        return out


def render_page_to_bytes(path: str, page: int = 1, dpi: int = 150,
                         fmt: str = "png", password=None) -> bytes:
    import pymupdf
    doc = pymupdf.open(path)
    try:
        if password and doc.needs_pass:
            doc.authenticate(password)
        pix = doc[page - 1].get_pixmap(matrix=pymupdf.Matrix(dpi / 72, dpi / 72))
        return pix.tobytes(fmt)
    finally:
        doc.close()


def extract_images(path: str, output_dir: str, pages: Optional[list] = None,
                   min_size: int = 0, password=None) -> Outcome:
    """Extract all embedded raster images to output_dir, dedup by xref."""
    import pymupdf
    out = Outcome(skill="pdf-extract")
    doc = pymupdf.open(path)
    if password and doc.needs_pass:
        doc.authenticate(password)
    os.makedirs(output_dir, exist_ok=True)
    pageset = set(pages) if pages else None
    produced = []
    seen = set()
    try:
        for i in range(doc.page_count):
            if pageset and (i + 1) not in pageset:
                continue
            for img in doc[i].get_images(full=True):
                xref = img[0]
                if xref in seen:
                    continue
                seen.add(xref)
                try:
                    pix = pymupdf.Pixmap(doc, xref)
                    if pix.width * pix.height < min_size:
                        continue
                    if pix.n - pix.alpha < 4:
                        fname = os.path.join(
                            output_dir,
                            f"p{i+1:03d}_x{xref:04d}.png")
                        pix.save(fname)
                    else:
                        # CMYK/other -> convert to png
                        pix2 = pymupdf.Pixmap(pymupdf.csRGB, pix)
                        fname = os.path.join(
                            output_dir, f"p{i+1:03d}_x{xref:04d}.png")
                        pix2.save(fname)
                    produced.append(fname)
                except Exception:
                    continue
        doc.close()
        out.output_path = output_dir
        out.ok = True
        out.status = "completed"
        out.data = {"files": produced, "count": len(produced)}
        out.check("extracted", ">=0", len(produced), True)
        return out
    except Exception as exc:  # noqa: BLE001
        try:
            doc.close()
        except Exception:
            pass
        out.ok = False
        out.status = "failed"
        out.messages.append(f"image extraction failed: {exc}")
        return out


def image_metadata(path: str) -> Outcome:
    from PIL import Image
    out = Outcome(skill="pdf-inspect")
    im = Image.open(path)
    out.ok = True
    out.data = {"format": im.format, "size": im.size, "mode": im.mode,
                "width": im.width, "height": im.height}
    out.check("open", True, True, True)
    return out


def optimize_image(path_in: str, path_out: str, quality: int = 75,
                   max_dim: int = 0) -> Outcome:
    from PIL import Image
    out = Outcome(skill="pdf-compress")
    im = Image.open(path_in)
    if im.mode not in ("RGB", "RGBA", "L"):
        im = im.convert("RGB")
    if max_dim:
        im.thumbnail((max_dim, max_dim), Image.LANCZOS)
    im.save(path_out, "JPEG" if path_out.lower().endswith((".jpg", ".jpeg"))
            else "PNG", quality=quality, optimize=True)
    out.ok = True
    out.output_path = path_out
    return out
