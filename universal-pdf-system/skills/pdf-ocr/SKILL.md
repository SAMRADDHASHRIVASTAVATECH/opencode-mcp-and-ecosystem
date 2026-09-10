---
name: pdf-ocr
title: "OCR scanned / image-only pages"
category: "PDF Management"
version: 1.0.0
engine: "core.ocr:detect_ocr_need / make_searchable / ocr_page_text"
preferred_tool: "ocrmypdf (add searchable layer)"
fallback_tool: "pytesseract+tesseract / easyocr (page text)"
validation: "OCR completeness; output openable"
---
# OCR scanned / image-only pages  (`pdf-ocr`)

OCR scanned / image-only pages

> Part of the **Universal PDF Management & Creation Skill Repository**.
> Category: **PDF Management**.
> Every skill is individually callable (INDIVIDUAL MODE) and may also be
> invoked automatically by the orchestrator (SYSTEM MODE).

## When to use
Only pages with no usable text layer are OCR'd; pages with text are skipped.

## Operations
- detect when OCR needed
- make scanned pages searchable
- page-level recognition
- language selection
- skip already-text pages
- graceful degradation when no OCR engine

## Engine (what actually executes this)
`universal_pdf/core.ocr:detect_ocr_need / make_searchable / ocr_page_text`

All heavy lifting is done on disk / one page at a time by the shared engine —
never by loading the document into an LLM context.

## Tools & graceful degradation
- Preferred tool: **ocrmypdf (add searchable layer)**
- Fallback: **pytesseract+tesseract / easyocr (page text)**

If the preferred backend is unavailable the skill transparently uses the
fallback or reports a documented limitation. It **never** reports success when
an operation did not actually happen.

## Validation (this skill attaches checks to its Outcome)
OCR completeness; output openable

## Related skills
`pdf-read`, `pdf-vision`, `pdf-render`, `pdf-inspect`

## Example requests it handles
  * "OCR this scanned book so I can search it."
  * "Make this image-only PDF selectable text."

## Notes
Provenance: outputs cite their source page/section where relevant.
