---
name: pdf-scale
title: "Scale / resize pages"
category: "PDF Management"
version: 1.0.0
engine: "core.manipulate:scale_pdf"
preferred_tool: "PyMuPDF page rebuild"
fallback_tool: "—"
validation: "page_count preserved"
---
# Scale / resize pages  (`pdf-scale`)

Scale / resize pages

> Part of the **Universal PDF Management & Creation Skill Repository**.
> Category: **PDF Management**.
> Every skill is individually callable (INDIVIDUAL MODE) and may also be
> invoked automatically by the orchestrator (SYSTEM MODE).

## When to use
Enlarge/shrink page content or normalise page size.

## Operations
- uniform scale factor
- set page size
- selected pages

## Engine (what actually executes this)
`universal_pdf/core.manipulate:scale_pdf`

All heavy lifting is done on disk / one page at a time by the shared engine —
never by loading the document into an LLM context.

## Tools & graceful degradation
- Preferred tool: **PyMuPDF page rebuild**
- Fallback: **—**

If the preferred backend is unavailable the skill transparently uses the
fallback or reports a documented limitation. It **never** reports success when
an operation did not actually happen.

## Validation (this skill attaches checks to its Outcome)
page_count preserved

## Related skills
`pdf-crop`, `pdf-orchestrate`

## Example requests it handles
  * "Resize all pages to A4."

## Notes
Provenance: outputs cite their source page/section where relevant.
