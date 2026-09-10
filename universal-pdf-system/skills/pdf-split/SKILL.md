---
name: pdf-split
title: "Split a PDF"
category: "PDF Management"
version: 1.0.0
engine: "core.manipulate:split_pdf / extract_pages"
preferred_tool: "PyMuPDF"
fallback_tool: "pypdf"
validation: "produced file count"
---
# Split a PDF  (`pdf-split`)

Split a PDF

> Part of the **Universal PDF Management & Creation Skill Repository**.
> Category: **PDF Management**.
> Every skill is individually callable (INDIVIDUAL MODE) and may also be
> invoked automatically by the orchestrator (SYSTEM MODE).

## When to use
Break one PDF into parts.

## Operations
- split every N pages
- split into ranges
- split at TOC top-level
- extract selected pages

## Engine (what actually executes this)
`universal_pdf/core.manipulate:split_pdf / extract_pages`

All heavy lifting is done on disk / one page at a time by the shared engine —
never by loading the document into an LLM context.

## Tools & graceful degradation
- Preferred tool: **PyMuPDF**
- Fallback: **pypdf**

If the preferred backend is unavailable the skill transparently uses the
fallback or reports a documented limitation. It **never** reports success when
an operation did not actually happen.

## Validation (this skill attaches checks to its Outcome)
produced file count

## Related skills
`pdf-merge`, `pdf-reorder`, `pdf-orchestrate`

## Example requests it handles
  * "Split this PDF every 5 pages."
  * "Extract just pages 1-3 and 8."

## Notes
Provenance: outputs cite their source page/section where relevant.
