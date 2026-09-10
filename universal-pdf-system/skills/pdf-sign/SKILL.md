---
name: pdf-sign
title: "Signatures"
category: "PDF Management"
version: 1.0.0
engine: "core.security:sign_pdf / inspect_signatures"
preferred_tool: "PyMuPDF widget/image placement"
fallback_tool: "pypdf (certificate signature infra)"
validation: "signature placed; clearly reported as visual unless crypto infra used"
---
# Signatures  (`pdf-sign`)

Signatures

> Part of the **Universal PDF Management & Creation Skill Repository**.
> Category: **PDF Management**.
> Every skill is individually callable (INDIVIDUAL MODE) and may also be
> invoked automatically by the orchestrator (SYSTEM MODE).

## When to use
Add a signature or inspect signature fields. Visual placement never claims cryptographic validity.

## Operations
- inspect signature fields
- place a visible signature image/text

## Engine (what actually executes this)
`universal_pdf/core.security:sign_pdf / inspect_signatures`

All heavy lifting is done on disk / one page at a time by the shared engine —
never by loading the document into an LLM context.

## Tools & graceful degradation
- Preferred tool: **PyMuPDF widget/image placement**
- Fallback: **pypdf (certificate signature infra)**

If the preferred backend is unavailable the skill transparently uses the
fallback or reports a documented limitation. It **never** reports success when
an operation did not actually happen.

## Validation (this skill attaches checks to its Outcome)
signature placed; clearly reported as visual unless crypto infra used

## Related skills
`pdf-fill-forms`, `pdf-validation`, `pdf-orchestrate`

## Example requests it handles
  * "Place my signature image on the last page."

## Notes
Provenance: outputs cite their source page/section where relevant.
