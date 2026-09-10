---
name: pdf-reorder
title: "Reorder / reverse / duplicate pages"
category: "PDF Management"
version: 1.0.0
engine: "core.manipulate:reorder_pdf"
preferred_tool: "PyMuPDF"
fallback_tool: "pypdf"
validation: "page_count == len(order)"
---
# Reorder / reverse / duplicate pages  (`pdf-reorder`)

Reorder / reverse / duplicate pages

> Part of the **Universal PDF Management & Creation Skill Repository**.
> Category: **PDF Management**.
> Every skill is individually callable (INDIVIDUAL MODE) and may also be
> invoked automatically by the orchestrator (SYSTEM MODE).

## When to use
Rearrange pages into any order.

## Operations
- arbitrary order
- reverse
- duplicate
- subset ordering

## Engine (what actually executes this)
`universal_pdf/core.manipulate:reorder_pdf`

All heavy lifting is done on disk / one page at a time by the shared engine —
never by loading the document into an LLM context.

## Tools & graceful degradation
- Preferred tool: **PyMuPDF**
- Fallback: **pypdf**

If the preferred backend is unavailable the skill transparently uses the
fallback or reports a documented limitation. It **never** reports success when
an operation did not actually happen.

## Validation (this skill attaches checks to its Outcome)
page_count == len(order)

## Related skills
`pdf-edit`, `pdf-split`, `pdf-merge`, `pdf-orchestrate`

## Example requests it handles
  * "Reverse the page order."
  * "Put page 3 first, then pages 5 and 1."

## Notes
Provenance: outputs cite their source page/section where relevant.
