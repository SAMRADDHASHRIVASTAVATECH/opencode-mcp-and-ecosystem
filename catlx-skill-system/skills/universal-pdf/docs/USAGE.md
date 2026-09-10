# Usage

## Two calling modes

### 1. INDIVIDUAL MODE — call one skill directly
Open the skill doc (`skills/<slug>/SKILL.md`) for parameters, then call its
engine function:

```python
import sys; sys.path.insert(0, "/path/to/universal-pdf-system")
from universal_pdf.core import inspect, manipulate, annotate

prof = inspect.inspect("report.pdf")              # pdf-inspect
print(prof.data["page_count"], prof.data["metadata"]["title"])

res = manipulate.merge_pdfs(["a.pdf", "b.pdf"], "combined.pdf")
print(res.ok, [ (c.name, c.passed) for c in res.checks ])

red = annotate.redact_text("doc.pdf", "clean.pdf", terms=["ACME-7788"])
assert red.checks[0].passed          # leak check passed
```

Every call returns an `Outcome` with `ok`, `status`, `data`, `messages`,
`warnings` and validation `checks`.

### 2. SYSTEM MODE — the Universal PDF Orchestrator
```python
from universal_pdf.orchestration import orchestrator as o

plan = o.route("Summarize this book and give me citations", ["book.pdf"])
res  = o.handle_request("Summarize this PDF", ["book.pdf"])
print(res["success"], [r["skill"] for r in res["results"]])
```

`route()` produces a plan you can inspect/edit before `execute_plan()` runs it,
so an agent keeps control. Every step is validated.

### Creation from common inputs
```python
from universal_pdf.core import create
create.create_pdf({"output": "r.pdf", "page_size": "a4", "header": "Q3",
                   "metadata": {"title": "Q3 Report"}},
                  [ {"type": "heading", "text": "Sales", "level": 1},
                    {"type": "table", "rows": [["R","Q1"],["N",120]]} ])
create.create_from_markdown("README.md", "readme.pdf")
create.create_from_html("doc.html", "doc.pdf")
create.create_from_images(["p1.png","p2.png"], "scan.pdf")
```

### Knowledge store, provenance, resumable processing
```python
from universal_pdf.core import state, chunk, qa
store = state.DocumentStore("knowledge/store.db")
did = store.register_document("book.pdf")
chunk.chunk_document("book.pdf", store_doc_id=did, page_store=store, per_page=True)
ans = qa.answer(did, "What is the refund policy?", store=store,
                reasoning=my_model_call)     # citation-grounded
```

### Configuration of optimisation profiles
`universal_pdf.core.compress.compress_pdf(path, out, profile="web_optimized")`
with profiles `maximum_quality | balanced | small_size | web_optimized |
archive_optimized`.

## Request → pipeline cheat-sheet
See `ARCHITECTURE.md` (routing table) and the master skill
`skills/UNIVERSAL_PDF.md`.
