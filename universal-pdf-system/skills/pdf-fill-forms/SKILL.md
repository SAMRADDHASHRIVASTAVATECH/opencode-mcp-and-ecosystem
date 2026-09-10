---
name: pdf-fill-forms
title: "Fill AcroForm fields"
category: "PDF Management"
version: 1.0.0
engine: "core.forms:fill_form"
preferred_tool: "PyMuPDF widget update"
fallback_tool: "pypdf update_page_form_field_values"
validation: "each requested field filled"
---
# Fill AcroForm fields  (`pdf-fill-forms`)

Fill AcroForm fields

> Part of the **Universal PDF Management & Creation Skill Repository**.
> Category: **PDF Management**.
> Every skill is individually callable (INDIVIDUAL MODE) and may also be
> invoked automatically by the orchestrator (SYSTEM MODE).

## When to use
Populate a form programmatically.

## Operations
- fill by field name
- text/checkbox/radio/list
- optional flatten

## Engine (what actually executes this)
`universal_pdf/core.forms:fill_form`

All heavy lifting is done on disk / one page at a time by the shared engine —
never by loading the document into an LLM context.

## Tools & graceful degradation
- Preferred tool: **PyMuPDF widget update**
- Fallback: **pypdf update_page_form_field_values**

If the preferred backend is unavailable the skill transparently uses the
fallback or reports a documented limitation. It **never** reports success when
an operation did not actually happen.

## Validation (this skill attaches checks to its Outcome)
each requested field filled

## Related skills
`pdf-forms`, `pdf-sign`, `pdf-orchestrate`

## Example requests it handles
  * "Fill the form with these values and flatten it."

## Notes
Provenance: outputs cite their source page/section where relevant.
