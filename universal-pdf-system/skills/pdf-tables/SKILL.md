---
name: pdf-tables
title: "Detect & extract tables as structure"
category: "PDF Management"
version: 1.0.0
engine: "core.tables:extract_tables / tables_to_csv / tables_to_xlsx / tables_to_json / tables_to_markdown / validate_tables"
preferred_tool: "pdfplumber layout extraction"
fallback_tool: "PyMuPDF find_tables"
validation: "extracted>0; each export written; column consistency"
---
# Detect & extract tables as structure  (`pdf-tables`)

Detect & extract tables as structure

> Part of the **Universal PDF Management & Creation Skill Repository**.
> Category: **PDF Management**.
> Every skill is individually callable (INDIVIDUAL MODE) and may also be
> invoked automatically by the orchestrator (SYSTEM MODE).

## When to use
Preserve tables as rows/columns instead of flattening to text.

## Operations
- extract tables
- header/rows reconstruction
- multi-page tables
- to CSV
- to XLSX
- to JSON
- to Markdown
- column-consistency validation

## Engine (what actually executes this)
`universal_pdf/core.tables:extract_tables / tables_to_csv / tables_to_xlsx / tables_to_json / tables_to_markdown / validate_tables`

All heavy lifting is done on disk / one page at a time by the shared engine —
never by loading the document into an LLM context.

## Tools & graceful degradation
- Preferred tool: **pdfplumber layout extraction**
- Fallback: **PyMuPDF find_tables**

If the preferred backend is unavailable the skill transparently uses the
fallback or reports a documented limitation. It **never** reports success when
an operation did not actually happen.

## Validation (this skill attaches checks to its Outcome)
extracted>0; each export written; column consistency

## Related skills
`pdf-extract`, `pdf-export`, `pdf-provenance`, `pdf-orchestrate`

## Example requests it handles
  * "Extract every table and export to Excel."
  * "Turn these PDF tables into CSV."

## Notes
Provenance: outputs cite their source page/section where relevant.
