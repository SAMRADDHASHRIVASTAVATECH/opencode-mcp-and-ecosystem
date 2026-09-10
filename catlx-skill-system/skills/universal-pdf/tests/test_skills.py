"""Broad functional tests across the individual skills (INDIVIDUAL MODE).

Each test drives one skill's engine function and asserts Outcome.ok plus the
relevant validation check. Covering tiny, large, table, image-only, encrypted,
merged/split/converted/generated/redacted/compressed PDFs (requirement 38).
"""
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from universal_pdf.core import (create, inspect, extract, manipulate, annotate,
                                meta, bookmarks, security, forms, images,
                                compress, tables, search, chunk, summarize,
                                convert, compare, repair, ocr, state)


# ------------------------------------------------------------------ creation
def test_create_text_and_markdown(text_pdf, tmp_path):
    from universal_pdf.core import create as C
    assert os.path.exists(text_pdf)
    # markdown creation
    md = tmp_path / "doc.md"
    md.write_text("# Title\n\nIntro paragraph here.\n\n- item one\n- item two\n")
    out = tmp_path / "md.pdf"
    o = C.create_from_markdown(str(md), str(out))
    assert o.ok
    # html
    h = tmp_path / "doc.html"
    h.write_text("<h1>Head</h1><p>Para text</p><table><tr><td>a</td><td>b</td></tr><tr><td>1</td><td>2</td></tr></table>")
    o = C.create_from_html(str(h), str(tmp_path / "h.pdf"))
    assert o.ok


def test_create_from_images(tmp_path):
    from PIL import Image
    im = Image.new("RGB", (300, 400), "navy")
    p = tmp_path / "a.png"
    im.save(p)
    o = create.create_from_images([str(p), str(p)], str(tmp_path / "img.pdf"))
    assert o.ok
    assert inspect.inspect(str(tmp_path / "img.pdf")).data["page_count"] == 2


# -------------------------------------------------------------- read/analyze
def test_inspect(text_pdf):
    o = inspect.inspect(text_pdf)
    assert o.ok and o.data["page_count"] >= 2
    assert "metadata" in o.data


def test_extract_and_text_layer(text_pdf):
    pages = extract.extract_per_page(text_pdf)
    assert len(pages) >= 2
    d = extract.detect_text_layer(text_pdf)
    assert d["has_text_layer"] is True and d["needs_ocr"] is False
    assert "unique_needle_phrase" in extract.extract_text(text_pdf)


def test_image_only_needs_ocr(image_only_pdf):
    d = extract.detect_text_layer(image_only_pdf)
    assert d["has_text_layer"] is False and d["needs_ocr"] is True


def test_ocr_degrades_gracefully(image_only_pdf):
    # no OCR backend expected in CI -> must degrade, not crash, not lie
    out = tmp = image_only_pdf + ".out.pdf"
    o = ocr.make_searchable(image_only_pdf, out)
    # If ocrmypdf is present this succeeds; otherwise degraded but never ok=True+fake
    if not ocr.ocr_available():
        assert o.degraded or (not o.ok)
        assert o.status in ("degraded", "failed")
    else:
        assert o.ok


def test_render_pages(text_pdf, tmp_path):
    d = tmp_path / "pages"
    o = images.render_pages(text_pdf, str(d), dpi=80)
    assert o.ok and len(o.data["files"]) >= 2
    assert os.path.exists(o.data["files"][0])


def test_tables(table_pdf, tmp_path):
    o = tables.extract_tables(table_pdf)
    assert o.ok and o.data["count"] >= 1
    csv = tables.tables_to_csv(o.data["tables"], str(tmp_path / "t.csv"))
    assert csv.ok
    xlsx = tables.tables_to_xlsx(o.data["tables"], str(tmp_path / "t.xlsx"))
    assert xlsx.ok and os.path.exists(str(tmp_path / "t.xlsx"))
    v = tables.validate_tables(o.data["tables"])
    assert v.ok


def test_search(text_pdf):
    o = search.search_document(text_pdf, "unique_needle_phrase", mode="phrase")
    assert o.ok and o.data["total"] >= 1
    m = search.find_mentions_all(text_pdf, "alpha")
    assert o.data["pages_total"] >= 2
    reg = search.search_document(text_pdf, r"needle_\w+", mode="regex")
    assert reg.data["total"] >= 1


def test_chunk_summarize(text_pdf, tmp_path):
    o = chunk.chunk_document(text_pdf, per_page=True)
    assert o.ok and o.data["chunks"] >= 2
    s = summarize.summarize(text_pdf, mode="extractive")
    assert s.ok and s.data["summary"]
    # persist to knowledge store
    db = tmp_path / "kb.db"
    store = state.DocumentStore(db)
    did = store.register_document(text_pdf, page_count=extract.detect_text_layer(text_pdf)["pages"])
    o2 = chunk.chunk_document(text_pdf, per_page=True, store_doc_id=did,
                              page_store=store)
    assert o2.ok
    assert store.page_count_in_store(did) >= 2
    store.close()


# -------------------------------------------------------------- manipulation
def test_merge_split_extract(text_pdf, tmp_path):
    o = manipulate.merge_pdfs([text_pdf, text_pdf], str(tmp_path / "m.pdf"))
    assert o.ok
    n2 = inspect.inspect(str(tmp_path / "m.pdf")).data["page_count"]
    assert n2 >= 4
    o = manipulate.extract_pages(str(tmp_path / "m.pdf"), [1, 2],
                                 str(tmp_path / "sub.pdf"))
    assert o.ok and o.data["pages"] == [1, 2]
    o = manipulate.split_pdf(text_pdf, str(tmp_path / "parts"), mode="every", every=1)
    assert o.ok and o.data["count"] >= 2


def test_reorder_delete_rotate_crop(text_pdf, tmp_path):
    total = inspect.inspect(text_pdf).data["page_count"]
    o = manipulate.reorder_pdf(text_pdf, list(reversed(range(1, total + 1))),
                               str(tmp_path / "rev.pdf"))
    assert o.ok
    o = manipulate.delete_pages(str(tmp_path / "rev.pdf"), [1],
                                str(tmp_path / "del.pdf"))
    assert o.ok and inspect.inspect(str(tmp_path / "del.pdf")).data["page_count"] == total - 1
    o = manipulate.rotate_pdf(text_pdf, 90, str(tmp_path / "rot.pdf"))
    assert o.ok
    o = manipulate.crop_pdf(text_pdf, str(tmp_path / "crop.pdf"), margin=36)
    assert o.ok


def test_watermark_header_annotate_redact(text_pdf, tmp_path):
    o = annotate.add_watermark(text_pdf, str(tmp_path / "wm.pdf"), text="DRAFT")
    assert o.ok
    o = annotate.add_header_footer(text_pdf, str(tmp_path / "hf.pdf"),
                                   header="H", footer="F", page_numbers=True)
    assert o.ok
    o = annotate.add_annotations(text_pdf, str(tmp_path / "an.pdf"),
                                 [{"type": "highlight", "page": 1,
                                   "rect": [70, 300, 300, 330]}])
    assert o.ok
    o = annotate.redact_text(text_pdf, str(tmp_path / "red.pdf"),
                             terms=["ACME-7788", "confidential"])
    assert o.ok
    # underlying content removal verified (leak check)
    assert o.checks[0].passed is True


def test_metadata_bookmarks_links(text_pdf, tmp_path):
    o = meta.set_metadata(text_pdf, str(tmp_path / "md.pdf"),
                          title="Renamed", author="Someone")
    assert o.ok
    assert inspect.inspect(str(tmp_path / "md.pdf")).data["metadata"]["title"] == "Renamed"
    o = bookmarks.set_bookmarks(text_pdf, str(tmp_path / "bm.pdf"),
                                [[1, "Intro", 1], [1, "Ch2", 2]])
    assert o.ok
    b = bookmarks.extract_bookmarks(text_pdf)
    assert b.ok
    lk = bookmarks.add_links(text_pdf, str(tmp_path / "lk.pdf"),
                             [{"page": 1, "rect": [70, 700, 200, 715],
                               "uri": "https://example.com"}])
    assert lk.ok
    e = bookmarks.extract_links(text_pdf)
    assert e.ok


# ---------------------------------------------------------------- security
def test_encrypt_decrypt(text_pdf, tmp_path):
    o = security.encrypt(text_pdf, str(tmp_path / "enc.pdf"),
                         user_password="pw123")
    assert o.ok
    enc = inspect.inspect(str(tmp_path / "enc.pdf")).data["security"]["encrypted"]
    assert enc is True
    o = security.decrypt(str(tmp_path / "enc.pdf"), str(tmp_path / "dec.pdf"),
                         password="pw123")
    assert o.ok
    assert inspect.inspect(str(tmp_path / "dec.pdf")).data["security"]["encrypted"] is False


def test_forms_detect_and_degrade(table_pdf):
    o = forms.list_fields(table_pdf)
    assert o.ok and o.data["is_form"] is False


def test_sign_inspect_degrade(text_pdf):
    o = security.inspect_signatures(text_pdf)
    assert o.ok and o.data["count"] == 0


# ----------------------------------------------------------------- convert
def test_compress_optimize(text_pdf, tmp_path):
    o = compress.compress_pdf(text_pdf, str(tmp_path / "comp.pdf"),
                              profile="small_size")
    assert o.ok
    # never larger
    assert o.data["final_bytes"] <= o.data["original_bytes"] or o.degraded


def test_convert_formats(text_pdf, tmp_path):
    for fmt, ext in [("txt", "txt"), ("markdown", "md"), ("html", "html"),
                     ("json", "json")]:
        o = convert.convert_pdf(text_pdf, str(tmp_path / f"out.{ext}"), fmt)
        assert o.ok and os.path.exists(str(tmp_path / f"out.{ext}")), fmt


def test_compare(text_pdf, tmp_path):
    a = text_pdf
    b = tmp_path / "tweaked.pdf"
    create.create_pdf({"output": str(b), "metadata": {"title": "Changed"}},
                      [{"type": "heading", "text": "Different", "level": 1},
                       {"type": "para", "text": "completely new body text."}])
    o = compare.compare_pdfs(a, str(b))
    assert o.ok
    assert "modified_pages" in o.data


def test_repair_diagnose(text_pdf):
    d = repair.diagnose(text_pdf)
    assert d.ok and d.data["openable"] is True
    o = repair.repair_pdf(text_pdf, text_pdf + ".repaired.pdf")
    assert o.ok


def test_forms_fill_on_fixture(tmp_path):
    """Fill the committed AcroForm fixture and confirm values persist."""
    from universal_pdf.core import forms
    fx = ROOT / "tests" / "fixtures" / "sample_form.pdf"
    f = forms.list_fields(str(fx))
    assert f.ok and f.data["is_form"] is True
    filled = forms.fill_form(str(fx), str(tmp_path / "filled.pdf"),
                             {"name": "Jane", "subscribe": True,
                              "email": "j@x.com"})
    assert filled.ok
    after = forms.list_fields(str(tmp_path / "filled.pdf"))
    vals = {x["name"]: x["value"] for x in after.data["fields"]}
    assert vals["name"] == "Jane" and vals["email"] == "j@x.com"
    # flatten is reported honestly (degrades if widgets cannot be removed)
    flat = forms.flatten_form(str(tmp_path / "filled.pdf"),
                              str(tmp_path / "flat.pdf"))
    assert flat.degraded or (flat.ok and flat.checks[0].passed)
