---
name: pdf-edit
title: "Structural page editing"
category: "PDF Management"
version: 1.0.0
engine: "core.manipulate:insert_blank_pages / delete_pages (+ create overlay for images)"
preferred_tool: "PyMuPDF reconstruction"
fallback_tool: "pypdf (pure-structural)"
validation: "page_count matches expectation"
---
# Structural page editing  (`pdf-edit`)

Structural page editing

> Part of the **Universal PDF Management & Creation Skill Repository**.
> Category: **PDF Management**.
> Every skill is individually callable (INDIVIDUAL MODE) and may also be
> invoked automatically by the orchestrator (SYSTEM MODE).

## When to use
Edit the page set of a PDF. In-place content editing is limited, so safe reconstruction/overlay is used instead of pretending to edit.

## Operations
- insert pages
- delete pages
- replace pages (delete+insert)
- add blank pages
- add images to a page

## Engine (what actually executes this)
`universal_pdf/core.manipulate:insert_blank_pages / delete_pages (+ create overlay for images)`

All heavy lifting is done on disk / one page at a time by the shared engine —
never by loading the document into an LLM context.

## Tools & graceful degradation
- Preferred tool: **PyMuPDF reconstruction**
- Fallback: **pypdf (pure-structural)**

If the preferred backend is unavailable the skill transparently uses the
fallback or reports a documented limitation. It **never** reports success when
an operation did not actually happen.

## Validation (this skill attaches checks to its Outcome)
page_count matches expectation

## Related skills
`pdf-reorder`, `pdf-split`, `pdf-merge`, `pdf-orchestrate`

## Example requests it handles
  * "Delete pages 4,7,9."
  * "Insert a blank page after page 3."

## Notes
Provenance: outputs cite their source page/section where relevant.
