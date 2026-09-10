---
name: pdf-links
title: "Hyperlinks"
category: "PDF Management"
version: 1.0.0
engine: "core.bookmarks:extract_links / add_links"
preferred_tool: "PyMuPDF links"
fallback_tool: "—"
validation: "parsed/added"
---
# Hyperlinks  (`pdf-links`)

Hyperlinks

> Part of the **Universal PDF Management & Creation Skill Repository**.
> Category: **PDF Management**.
> Every skill is individually callable (INDIVIDUAL MODE) and may also be
> invoked automatically by the orchestrator (SYSTEM MODE).

## When to use
Manage clickable links.

## Operations
- extract links (URI/page/rect)
- add URI links
- inspect link targets

## Engine (what actually executes this)
`universal_pdf/core.bookmarks:extract_links / add_links`

All heavy lifting is done on disk / one page at a time by the shared engine —
never by loading the document into an LLM context.

## Tools & graceful degradation
- Preferred tool: **PyMuPDF links**
- Fallback: **—**

If the preferred backend is unavailable the skill transparently uses the
fallback or reports a documented limitation. It **never** reports success when
an operation did not actually happen.

## Validation (this skill attaches checks to its Outcome)
parsed/added

## Related skills
`pdf-annotate`, `pdf-bookmarks`, `pdf-orchestrate`

## Example requests it handles
  * "List all hyperlinks in the PDF."

## Notes
Provenance: outputs cite their source page/section where relevant.
