---
name: UNIVERSAL_PDF
title: "Universal PDF Orchestrator"
category: "Orchestration"
version: 1.0.0
engine: "universal_pdf.orchestration.orchestrator"
related: "pdf-create, pdf-inspect, pdf-read, pdf-extract, pdf-ocr, pdf-tables, pdf-search, pdf-summarize, pdf-qa, pdf-merge, pdf-split, pdf-edit, pdf-redact, pdf-compress, pdf-repair, pdf-compare, pdf-batch"
---

# Universal PDF Orchestrator  (`UNIVERSAL_PDF`)

This is the **SYSTEM MODE** entry point for the Universal PDF Management &
Creation Skill Repository. It is not a PDF operation itself; it decides which
individual skills (below) are needed and runs them in the right order. Every
individual skill is also callable directly (**INDIVIDUAL MODE**) — do not route
trivial single-step requests through the full pipeline.

## Decision procedure (for an agent)
1. **Identify the input(s).** Are there PDF files, or data/images to turn into
   a PDF?
2. **Classify the intent** against the routing table (below) / the programmatic
   `route()` function.
3. **Respect capabilities & resources** before spending work:
   - Tiny text PDF + simple read → just `pdf-read`/`pdf-extract`.
   - Scanned/image-only pages (no text layer) → `pdf-ocr`; if no OCR engine,
     degrade and say so (never fabricate).
   - Vision requested (a chart/figure) → only use `pdf-vision` if a vision
     provider exists; otherwise fall back to text/OCR.
   - Huge file (thousands of pages) → use the knowledge store + chunking +
     index + retrieval (`pdf-document-state`, `pdf-chunk`, `pdf-index`,
     `pdf-search`, `pdf-qa`), never load it into context.
4. **Chain the minimum set of skills** for the goal.
5. **Validate** every step (each returns an `Outcome` with checks).
6. **Report** what succeeded, what degraded, and any limitations.

## Routing table
| Request | Skill chain |
|---|---|
| Read / “what does it say” | `pdf-inspect` → `pdf-read` |
| Summarize / main points | `pdf-inspect` → `pdf-summarize` |
| Find/mention/where is X | `pdf-search` (streamed for huge docs) |
| Extract tables / to Excel/CSV | `pdf-tables` → export |
| Scanned → searchable | `pdf-inspect` → `pdf-ocr` |
| Question over a document | `pdf-chunk`(+store) → `pdf-qa` (citation-grounded) |
| Merge | `pdf-merge` |
| Split / extract pages | `pdf-split` |
| Remove/reorder pages | `pdf-edit` / `pdf-reorder` |
| Rotate / crop / scale | `pdf-rotate` / `pdf-crop` / `pdf-scale` |
| Watermark / stamp / header/footer | `pdf-watermark` / `pdf-header-footer` |
| Annotate / highlight | `pdf-annotate` |
| Metadata / bookmarks / links / forms | `pdf-metadata` / `pdf-bookmarks` / `pdf-links` / `pdf-forms`(+fill) |
| Encrypt / decrypt / permissions | `pdf-encrypt` / `pdf-decrypt` / `pdf-permissions` |
| Redact (true removal + verify) | `pdf-redact` |
| Compress / optimize | `pdf-compress` / `pdf-optimize` (choose profile) |
| Repair / “won’t open” | `pdf-repair` |
| Convert / export | `pdf-convert` / `pdf-export` |
| Compare / diff versions | `pdf-compare` / `pdf-diff` |
| Many files at once | `pdf-batch` |
| Create a document/report | `pdf-create` (text/MD/HTML/images/data) |

## Programmatic orchestrator
```python
from universal_pdf.orchestration import orchestrator as o
plan = o.route("Merge and compress these", ["a.pdf", "b.pdf"])
res  = o.execute_plan(plan)          # inspect/plan first if you want control
# or all-in-one:
res  = o.handle_request("Compress this PDF", ["big.pdf"])
```

## Rules of engagement
- **Only run the capabilities the task needs.** No forced full pipeline.
- **Never claim success on a degraded/failed step.** Surface `Outcome.warnings`.
- **Provenance first**: for Q&A/summaries require the chain to keep page/source.
- **Stay inside the context budget** (`UPPDF_LLM_CONTEXT_CHARS`): use chunks,
  buckets and retrieval.
- **Batch**: process per-file with a checkpoint so an interruption resumes.

## Related
Browse every leaf skill in `skills/INDEX.md`; architecture in `../ARCHITECTURE.md`.
