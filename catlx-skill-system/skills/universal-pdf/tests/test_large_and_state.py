"""Large-document streaming + external state + resumable processing tests
(requirements 10, 11, 28, 33, 34)."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import pymupdf

from universal_pdf.core import extract, search, checkpoint, state


def _build_large(tmp_path, pages=1200, token="needle"):
    """Build a moderately large PDF cheaply by page replication."""
    seed = tmp_path / "seed.pdf"
    d = pymupdf.open()
    p = d.new_page()
    p.insert_text((50, 80), f"line with {token}_special_term and filler")
    p.insert_text((50, 100), "second line of content words")
    d.save(str(seed))
    d.close()
    acc = str(tmp_path / "large.pdf")
    import shutil
    shutil.copy(str(seed), acc)
    while pymupdf.open(acc).page_count < pages:
        src = pymupdf.open(acc)
        n = src.page_count
        dst = pymupdf.open(acc)
        dst.insert_pdf(src, from_page=0, to_page=n - 1)
        dst.save(str(tmp_path / "t.pdf"))
        dst.close()
        src.close()
        shutil.move(str(tmp_path / "t.pdf"), acc)
    return acc


def test_streaming_extraction_single_page(tmp_path):
    p = _build_large(tmp_path, pages=800)
    # extract one page without loading all
    t = extract.extract_text(p, pages=[400])
    assert "special_term" in t


def test_streaming_mention_scan(tmp_path):
    p = _build_large(tmp_path, pages=600, token="needle")
    o = search.find_mentions_all(p, "needle_special_term")
    assert o.data["pages_total"] >= 600
    assert o.data["pages_with_hits"] == o.data["pages_total"]


def test_checkpoint_resume(tmp_path):
    cp = checkpoint.Checkpoint(tmp_path / "ck.json")
    units = [f"p{i}" for i in range(20)]
    done = set()

    def step(u):
        done.add(u)
        if len(done) == 7:
            raise InterruptedError("simulated crash")

    summary = cp.run(units, step)
    assert summary["failed"] == 1
    # resume: only pending/failed rerun; completed skipped
    summary2 = cp.run(units, step)
    assert summary2["skipped"] >= 6  # previously completed were skipped
    assert cp.completed() == units


def test_knowledge_store_persistence(tmp_path):
    s = state.DocumentStore(tmp_path / "kb.db")
    did = s.register_document("/tmp/fake.pdf", page_count=3,
                              title="Fake")
    s.put_page(did, 1, "hello world")
    s.put_chunk(did, "c1", 1, 0, "hello world")
    s.set_meta(did, "author", "me")
    s.mark(did, "inspect", "completed")
    assert s.page( did, 1)["text"] == "hello world"
    assert s.status(did, "inspect") == "completed"
    # reload store from same file to prove persistence
    s.close()
    s2 = state.DocumentStore(tmp_path / "kb.db")
    assert s2.get_document(did)["title"] == "Fake"
    s2.close()
