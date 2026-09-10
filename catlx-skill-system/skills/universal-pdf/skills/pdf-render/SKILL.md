---
name: pdf-render
title: "Render PDF pages to images"
category: "PDF Management"
version: 1.0.0
engine: "core.images:render_pages / render_page_to_bytes"
preferred_tool: "PyMuPDF pixmap"
fallback_tool: "—"
validation: "rendered file count; each opens"
---
# Render PDF pages to images  (`pdf-render`)

Render PDF pages to images

> Part of the **Universal PDF Management & Creation Skill Repository**.
> Category: **PDF Management**.
> Every skill is individually callable (INDIVIDUAL MODE) and may also be
> invoked automatically by the orchestrator (SYSTEM MODE).

## When to use
Produce images of pages for OCR, vision, thumbnails or preview.

## Operations
- render page(s) to PNG/JPG
- custom DPI
- page subset
- single-page raster for vision/OCR pre-pass

## Engine (what actually executes this)
`universal_pdf/core.images:render_pages / render_page_to_bytes`

All heavy lifting is done on disk / one page at a time by the shared engine —
never by loading the document into an LLM context.

## Tools & graceful degradation
- Preferred tool: **PyMuPDF pixmap**
- Fallback: **—**

If the preferred backend is unavailable the skill transparently uses the
fallback or reports a documented limitation. It **never** reports success when
an operation did not actually happen.

## Validation (this skill attaches checks to its Outcome)
rendered file count; each opens

## Related skills
`pdf-ocr`, `pdf-vision`, `pdf-export`, `pdf-compare`

## Example requests it handles
  * "Give me a PNG of page 1 at 200 dpi."

## Notes
Provenance: outputs cite their source page/section where relevant.
