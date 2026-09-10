---
name: pdf-compare
title: "Compare two PDFs"
category: "PDF Management"
version: 1.0.0
engine: "core.compare:compare_pdfs / text_report"
preferred_tool: "PyMuPDF text + PIL visual"
fallback_tool: "difflib text similarity"
validation: "compared (both pages counted)"
---
# Compare two PDFs  (`pdf-compare`)

Compare two PDFs

> Part of the **Universal PDF Management & Creation Skill Repository**.
> Category: **PDF Management**.
> Every skill is individually callable (INDIVIDUAL MODE) and may also be
> invoked automatically by the orchestrator (SYSTEM MODE).

## When to use
Find what changed between versions.

## Operations
- page-count diff
- added/removed/modified pages
- text similarity per page
- metadata diff
- optional visual diff
- report output

## Engine (what actually executes this)
`universal_pdf/core.compare:compare_pdfs / text_report`

All heavy lifting is done on disk / one page at a time by the shared engine —
never by loading the document into an LLM context.

## Tools & graceful degradation
- Preferred tool: **PyMuPDF text + PIL visual**
- Fallback: **difflib text similarity**

If the preferred backend is unavailable the skill transparently uses the
fallback or reports a documented limitation. It **never** reports success when
an operation did not actually happen.

## Validation (this skill attaches checks to its Outcome)
compared (both pages counted)

## Related skills
`pdf-inspect`, `pdf-validation`, `pdf-orchestrate`

## Example requests it handles
  * "Compare v1 and v2 of this contract."
  * "Diff these two PDFs and show me the changes."

## Notes
Provenance: outputs cite their source page/section where relevant.
