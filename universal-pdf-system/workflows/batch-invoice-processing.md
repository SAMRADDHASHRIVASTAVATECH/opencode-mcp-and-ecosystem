# Workflow: Batch invoice processing (many files)

**Goal:** process a folder of PDFs with a repeatable pipeline that never holds
every document in context: inspect → classify → rename → metadata → compress →
index → report.

**Skills:** `pdf-batch`, with per-file calls to `pdf-inspect`, `pdf-tables`,
`pdf-metadata`, `pdf-compress`, `pdf-document-state`, plus `pdf-validation`.

## Steps
1. Enumerate input files.
2. For each file (streamed, one at a time):
   a. `inspect` → page count, size, text layer.
   b. `tables.extract_tables` (if it is an invoice, find total rows).
   c. choose a classification (invoice/letter/report) by heuristics.
   d. rename to a canonical name; write metadata (title, author, a `Type` key).
   e. optionally compress.
   f. record progress in a **checkpoint** so an interruption resumes.
3. Aggregate a report (file → page count → size → status → checks).

## Concrete calls
```python
import os, json
from pathlib import Path
from universal_pdf.core import inspect, tables, meta, compress, checkpoint

ck = checkpoint.Checkpoint("workflows/_batch_ck.json")
files = sorted(Path("inbox").glob("*.pdf"))
report = []

def handle(fp):
    src = str(fp)
    p = inspect.inspect(src).data
    t = tables.extract_tables(src)
    n_tables = t.data["count"] if t.ok else 0
    kind = "invoice" if n_tables else "document"
    out = f"out/{fp.stem}_{kind}.pdf"
    meta.set_metadata(src, out, title=fp.stem, extra={"docType": kind})
    report.append({"file": src, "pages": p["page_count"],
                   "size": p["size_bytes"], "kind": kind, "tables": n_tables})

summary = ck.run([str(f) for f in files], handle, only_pending=True)
json.dump(report, open("out/batch_report.json", "w"), indent=2)
print(summary)   # completed/failed/skipped
```
Running the script again resumes any failed/skipped files automatically.
