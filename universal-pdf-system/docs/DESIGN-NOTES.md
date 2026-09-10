# Design notes: scaling, weak models, state, and recovery

This document explains the engineering decisions that make the system work for
**1→10,000+ page PDFs**, **small/local models**, and **flaky environments**.

## 1. Nothing large ever enters the model context
- `core/extract.iter_page_text()` yields one page at a time (generator). Search,
  mention scans and summaries consume pages as a stream and keep only small
  aggregates/hits.
- `core/chunk.chunk_document()` cuts documents into page-scoped or size-bounded
  chunks (with overlap) that are small enough for any model. A prompt/QA layer
  is fed *retrieved* chunks only.

## 2. External state instead of model memory
- `core/state.DocumentStore` is a SQLite knowledge base holding per-document
  records: pages, chunks, tables, images, sections, metadata, pipeline step
  status, summaries, validation and errors. A later operation can ask the store
  for a page without re-parsing the file.
- `core/provenance` anchors derived items to a stable `document_id` (content
  fingerprint) plus page/section/method, so answers can be cited.

## 3. Resource-aware strategy
- Before expensive work, `core/resource.strategy()` looks at page count, file
  size, text-layer presence and the host profile and decides: whole-load vs
  batched streaming, whether OCR is truly needed, whether to build an index,
  and the page batch size. Simple cases never pay for heavy machinery.

## 4. Resumable processing (checkpoints)
- `core/checkpoint.Checkpoint` tracks per-unit status:
  `pending → processing → completed / failed → (retry) → validated`. If a
  batch dies mid-way it restarts and skips completed units. Used by long
  pipelines and `pdf-batch`.

## 5. Weak-model adaptation
- Context budget is configurable (`UPPDF_LLM_CONTEXT_CHARS`). `summarize` and
  `qa` guarantee their output/retrieval stays inside it by construction.
- Abstractive text generation is optional: local *extractive* summarization
  runs with no model at all; a reasoning/vision provider is injected when the
  host agent has one.

## 6. Graceful degradation contract
- Backends are probed once and cached (`core/tools/adapter.py`). Absent tools →
  documented fallback; absent capability → `Outcome(ok=False, degraded=True)`
  with a precise message. Every engine call runs post-condition validation and
  reports the checks, so an upstream agent can trust `Outcome.ok`.

## 7. Recovery
- `core/repair` diagnoses openability/page-tree/renderability, re-serialises the
  object graph (garbage collection rebuilds cross-references), and, if the page
  tree is corrupt, rescues content page-by-page into a fresh document — then
  reports exactly how many pages were recovered and what could not be.

## 8. Why PyMuPDF as the preferred backend
Single richest library covering text, structure, annotations, forms, redaction,
encryption, rendering and compression. pdfplumber/pypdf/reportlab are used only
where they are strictly better (layout/table fidelity, pure-structural/crypto,
and creation respectively). This keeps the code portable and lets any one
backend fail open.
