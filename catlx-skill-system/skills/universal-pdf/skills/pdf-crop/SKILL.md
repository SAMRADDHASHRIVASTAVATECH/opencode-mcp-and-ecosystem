---
name: pdf-crop
title: "Crop pages"
category: "PDF Management"
version: 1.0.0
engine: "core.manipulate:crop_pdf"
preferred_tool: "PyMuPDF set_cropbox/mediabox"
fallback_tool: "—"
validation: "page_count preserved"
---
# Crop pages  (`pdf-crop`)

Crop pages

> Part of the **Universal PDF Management & Creation Skill Repository**.
> Category: **PDF Management**.
> Every skill is individually callable (INDIVIDUAL MODE) and may also be
> invoked automatically by the orchestrator (SYSTEM MODE).

## When to use
Trim edges / white borders of pages.

## Operations
- uniform margin crop
- asymmetric insets
- selected pages

## Engine (what actually executes this)
`universal_pdf/core.manipulate:crop_pdf`

All heavy lifting is done on disk / one page at a time by the shared engine —
never by loading the document into an LLM context.

## Tools & graceful degradation
- Preferred tool: **PyMuPDF set_cropbox/mediabox**
- Fallback: **—**

If the preferred backend is unavailable the skill transparently uses the
fallback or reports a documented limitation. It **never** reports success when
an operation did not actually happen.

## Validation (this skill attaches checks to its Outcome)
page_count preserved

## Related skills
`pdf-rotate`, `pdf-scale`, `pdf-orchestrate`

## Example requests it handles
  * "Crop 0.5 inch margins off every page."

## Notes
Provenance: outputs cite their source page/section where relevant.
