---
name: pdf-images
title: "Embedded image operations"
category: "PDF Management"
version: 1.0.0
engine: "core.images:extract_images / image_metadata / render_pages"
preferred_tool: "PyMuPDF pixmap + PIL"
fallback_tool: "—"
validation: "extracted count"
---
# Embedded image operations  (`pdf-images`)

Embedded image operations

> Part of the **Universal PDF Management & Creation Skill Repository**.
> Category: **PDF Management**.
> Every skill is individually callable (INDIVIDUAL MODE) and may also be
> invoked automatically by the orchestrator (SYSTEM MODE).

## When to use
Pull or inspect the raster images inside a PDF.

## Operations
- extract images
- inspect image resolution
- render page->image
- optimize image quality
- image-heavy page detection

## Engine (what actually executes this)
`universal_pdf/core.images:extract_images / image_metadata / render_pages`

All heavy lifting is done on disk / one page at a time by the shared engine —
never by loading the document into an LLM context.

## Tools & graceful degradation
- Preferred tool: **PyMuPDF pixmap + PIL**
- Fallback: **—**

If the preferred backend is unavailable the skill transparently uses the
fallback or reports a documented limitation. It **never** reports success when
an operation did not actually happen.

## Validation (this skill attaches checks to its Outcome)
extracted count

## Related skills
`pdf-render`, `pdf-ocr`, `pdf-orchestrate`

## Example requests it handles
  * "Extract all embedded images."
  * "Which pages are image-heavy (scanned)?"

## Notes
Provenance: outputs cite their source page/section where relevant.
