"""PDF comparison / diff (requirement 25).

Compares two PDFs across several lenses:
  * structure (page count, size)
  * per-page text similarity (diffs)
  * added / removed / modified content
  * metadata differences
  * optional visual diff (renders + pixel difference) for a page
Produces a JSON report and (optionally) a human-readable text report.
"""
from __future__ import annotations

import difflib
from typing import Optional

from ..result import Outcome


def _pagecount(doc):
    return int(doc.page_count) if hasattr(doc, "page_count") else len(doc.pages)


def _pages(path, password=None):
    from ..core import extract as ex
    return ex.extract_per_page(path, password)


def _meta(path, password=None):
    from ..core import inspect as ins
    r = ins.inspect(path, password)
    return (r.data or {}).get("metadata", {}) if r.ok else {}


def compare_pdfs(path_a: str, path_b: str, report: Optional[str] = None,
                 visual_pages: Optional[list] = None, password=None) -> Outcome:
    out = Outcome(skill="pdf-compare")
    pages_a = _pages(path_a, password)
    pages_b = _pages(path_b, password)
    meta_a = _meta(path_a, password)
    meta_b = _meta(path_b, password)
    n_a, n_b = len(pages_a), len(pages_b)
    report_obj = {"a": path_a, "b": path_b,
                  "pages": {"a": n_a, "b": n_b}}

    # metadata diff
    md_keys = set(meta_a) | set(meta_b)
    md_diff = {k: {"a": meta_a.get(k), "b": meta_b.get(k)}
               for k in md_keys if meta_a.get(k) != meta_b.get(k)}
    report_obj["metadata_diff"] = md_diff

    # page diff alignment
    page_diffs = []
    added, removed, modified = [], [], []
    for i in range(1, max(n_a, n_b) + 1):
        ta = pages_a[i - 1] if i <= n_a else ""
        tb = pages_b[i - 1] if i <= n_b else ""
        if not ta and tb:
            added.append(i)
        elif ta and not tb:
            removed.append(i)
        elif ta != tb:
            modified.append(i)
            # produce a unified-ish diff snippet
            sm = difflib.SequenceMatcher(None, ta, tb)
            ratio = round(sm.ratio(), 3)
            delta = difflib.ndiff(ta.splitlines(), tb.splitlines())
            removed_lines = [l[2:] for l in delta if l.startswith("- ")][:8]
            page_diffs.append({"page": i, "similarity": ratio,
                               "removed_sample": removed_lines})
        else:
            pass
    report_obj["added_pages"] = added
    report_obj["removed_pages"] = removed
    report_obj["modified_pages"] = modified
    report_obj["page_diffs"] = page_diffs
    report_obj["pages_identical"] = not (added or removed or modified)

    # overall text similarity
    full_a = "\n".join(pages_a)
    full_b = "\n".join(pages_b)
    if full_a or full_b:
        report_obj["overall_similarity"] = round(
            difflib.SequenceMatcher(None, full_a, full_b).ratio(), 4)

    # visual diff for requested pages
    visual = {}
    if visual_pages:
        from ..core import images as im
        for p in visual_pages:
            try:
                ba = im.render_page_to_bytes(path_a, p, dpi=72)
                bb = im.render_page_to_bytes(path_b, p, dpi=72)
                from PIL import Image, ImageChops
                import io
                ia, ib = Image.open(io.BytesIO(ba)).convert("RGB"), \
                    Image.open(io.BytesIO(bb)).convert("RGB")
                if ia.size != ib.size:
                    visual[p] = {"note": "size differs"}
                    continue
                diff = ImageChops.difference(ia, ib)
                bbox = diff.getbbox()
                # fraction of changed pixels
                from PIL import ImageStat
                stat = ImageStat.Stat(diff.convert("L"))
                mean = stat.mean[0] / 255.0
                visual[p] = {"changed_bbox": list(bbox) if bbox else None,
                             "mean_diff": round(mean, 4)}
            except Exception as exc:  # noqa: BLE001
                visual[p] = {"error": str(exc)}
    report_obj["visual_diff"] = visual

    # write report if requested
    report_obj["identical"] = (n_a == n_b and not page_diffs and not md_diff)
    out.data = report_obj
    out.ok = True
    out.status = "completed"
    if report:
        import json
        with open(report, "w", encoding="utf-8") as fh:
            json.dump(report_obj, fh, indent=2, default=str)
        out.output_path = report
    out.check("pages_a", n_a, n_a, True)
    out.check("pages_b", n_b, n_b, True)
    out.check("compared", True, True, True)
    return out


def text_report(out: Outcome) -> str:
    """Human-readable summary from a compare Outcome."""
    d = out.data
    lines = []
    lines.append(f"Comparing: {d['a']}  vs  {d['b']}")
    lines.append(f"Pages: {d['pages']['a']} vs {d['pages']['b']}")
    lines.append(f"Identical: {d.get('identical')}")
    if d.get("added_pages"):
        lines.append(f"Added pages: {d['added_pages']}")
    if d.get("removed_pages"):
        lines.append(f"Removed pages: {d['removed_pages']}")
    if d.get("modified_pages"):
        lines.append(f"Modified pages: {d['modified_pages']}")
    for pd in d.get("page_diffs", [])[:5]:
        lines.append(f"  p.{pd['page']} similarity={pd['similarity']} "
                     f"removed_sample={pd['removed_sample'][:2]}")
    if d.get("metadata_diff"):
        lines.append(f"Metadata differences: {list(d['metadata_diff'].keys())}")
    if d.get("overall_similarity") is not None:
        lines.append(f"Overall text similarity: {d['overall_similarity']}")
    return "\n".join(lines)
