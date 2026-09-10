"""Whole-system orchestration tests (SYSTEM MODE, requirement 29/30)."""
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from universal_pdf.orchestration import orchestrator as orch
from universal_pdf.core import state, qa


def test_routing():
    cases = [
        ("Read this PDF.", "pdf-inspect"),
        ("Summarize this book.", "pdf-summarize"),
        ("Merge these PDFs.", "pdf-merge"),
        ("Compress this PDF.", "pdf-compress"),
        ("Extract all tables to Excel.", "pdf-tables"),
        ("Redact these details.", "pdf-redact"),
        ("Remove pages 4,7 and 9.", "pdf-edit"),
    ]
    for req, expect in cases:
        plan = orch.route(req, files=["f.pdf"] * 2)
        assert any(p["skill"] == expect for p in plan), (req, plan)


def test_execute_pipeline(text_pdf, tmp_path):
    # inspect -> summarize -> merge -> compress
    merged = str(tmp_path / "m.pdf")
    p1 = [{"skill": "pdf-inspect", "path": text_pdf},
          {"skill": "pdf-summarize", "path": text_pdf}]
    r1 = orch.execute_plan(p1)
    assert all(x["ok"] for x in r1)

    p2 = [{"skill": "pdf-merge", "inputs": [text_pdf, text_pdf],
           "output": merged},
          {"skill": "pdf-compress", "path": merged,
           "output": str(tmp_path / "mc.pdf")}]
    r2 = orch.execute_plan(p2)
    assert all(x["ok"] for x in r2)
    assert os.path.exists(str(tmp_path / "mc.pdf"))


def test_handle_request_full(text_pdf, tmp_path):
    req = {"request": "Read this PDF and summarize it.",
           "plan": [{"skill": "pdf-inspect", "path": text_pdf},
                    {"skill": "pdf-summarize", "path": text_pdf}]}
    res = orch.handle_request("Summarize this PDF", [text_pdf])
    assert res["success"]
    assert any(r["skill"] == "pdf-summarize" for r in res["results"])


def test_qa_with_knowledge_store(text_pdf, tmp_path):
    """QA grounds the answer in retrieved, cited chunks (never the whole doc)."""
    db = tmp_path / "kb.db"
    store = state.DocumentStore(db)
    from universal_pdf.core import chunk as ch
    did = store.register_document(text_pdf,
                                  page_count=0)
    ch.chunk_document(text_pdf, per_page=True, store_doc_id=did,
                      page_store=store)

    # evidence mode (no reasoning model)
    ret = qa.retrieve(did, "unique_needle_phrase", store=store)
    assert ret.ok and ret.data["retrieved_pages"] >= 1
    ans = qa.answer(did, "unique_needle_phrase", store=store, reasoning=None)
    assert ans.data["citations"], "expected citations to pages"
    store.close()
