---
name: pdf-export
title: "Export PDF content/data"
category: "PDF Management"
version: 1.0.0
engine: "core.convert:convert_pdf + core.tables exporters + core.images render"
preferred_tool: "multiple exporters"
fallback_tool: "—"
validation: "output exists"
---
# Export PDF content/data  (`pdf-export`)

Export PDF content/data

> Part of the **Universal PDF Management & Creation Skill Repository**.
> Category: **PDF Management**.
> Every skill is individually callable (INDIVIDUAL MODE) and may also be
> invoked automatically by the orchestrator (SYSTEM MODE).

## When to use
Ship PDF content out in the format the downstream consumer needs.

## Operations
- export text file
- export per-page
- export tables (csv/xlsx/json/md)
- export pages as images
- export full profile JSON

## Engine (what actually executes this)
`universal_pdf/core.convert:convert_pdf + core.tables exporters + core.images render`

All heavy lifting is done on disk / one page at a time by the shared engine —
never by loading the document into an LLM context.

## Tools & graceful degradation
- Preferred tool: **multiple exporters**
- Fallback: **—**

If the preferred backend is unavailable the skill transparently uses the
fallback or reports a documented limitation. It **never** reports success when
an operation did not actually happen.

## Validation (this skill attaches checks to its Outcome)
output exists

## Related skills
`pdf-convert`, `pdf-tables`, `pdf-create`, `pdf-orchestrate`

## Example requests it handles
  * "Export this report to Excel."
  * "Save all pages as PNGs."

## Notes
Provenance: outputs cite their source page/section where relevant.
