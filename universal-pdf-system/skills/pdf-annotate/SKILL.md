---
name: pdf-annotate
title: "Add annotations"
category: "PDF Management"
version: 1.0.0
engine: "core.annotate:add_annotations"
preferred_tool: "PyMuPDF annotation API"
fallback_tool: "—"
validation: "added>=0"
---
# Add annotations  (`pdf-annotate`)

Add annotations

> Part of the **Universal PDF Management & Creation Skill Repository**.
> Category: **PDF Management**.
> Every skill is individually callable (INDIVIDUAL MODE) and may also be
> invoked automatically by the orchestrator (SYSTEM MODE).

## When to use
Annotate pages with standard markups and notes.

## Operations
- highlight
- underline
- strikeout
- text note
- free text
- square/circle
- line/arrow
- link
- preserve existing annotations

## Engine (what actually executes this)
`universal_pdf/core.annotate:add_annotations`

All heavy lifting is done on disk / one page at a time by the shared engine —
never by loading the document into an LLM context.

## Tools & graceful degradation
- Preferred tool: **PyMuPDF annotation API**
- Fallback: **—**

If the preferred backend is unavailable the skill transparently uses the
fallback or reports a documented limitation. It **never** reports success when
an operation did not actually happen.

## Validation (this skill attaches checks to its Outcome)
added>=0

## Related skills
`pdf-links`, `pdf-inspect`, `pdf-orchestrate`

## Example requests it handles
  * "Highlight all occurrences of the keyword on page 2."

## Notes
Provenance: outputs cite their source page/section where relevant.
