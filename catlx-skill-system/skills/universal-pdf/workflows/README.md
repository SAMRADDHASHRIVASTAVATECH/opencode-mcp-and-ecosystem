# Reusable PDF workflows

These end-to-end recipes chain individual skills into complete, repeatable
pipelines. Each workflow is a Markdown plan you can hand to an agent (or the
orchestrator) plus the concrete engine calls.

| Workflow | Solves | Typical file |
|---|---|---|
| Professional report creation | data/text/images → branded multi-section PDF | `report-creation.md` |
| Digitalization pipeline | scanned folder → searchable, extracted, indexed | `digitalization.md` |
| Batch invoice processing | 100s of invoices → inspect/classify/metadata/compress/index/report | `batch-invoice-processing.md` |
| Secure redaction & publishing | find+remove sensitive content, verify, publish | `secure-redaction.md` |
| Merge → watermark → compress | combine documents, mark them, shrink for delivery | `merge-watermark-compress.md` |
| Large-document Q&A (10k pages) | index + retrieve + cite answers on huge files | `large-doc-qa.md` |

General principles that apply to every workflow:
1. **Inspect first** (`pdf-inspect`) so you know page count, text-layer health,
   size and encryption before choosing a strategy.
2. **Do the minimum.** Route by intent; don't OCR a text PDF.
3. **Validate after** each transformation (page counts, leak checks, openability).
4. **Keep state externally** for huge or batched jobs so you can resume.
