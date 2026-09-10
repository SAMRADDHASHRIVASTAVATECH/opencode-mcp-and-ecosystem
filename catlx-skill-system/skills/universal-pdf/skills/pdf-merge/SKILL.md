---
name: pdf-merge
title: "Merge PDFs"
category: "PDF Management"
version: 1.0.0
engine: "core.manipulate:merge_pdfs"
preferred_tool: "PyMuPDF insert_pdf"
fallback_tool: "pypdf PdfWriter"
validation: "page_count == sum of inputs"
---
# Merge PDFs  (`pdf-merge`)

Merge PDFs

> Part of the **Universal PDF Management & Creation Skill Repository**.
> Category: **PDF Management**.
> Every skill is individually callable (INDIVIDUAL MODE) and may also be
> invoked automatically by the orchestrator (SYSTEM MODE).

## When to use
Combine multiple PDFs into one.

## Operations
- merge N PDFs in order
- preserve bookmarks with page offsets

## Engine (what actually executes this)
`universal_pdf/core.manipulate:merge_pdfs`

All heavy lifting is done on disk / one page at a time by the shared engine —
never by loading the document into an LLM context.

## Tools & graceful degradation
- Preferred tool: **PyMuPDF insert_pdf**
- Fallback: **pypdf PdfWriter**

If the preferred backend is unavailable the skill transparently uses the
fallback or reports a documented limitation. It **never** reports success when
an operation did not actually happen.

## Validation (this skill attaches checks to its Outcome)
page_count == sum of inputs

## Related skills
`pdf-split`, `pdf-reorder`, `pdf-orchestrate`

## Example requests it handles
  * "Merge these three PDFs into one file."

## Notes
Provenance: outputs cite their source page/section where relevant.
