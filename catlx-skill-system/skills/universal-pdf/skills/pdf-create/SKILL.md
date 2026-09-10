---
name: pdf-create
title: "Create PDFs from documents & data"
category: "PDF Creation"
version: 1.0.0
engine: "core.create:create_pdf / create_from_markdown / create_from_text / create_from_html / create_from_images / create_report_from_rows"
preferred_tool: "reportlab platypus (vector, templated)"
fallback_tool: "PyMuPDF insert_text (simple docs)"
validation: "openable; page_count>=1; metadata valid; pages render"
---
# Create PDFs from documents & data  (`pdf-create`)

Create PDFs from documents & data

> Part of the **Universal PDF Management & Creation Skill Repository**.
> Category: **PDF Creation**.
> Every skill is individually callable (INDIVIDUAL MODE) and may also be
> invoked automatically by the orchestrator (SYSTEM MODE).

## When to use
Generate a brand new professional PDF from text, Markdown, HTML, images or tabular data.

## Operations
- plain text
- Markdown (subset)
- HTML (subset)
- images
- structured rows
- reports
- invoices
- cover pages
- tables
- lists
- headings
- headers/footers
- page numbers
- bookmarks
- metadata
- TOC placeholder

## Engine (what actually executes this)
`universal_pdf/core.create:create_pdf / create_from_markdown / create_from_text / create_from_html / create_from_images / create_report_from_rows`

All heavy lifting is done on disk / one page at a time by the shared engine —
never by loading the document into an LLM context.

## Tools & graceful degradation
- Preferred tool: **reportlab platypus (vector, templated)**
- Fallback: **PyMuPDF insert_text (simple docs)**

If the preferred backend is unavailable the skill transparently uses the
fallback or reports a documented limitation. It **never** reports success when
an operation did not actually happen.

## Validation (this skill attaches checks to its Outcome)
openable; page_count>=1; metadata valid; pages render

## Related skills
`pdf-read`, `pdf-export`, `pdf-inspect`, `pdf-orchestrate`

## Example requests it handles
  * "Create a 3-page report from this JSON of quarterly sales."
  * "Turn README.md into a clean PDF."
  * "Make an invoice PDF from these line items."

## Notes
Provenance: outputs cite their source page/section where relevant.
