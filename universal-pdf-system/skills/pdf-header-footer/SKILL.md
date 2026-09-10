---
name: pdf-header-footer
title: "Add headers, footers, page numbers"
category: "PDF Management"
version: 1.0.0
engine: "core.annotate:add_header_footer"
preferred_tool: "PyMuPDF insert_text"
fallback_tool: "—"
validation: "page_count preserved"
---
# Add headers, footers, page numbers  (`pdf-header-footer`)

Add headers, footers, page numbers

> Part of the **Universal PDF Management & Creation Skill Repository**.
> Category: **PDF Management**.
> Every skill is individually callable (INDIVIDUAL MODE) and may also be
> invoked automatically by the orchestrator (SYSTEM MODE).

## When to use
Add running heads/footers and page numbers.

## Operations
- running header
- running footer
- page numbers
- skip first page
- start number
- page selection

## Engine (what actually executes this)
`universal_pdf/core.annotate:add_header_footer`

All heavy lifting is done on disk / one page at a time by the shared engine —
never by loading the document into an LLM context.

## Tools & graceful degradation
- Preferred tool: **PyMuPDF insert_text**
- Fallback: **—**

If the preferred backend is unavailable the skill transparently uses the
fallback or reports a documented limitation. It **never** reports success when
an operation did not actually happen.

## Validation (this skill attaches checks to its Outcome)
page_count preserved

## Related skills
`pdf-watermark`, `pdf-annotate`, `pdf-orchestrate`

## Example requests it handles
  * "Add 'Quarterly Report' header and page numbers."

## Notes
Provenance: outputs cite their source page/section where relevant.
