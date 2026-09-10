---
name: pdf-metadata
title: "Read / write / remove metadata"
category: "PDF Management"
version: 1.0.0
engine: "core.meta:set_metadata / remove_metadata (+ inspect for read)"
preferred_tool: "PyMuPDF set_metadata"
fallback_tool: "pypdf metadata"
validation: "metadata round-trips (verify after write)"
---
# Read / write / remove metadata  (`pdf-metadata`)

Read / write / remove metadata

> Part of the **Universal PDF Management & Creation Skill Repository**.
> Category: **PDF Management**.
> Every skill is individually callable (INDIVIDUAL MODE) and may also be
> invoked automatically by the orchestrator (SYSTEM MODE).

## When to use
Manage document properties.

## Operations
- read title/author/subject/keywords/creator/producer/dates
- write fields
- strip all metadata
- batch update

## Engine (what actually executes this)
`universal_pdf/core.meta:set_metadata / remove_metadata (+ inspect for read)`

All heavy lifting is done on disk / one page at a time by the shared engine —
never by loading the document into an LLM context.

## Tools & graceful degradation
- Preferred tool: **PyMuPDF set_metadata**
- Fallback: **pypdf metadata**

If the preferred backend is unavailable the skill transparently uses the
fallback or reports a documented limitation. It **never** reports success when
an operation did not actually happen.

## Validation (this skill attaches checks to its Outcome)
metadata round-trips (verify after write)

## Related skills
`pdf-inspect`, `pdf-provenance`, `pdf-orchestrate`

## Example requests it handles
  * "Set author to 'Legal Dept' and add keywords."

## Notes
Provenance: outputs cite their source page/section where relevant.
