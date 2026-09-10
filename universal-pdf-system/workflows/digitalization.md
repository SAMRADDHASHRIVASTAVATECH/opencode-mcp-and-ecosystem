# Workflow: Digitalization pipeline (scanned docs → searchable & structured)

**Goal:** process a scanned folder into searchable, table-aware, indexed PDFs.

**Skills:** `pdf-inspect` → `pdf-ocr` → `pdf-extract`/`pdf-tables` →
`pdf-document-state`/`pdf-index` → `pdf-search`/`pdf-qa`.

## Steps
1. **Inspect each file.** Note page count and `has_text_layer`.
2. **Route:** pages with no usable text layer need OCR; text pages are skipped
   (`pdf-ocr` never OCRs pages that already have text).
3. If OCR is unavailable, degrade with a clear note (never claim success).
4. Extract text/tables from the (now searchable) result.
5. Register in the knowledge store and chunk/index for later retrieval.

## Concrete calls
```python
from universal_pdf.core import ocr, inspect, extract, tables, chunk, state

for src in ["scan1.pdf", "scan2.pdf"]:
    prof = inspect.inspect(src).data
    need  = extract.detect_text_layer(src)
    if need["needs_ocr"]:
        r = ocr.make_searchable(src, src.replace(".pdf", "_srch.pdf"))
        if not r.ok:            # degraded — report and continue
            print("OCR unavailable for", src); continue
        work = r.output_path
    else:
        work = src
    t = tables.extract_tables(work)
    store = state.DocumentStore("knowledge/store.db")
    did = store.register_document(work, page_count=prof["page_count"])
    chunk.chunk_document(work, store_doc_id=did, page_store=store, per_page=True)
```

## Output
A folder of searchable PDFs plus a knowledge DB that supports `pdf-search`,
`pdf-qa` (citation-grounded) and `pdf-summarize` without re-parsing.
