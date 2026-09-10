---
name: pdf-watermark
title: "Add watermarks & stamps"
category: "PDF Management"
version: 1.0.0
engine: "core.annotate:add_watermark / add_stamp"
preferred_tool: "reportlab overlay + PyMuPDF stamping"
fallback_tool: "—"
validation: "page_count preserved; overlay renders"
---
# Add watermarks & stamps  (`pdf-watermark`)

Add watermarks & stamps

> Part of the **Universal PDF Management & Creation Skill Repository**.
> Category: **PDF Management**.
> Every skill is individually callable (INDIVIDUAL MODE) and may also be
> invoked automatically by the orchestrator (SYSTEM MODE).

## When to use
Protect or mark pages with text/image watermarks and stamps.

## Operations
- diagonal text watermark (arbitrary angle)
- image watermark
- opacity
- page selection
- stamp overlays (APPROVED/CONFIDENTIAL)

## Engine (what actually executes this)
`universal_pdf/core.annotate:add_watermark / add_stamp`

All heavy lifting is done on disk / one page at a time by the shared engine —
never by loading the document into an LLM context.

## Tools & graceful degradation
- Preferred tool: **reportlab overlay + PyMuPDF stamping**
- Fallback: **—**

If the preferred backend is unavailable the skill transparently uses the
fallback or reports a documented limitation. It **never** reports success when
an operation did not actually happen.

## Validation (this skill attaches checks to its Outcome)
page_count preserved; overlay renders

## Related skills
`pdf-header-footer`, `pdf-annotate`, `pdf-orchestrate`

## Example requests it handles
  * "Watermark every page with 'CONFIDENTIAL'."
  * "Stamp page 1 with APPROVED."

## Notes
Provenance: outputs cite their source page/section where relevant.
