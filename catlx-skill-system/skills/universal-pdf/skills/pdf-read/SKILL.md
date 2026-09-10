---
name: pdf-read
title: "Universal text reading"
category: "PDF Management"
version: 1.0.0
engine: "core.extract:extract_text / extract_per_page / iter_page_text / detect_text_layer"
preferred_tool: "PyMuPDF text layer"
fallback_tool: "pdfplumber (layout text)"
validation: "text_coverage; page coverage"
---
# Universal text reading  (`pdf-read`)

Universal text reading

> Part of the **Universal PDF Management & Creation Skill Repository**.
> Category: **PDF Management**.
> Every skill is individually callable (INDIVIDUAL MODE) and may also be
> invoked automatically by the orchestrator (SYSTEM MODE).

## When to use
Pull readable text out of a digital PDF without loading it into the model.

## Operations
- read full text
- read selected pages
- read preserving page boundaries
- stream huge documents page-by-page
- detect whether OCR needed

## Engine (what actually executes this)
`universal_pdf/core.extract:extract_text / extract_per_page / iter_page_text / detect_text_layer`

All heavy lifting is done on disk / one page at a time by the shared engine —
never by loading the document into an LLM context.

## Tools & graceful degradation
- Preferred tool: **PyMuPDF text layer**
- Fallback: **pdfplumber (layout text)**

If the preferred backend is unavailable the skill transparently uses the
fallback or reports a documented limitation. It **never** reports success when
an operation did not actually happen.

## Validation (this skill attaches checks to its Outcome)
text_coverage; page coverage

## Related skills
`pdf-extract`, `pdf-inspect`, `pdf-ocr`, `pdf-search`, `pdf-orchestrate`

## Example requests it handles
  * "Read this PDF and tell me the main points."
  * "Show me the text on pages 4 and 7."

## Notes
Provenance: outputs cite their source page/section where relevant.
