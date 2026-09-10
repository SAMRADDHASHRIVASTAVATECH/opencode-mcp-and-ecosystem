---
name: pdf-encrypt
title: "Encrypt / password-protect"
category: "PDF Management"
version: 1.0.0
engine: "core.security:encrypt"
preferred_tool: "PyMuPDF encryption"
fallback_tool: "pypdf writer.encrypt"
validation: "output is_encrypted"
---
# Encrypt / password-protect  (`pdf-encrypt`)

Encrypt / password-protect

> Part of the **Universal PDF Management & Creation Skill Repository**.
> Category: **PDF Management**.
> Every skill is individually callable (INDIVIDUAL MODE) and may also be
> invoked automatically by the orchestrator (SYSTEM MODE).

## When to use
Add password protection and set permissions.

## Operations
- AES-128/256
- user + owner passwords
- permission flags (print/modify/copy/annotate)

## Engine (what actually executes this)
`universal_pdf/core.security:encrypt`

All heavy lifting is done on disk / one page at a time by the shared engine —
never by loading the document into an LLM context.

## Tools & graceful degradation
- Preferred tool: **PyMuPDF encryption**
- Fallback: **pypdf writer.encrypt**

If the preferred backend is unavailable the skill transparently uses the
fallback or reports a documented limitation. It **never** reports success when
an operation did not actually happen.

## Validation (this skill attaches checks to its Outcome)
output is_encrypted

## Related skills
`pdf-decrypt`, `pdf-permissions`, `pdf-orchestrate`

## Example requests it handles
  * "Encrypt this PDF with password 's3cret' and disallow copying."

## Notes
Provenance: outputs cite their source page/section where relevant.
