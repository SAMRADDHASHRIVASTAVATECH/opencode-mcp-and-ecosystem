---
name: pdf-rotate
title: "Rotate pages"
category: "PDF Management"
version: 1.0.0
engine: "core.manipulate:rotate_pdf"
preferred_tool: "PyMuPDF set_rotation"
fallback_tool: "pypdf"
validation: "page_count preserved"
---
# Rotate pages  (`pdf-rotate`)

Rotate pages

> Part of the **Universal PDF Management & Creation Skill Repository**.
> Category: **PDF Management**.
> Every skill is individually callable (INDIVIDUAL MODE) and may also be
> invoked automatically by the orchestrator (SYSTEM MODE).

## When to use
Fix or change page orientation.

## Operations
- rotate 90/180/270
- selected pages
- preserve text/orientation metadata

## Engine (what actually executes this)
`universal_pdf/core.manipulate:rotate_pdf`

All heavy lifting is done on disk / one page at a time by the shared engine —
never by loading the document into an LLM context.

## Tools & graceful degradation
- Preferred tool: **PyMuPDF set_rotation**
- Fallback: **pypdf**

If the preferred backend is unavailable the skill transparently uses the
fallback or reports a documented limitation. It **never** reports success when
an operation did not actually happen.

## Validation (this skill attaches checks to its Outcome)
page_count preserved

## Related skills
`pdf-reorder`, `pdf-crop`, `pdf-orchestrate`

## Example requests it handles
  * "Rotate the scanned page 4 by 90 degrees."

## Notes
Provenance: outputs cite their source page/section where relevant.
