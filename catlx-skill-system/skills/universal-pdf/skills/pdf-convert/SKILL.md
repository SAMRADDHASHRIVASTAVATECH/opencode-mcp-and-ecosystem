---
name: pdf-convert
title: "Convert to/from other formats"
category: "PDF Management"
version: 1.0.0
engine: "core.convert:convert_pdf (and core.create for creation direction)"
preferred_tool: "text/tables/render engines"
fallback_tool: "pandoc for DOCX (documented limitation)"
validation: "output exists; renderable; sanity"
---
# Convert to/from other formats  (`pdf-convert`)

Convert to/from other formats

> Part of the **Universal PDF Management & Creation Skill Repository**.
> Category: **PDF Management**.
> Every skill is individually callable (INDIVIDUAL MODE) and may also be
> invoked automatically by the orchestrator (SYSTEM MODE).

## When to use
Move content in and out of PDF with clearly documented fidelity limits.

## Operations
- PDF->TXT
- PDF->Markdown
- PDF->HTML
- PDF->JSON
- PDF->Images
- PDF->CSV/XLSX (tables)
- PDF->DOCX (when pandoc present)
- TXT/MD/HTML/Images->PDF

## Engine (what actually executes this)
`universal_pdf/core.convert:convert_pdf (and core.create for creation direction)`

All heavy lifting is done on disk / one page at a time by the shared engine —
never by loading the document into an LLM context.

## Tools & graceful degradation
- Preferred tool: **text/tables/render engines**
- Fallback: **pandoc for DOCX (documented limitation)**

If the preferred backend is unavailable the skill transparently uses the
fallback or reports a documented limitation. It **never** reports success when
an operation did not actually happen.

## Validation (this skill attaches checks to its Outcome)
output exists; renderable; sanity

## Related skills
`pdf-create`, `pdf-export`, `pdf-tables`, `pdf-orchestrate`

## Example requests it handles
  * "Turn this PDF into Markdown."
  * "Convert these images into a PDF."

## Notes
Provenance: outputs cite their source page/section where relevant.
