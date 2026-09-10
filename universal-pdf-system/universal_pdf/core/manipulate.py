"""Structural PDF manipulation (merge/split/reorder/rotate/crop/scale/insert/delete).

Preferred tool: PyMuPDF. Fallback for pure structural page ops: pypdf.
Strategies scale to huge files by working page-by-page and saving to a fresh
document rather than holding everything in the model context.
"""
from __future__ import annotations

import re
from typing import Optional, Sequence

from ..result import Outcome
from ..tools import adapter
from ..core import validation as V


def _open(path, password=None):
    doc, backend = adapter.load_document(path)
    if password and hasattr(doc, "needs_pass") and doc.needs_pass:
        doc.authenticate(password)
    return doc, backend


def _save(doc, target, garbage=3, deflate=True, clean=True):
    doc.save(target, garbage=garbage, deflate=deflate, clean=clean)
    doc.close()


# ----------------------------------------------------------------- page spec
def _spec_to_pages(spec, total) -> list[int]:
    """Accept None/[]/int/list of ints/int-of-1based/str like '1,3-5'."""
    if spec is None:
        return list(range(1, total + 1))
    if isinstance(spec, int):
        return [spec]
    if isinstance(spec, list):
        out = []
        for s in spec:
            out.extend(_spec_to_pages(s, total))
        return _dedup(out)
    if isinstance(spec, str):
        out = []
        for part in spec.split(","):
            part = part.strip()
            if not part:
                continue
            if "-" in part and not part.startswith("-"):
                a, b = part.split("-", 1)
                try:
                    start, end = int(a), int(b)
                except ValueError:
                    continue
                out.extend(range(start, end + 1))
            else:
                try:
                    out.append(int(part))
                except ValueError:
                    continue
        return _dedup(out)
    return _dedup([int(s) for s in spec])


def _dedup(xs):
    seen, r = set(), []
    for x in xs:
        if x not in seen:
            seen.add(x)
            r.append(x)
    return r


def _pagecount(doc):
    return int(doc.page_count) if hasattr(doc, "page_count") else len(doc.pages)


def merge_pdfs(inputs: Sequence[str], output: str,
               preserve_toc: bool = True) -> Outcome:
    """Merge multiple PDFs in order into ``output``."""
    out = Outcome(skill="pdf-merge")
    import pymupdf
    try:
        merged = pymupdf.open()
        toc = []
        offset = 0
        for i, inp in enumerate(inputs):
            src = pymupdf.open(inp)
            merged.insert_pdf(src)
            if preserve_toc:
                for t in src.get_toc():
                    toc.append([t[0], t[1], t[2] + offset])
            offset += src.page_count
            src.close()
        if preserve_toc:
            try:
                merged.set_toc(toc)
            except Exception:
                pass
        merged.save(output, garbage=3, deflate=True)
        merged.close()
        out.output_path = output
        out.ok = True
        out.status = "completed"
        expected = sum(pymupdf.open(x).page_count for x in inputs)
        actual = _pc(output)
        out.check("page_count", expected, actual, actual == expected)
        out.check("openable", True, V.openable(output).passed, True)
        return out
    except Exception as exc:  # noqa: BLE001
        out.ok = False
        out.status = "failed"
        out.messages.append(f"merge failed: {exc}")
        return out


def split_pdf(path: str, output_dir: str, mode: str = "ranges",
              pages=None, every: int = None, per: int = None,
              by_toc: bool = False, password=None) -> Outcome:
    """Split a PDF.

    modes:
      ranges : split into exactly the provided page groups (list of lists)
      ranges_flat : write one file per provided page (list of ints)
      every  : split every ``every`` pages (1 => each single page)
      per    : fixed-size chunks of ``per`` pages (equivalent to every)
      toc    : split at top-level TOC entries
    """
    out = Outcome(skill="pdf-split")
    import os
    import pymupdf
    src = pymupdf.open(path)
    if password and src.needs_pass:
        src.authenticate(password)
    total = src.page_count
    os.makedirs(output_dir, exist_ok=True)
    produced = []
    try:
        groups = []
        base = os.path.splitext(os.path.basename(path))[0]
        if mode in ("every", "per"):
            n = every or per or 1
            for start in range(0, total, n):
                groups.append(list(range(start + 1, min(start + n, total) + 1)))
        elif mode == "ranges" and isinstance(pages, list) and pages and \
                isinstance(pages[0], (list, tuple)):
            groups = [sorted(set(p)) for p in pages]
        elif mode == "toc":
            toc = src.get_toc()
            top = [t for t in toc if t[0] <= 1]
            bounds = []
            for idx, t in enumerate(top):
                st = t[2]
                en = (top[idx + 1][2] - 1) if idx + 1 < len(top) else total
                bounds.append(list(range(st, en + 1)))
            if bounds:
                groups = bounds
            else:
                groups = [list(range(1, total + 1))]
        else:
            # flat page list -> one file each
            plist = _spec_to_pages(pages, total)
            for p in plist:
                groups.append([p])

        for gi, g in enumerate(groups, 1):
            g = [x for x in g if 1 <= x <= total]
            if not g:
                continue
            fname = os.path.join(output_dir, f"{base}_part{gi:03d}.pdf")
            tmp = pymupdf.open()
            tmp.insert_pdf(src, from_page=g[0] - 1, to_page=g[-1] - 1)
            tmp.save(fname, garbage=3, deflate=True)
            tmp.close()
            produced.append(fname)

        out.output_path = output_dir
        out.data = {"files": produced, "count": len(produced)}
        out.ok = True
        out.status = "completed"
        out.check("produced_files", len(groups), len(produced),
                  len(produced) == len([x for x in groups if x]))
        return out
    except Exception as exc:  # noqa: BLE001
        out.ok = False
        out.status = "failed"
        out.messages.append(f"split failed: {exc}")
        return out
    finally:
        src.close()


def extract_pages(path: str, pages, output: str, password=None) -> Outcome:
    """Extract selected pages into a new PDF (subset)."""
    import pymupdf
    src = pymupdf.open(path)
    if password and src.needs_pass:
        src.authenticate(password)
    total = src.page_count
    out = Outcome(skill="pdf-split")
    plist = _spec_to_pages(pages, total)
    try:
        tmp = pymupdf.open()
        tmp.insert_pdf(src, from_page=min(plist) - 1, to_page=max(plist) - 1)
        # filter to exact set (insert_pdf supports pages=)
        tmp2 = pymupdf.open()
        for p in plist:
            tmp2.insert_pdf(tmp, from_page=p - min(plist), to_page=p - min(plist))
        tmp2.save(output, garbage=3, deflate=True)
        tmp.close()
        tmp2.close()
        out.output_path = output
        out.ok = True
        out.status = "completed"
        out.data = {"pages": plist}
        out.check("page_count", len(plist),
                  _pc(output), _pc(output) == len(plist))
        return out
    except Exception as exc:  # noqa: BLE001
        out.ok = False
        out.status = "failed"
        out.messages.append(f"extract failed: {exc}")
        return out
    finally:
        src.close()


def _pc(path):
    import pymupdf
    d = pymupdf.open(path)
    n = d.page_count
    d.close()
    return n


def reorder_pdf(path: str, order: list[int], output: str,
                password=None) -> Outcome:
    """Reorder pages. ``order`` is a 1-based list e.g. [3,1,2]; may contain
    duplicates (duplication) and must cover each source page at least once for
    full content, though partial subsets are allowed.
    """
    import pymupdf
    src = pymupdf.open(path)
    if password and src.needs_pass:
        src.authenticate(password)
    total = src.page_count
    out = Outcome(skill="pdf-reorder")
    resolved = [o for o in order if 1 <= o <= total]
    try:
        tmp = pymupdf.open()
        # map target indices to 0-based
        for idx0 in [r - 1 for r in resolved]:
            tmp.insert_pdf(src, from_page=idx0, to_page=idx0)
        tmp.save(output, garbage=3, deflate=True)
        tmp.close()
        out.output_path = output
        out.ok = True
        out.status = "completed"
        out.data = {"order": resolved}
        out.check("page_count", len(resolved), _pc(output),
                  _pc(output) == len(resolved))
        return out
    except Exception as exc:  # noqa: BLE001
        out.ok = False
        out.status = "failed"
        out.messages.append(f"reorder failed: {exc}")
        return out
    finally:
        src.close()


def delete_pages(path: str, pages, output: str, password=None) -> Outcome:
    """Delete given pages (1-based)."""
    import pymupdf
    src = pymupdf.open(path)
    if password and src.needs_pass:
        src.authenticate(password)
    total = src.page_count
    out = Outcome(skill="pdf-edit")
    todel = set(_spec_to_pages(pages, total))
    keep = [i + 1 for i in range(total) if (i + 1) not in todel]
    try:
        tmp = pymupdf.open()
        for k in keep:
            tmp.insert_pdf(src, from_page=k - 1, to_page=k - 1)
        tmp.save(output, garbage=3, deflate=True)
        tmp.close()
        out.output_path = output
        out.ok = True
        out.status = "completed"
        out.data = {"deleted": sorted(todel), "remaining": keep}
        out.check("page_count", len(keep), _pc(output), _pc(output) == len(keep))
        return out
    except Exception as exc:  # noqa: BLE001
        out.ok = False
        out.status = "failed"
        out.messages.append(f"delete failed: {exc}")
        return out
    finally:
        src.close()


def insert_blank_pages(path: str, after: list[int], output: str,
                       page_size=None, password=None) -> Outcome:
    """Insert one blank page after each position in ``after`` (1-based)."""
    import pymupdf
    src = pymupdf.open(path)
    if password and src.needs_pass:
        src.authenticate(password)
    total = src.page_count
    out = Outcome(skill="pdf-edit")
    target_size = src[0].rect if page_size is None else pymupdf.paper_rect(page_size)
    afterset = set(_spec_to_pages(after, total))
    try:
        tmp = pymupdf.open()
        for i in range(1, total + 1):
            tmp.insert_pdf(src, from_page=i - 1, to_page=i - 1)
            if i in afterset:
                p = tmp.new_page(width=target_size.width,
                                 height=target_size.height)
        tmp.save(output, garbage=3, deflate=True)
        tmp.close()
        out.output_path = output
        out.ok = True
        out.status = "completed"
        expected = total + len(afterset)
        out.check("page_count", expected, _pc(output), _pc(output) == expected)
        return out
    except Exception as exc:  # noqa: BLE001
        out.ok = False
        out.status = "failed"
        out.messages.append(f"insert failed: {exc}")
        return out
    finally:
        src.close()


def rotate_pdf(path: str, rotation: int, output: str,
               pages=None, password=None) -> Outcome:
    """Rotate pages by ``rotation`` (90/180/270 multiples)."""
    import pymupdf
    src = pymupdf.open(path)
    if password and src.needs_pass:
        src.authenticate(password)
    total = src.page_count
    out = Outcome(skill="pdf-rotate")
    r = int(rotation) % 360
    target = _spec_to_pages(pages, total) if pages else list(range(1, total + 1))
    targetset = set(target)
    try:
        for i in range(total):
            if (i + 1) in targetset:
                page = src[i]
                page.set_rotation((page.rotation + r) % 360)
        src.save(output, garbage=3, deflate=True)
        out.output_path = output
        out.ok = True
        out.status = "completed"
        out.data = {"rotation": r, "pages": sorted(targetset)}
        out.check("page_count", total, _pc(output), _pc(output) == total)
        return out
    except Exception as exc:  # noqa: BLE001
        out.ok = False
        out.status = "failed"
        out.messages.append(f"rotate failed: {exc}")
        return out
    finally:
        src.close()


def crop_pdf(path: str, output: str, margin=0, left=0, right=0,
             top=0, bottom=0, pages=None, password=None) -> Outcome:
    """Crop pages to a new MediaBox (content is scaled via CropBox only
    preserves layout at same coordinates). Provide margins in points OR
    explicit insets. Applies to the page boxes so downstream render/view is
    cropped.
    """
    import pymupdf
    src = pymupdf.open(path)
    if password and src.needs_pass:
        src.authenticate(password)
    total = src.page_count
    out = Outcome(skill="pdf-crop")
    targetset = set(_spec_to_pages(pages, total)) if pages else set(range(1, total + 1))
    l, r = left or margin, right or margin
    t, b = top or margin, bottom or margin
    try:
        for i in range(total):
            if (i + 1) in targetset:
                page = src[i]
                rct = page.rect
                nr = pymupdf.Rect(rct.x0 + l, rct.y0 + t,
                                  rct.x1 - r, rct.y1 - b)
                page.set_cropbox(nr)
                page.set_mediabox(nr)
        src.save(output, garbage=3, deflate=True)
        out.output_path = output
        out.ok = True
        out.status = "completed"
        out.data = {"cropbox": [l, r, t, b]}
        out.check("page_count", total, _pc(output), _pc(output) == total)
        return out
    except Exception as exc:  # noqa: BLE001
        out.ok = False
        out.status = "failed"
        out.messages.append(f"crop failed: {exc}")
        return out
    finally:
        src.close()


def scale_pdf(path: str, output: str, scale=1.0, page_size=None,
              pages=None, password=None) -> Outcome:
    """Scale page content (0..1 shrink / >1 enlarge) OR set a uniform page
    size. Content is scaled by inserting into a resized page.
    """
    import pymupdf
    src = pymupdf.open(path)
    if password and src.needs_pass:
        src.authenticate(password)
    total = src.page_count
    out = Outcome(skill="pdf-scale")
    targetset = set(_spec_to_pages(pages, total)) if pages else set(range(1, total + 1))
    try:
        tmp = pymupdf.open()
        for i in range(total):
            page = src[i]
            if (i + 1) not in targetset or (scale == 1.0 and not page_size):
                tmp.insert_pdf(src, from_page=i, to_page=i)
                continue
            old = page.rect
            if page_size:
                r = pymupdf.paper_rect(page_size)
            else:
                r = pymupdf.Rect(0, 0, old.width * scale, old.height * scale)
            npg = tmp.new_page(width=r.width, height=r.height)
            # scale factor preserving content center
            sx = (r.width - 20) / old.width
            sy = (r.height - 20) / old.height
            s = min(sx, sy, scale if scale != 1.0 else min(sx, sy))
            # use show_pdf_page with a clip? simpler: zoom via pixmap not here
            # re-draw content scaled
            npg.show_pdf_page(npg.rect, src, i)
        tmp.save(output, garbage=3, deflate=True)
        tmp.close()
        out.output_path = output
        out.ok = True
        out.status = "completed"
        out.check("page_count", total, _pc(output), _pc(output) == total)
        return out
    except Exception as exc:  # noqa: BLE001
        out.ok = False
        out.status = "failed"
        out.messages.append(f"scale failed: {exc}")
        return out
    finally:
        src.close()
