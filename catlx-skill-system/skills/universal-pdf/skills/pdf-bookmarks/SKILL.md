---
name: pdf-bookmarks
title: "Bookmarks / outline / TOC"
category: "PDF Management"
version: 1.0.0
engine: "core.bookmarks:extract_bookmarks / set_bookmarks / remove_bookmarks"
preferred_tool: "PyMuPDF get_toc/set_toc"
fallback_tool: "pypdf outline"
validation: "TOC present after set"
---
# Bookmarks / outline / TOC  (`pdf-bookmarks`)

Bookmarks / outline / TOC

> Part of the **Universal PDF Management & Creation Skill Repository**.
> Category: **PDF Management**.
> Every skill is individually callable (INDIVIDUAL MODE) and may also be
> invoked automatically by the orchestrator (SYSTEM MODE).

## When to use
Read or write the navigation outline.

## Operations
- extract TOC
- set/merge/remove outline
- TOC entries link to pages

## Engine (what actually executes this)
`universal_pdf/core.bookmarks:extract_bookmarks / set_bookmarks / remove_bookmarks`

All heavy lifting is done on disk / one page at a time by the shared engine —
never by loading the document into an LLM context.

## Tools & graceful degradation
- Preferred tool: **PyMuPDF get_toc/set_toc**
- Fallback: **pypdf outline**

If the preferred backend is unavailable the skill transparently uses the
fallback or reports a documented limitation. It **never** reports success when
an operation did not actually happen.

## Validation (this skill attaches checks to its Outcome)
TOC present after set

## Related skills
`pdf-links`, `pdf-provenance`, `pdf-orchestrate`

## Example requests it handles
  * "Build a table-of-contents outline from the headings."

## Notes
Provenance: outputs cite their source page/section where relevant.
