---
name: pdf-extract
title: "Extract text/structure with provenance"
category: "PDF Management"
version: 1.0.0
engine: "core.extract:extract_text / extract_blocks_per_page / extract_per_page"
preferred_tool: "PyMuPDF text (text/dict)"
fallback_tool: "pdfplumber (column layout)"
validation: "text_coverage; page coverage"
---
# Extract text/structure with provenance  (`pdf-extract`)

Extract text/structure with provenance

> Part of the **Universal PDF Management & Creation Skill Repository**.
> Category: **PDF Management**.
> Every skill is individually callable (INDIVIDUAL MODE) and may also be
> invoked automatically by the orchestrator (SYSTEM MODE).

## When to use
Extract structured content while keeping page & position so downstream steps can cite sources.

## Operations
- extract text
- per-page blocks with bbox
- multi-column via layout
- preserve page/position info
- image-only pages routed to OCR

## Engine (what actually executes this)
`universal_pdf/core.extract:extract_text / extract_blocks_per_page / extract_per_page`

All heavy lifting is done on disk / one page at a time by the shared engine —
never by loading the document into an LLM context.

## Tools & graceful degradation
- Preferred tool: **PyMuPDF text (text/dict)**
- Fallback: **pdfplumber (column layout)**

If the preferred backend is unavailable the skill transparently uses the
fallback or reports a documented limitation. It **never** reports success when
an operation did not actually happen.

## Validation (this skill attaches checks to its Outcome)
text_coverage; page coverage

## Related skills
`pdf-read`, `pdf-tables`, `pdf-ocr`, `pdf-provenance`

## Example requests it handles
  * "Extract all the body text of this report keeping page numbers."

## Notes
Provenance: outputs cite their source page/section where relevant.
