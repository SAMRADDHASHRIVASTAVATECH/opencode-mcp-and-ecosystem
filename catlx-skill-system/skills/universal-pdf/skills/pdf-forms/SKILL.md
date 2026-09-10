---
name: pdf-forms
title: "Forms: detect, list, extract, flatten"
category: "PDF Management"
version: 1.0.0
engine: "core.forms:list_fields / extract_form_data / flatten_form"
preferred_tool: "PyMuPDF widget API"
fallback_tool: "pypdf (reader fields)"
validation: "fields enumerated"
---
# Forms: detect, list, extract, flatten  (`pdf-forms`)

Forms: detect, list, extract, flatten

> Part of the **Universal PDF Management & Creation Skill Repository**.
> Category: **PDF Management**.
> Every skill is individually callable (INDIVIDUAL MODE) and may also be
> invoked automatically by the orchestrator (SYSTEM MODE).

## When to use
Understand PDF AcroForms.

## Operations
- detect form
- list fields+types+values
- extract data
- flatten values into content

## Engine (what actually executes this)
`universal_pdf/core.forms:list_fields / extract_form_data / flatten_form`

All heavy lifting is done on disk / one page at a time by the shared engine —
never by loading the document into an LLM context.

## Tools & graceful degradation
- Preferred tool: **PyMuPDF widget API**
- Fallback: **pypdf (reader fields)**

If the preferred backend is unavailable the skill transparently uses the
fallback or reports a documented limitation. It **never** reports success when
an operation did not actually happen.

## Validation (this skill attaches checks to its Outcome)
fields enumerated

## Related skills
`pdf-fill-forms`, `pdf-inspect`, `pdf-orchestrate`

## Example requests it handles
  * "Are there fillable fields? List them."

## Notes
Provenance: outputs cite their source page/section where relevant.
