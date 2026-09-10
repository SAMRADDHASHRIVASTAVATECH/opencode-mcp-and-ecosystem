---
name: pdf-redact
title: "True content redaction"
category: "PDF Management"
version: 1.0.0
engine: "core.annotate:redact_text"
preferred_tool: "PyMuPDF redact annots + apply_redactions"
fallback_tool: "—"
validation: "underlying_content_removed (leak check passes)"
---
# True content redaction  (`pdf-redact`)

True content redaction

> Part of the **Universal PDF Management & Creation Skill Repository**.
> Category: **PDF Management**.
> Every skill is individually callable (INDIVIDUAL MODE) and may also be
> invoked automatically by the orchestrator (SYSTEM MODE).

## When to use
Remove sensitive content so it cannot be copied/selected, with verification.

## Operations
- text-term redaction
- region redaction
- page-level
- metadata cleanup
- post-redaction leak verification

## Engine (what actually executes this)
`universal_pdf/core.annotate:redact_text`

All heavy lifting is done on disk / one page at a time by the shared engine —
never by loading the document into an LLM context.

## Tools & graceful degradation
- Preferred tool: **PyMuPDF redact annots + apply_redactions**
- Fallback: **—**

If the preferred backend is unavailable the skill transparently uses the
fallback or reports a documented limitation. It **never** reports success when
an operation did not actually happen.

## Validation (this skill attaches checks to its Outcome)
underlying_content_removed (leak check passes)

## Related skills
`pdf-validation`, `pdf-metadata`, `pdf-provenance`, `pdf-orchestrate`

## Example requests it handles
  * "Redact every mention of the account number and all metadata."

## Notes
Provenance: outputs cite their source page/section where relevant.
