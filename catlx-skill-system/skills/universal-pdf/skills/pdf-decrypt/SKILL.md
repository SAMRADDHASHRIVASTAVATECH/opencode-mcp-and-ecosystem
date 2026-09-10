---
name: pdf-decrypt
title: "Decrypt / remove protection"
category: "PDF Management"
version: 1.0.0
engine: "core.security:decrypt"
preferred_tool: "PyMuPDF"
fallback_tool: "pypdf"
validation: "output not encrypted (when requested)"
---
# Decrypt / remove protection  (`pdf-decrypt`)

Decrypt / remove protection

> Part of the **Universal PDF Management & Creation Skill Repository**.
> Category: **PDF Management**.
> Every skill is individually callable (INDIVIDUAL MODE) and may also be
> invoked automatically by the orchestrator (SYSTEM MODE).

## When to use
Remove encryption from a document you are authorized to open.

## Operations
- open with password
- save unencrypted copy
- legitimate access workflows

## Engine (what actually executes this)
`universal_pdf/core.security:decrypt`

All heavy lifting is done on disk / one page at a time by the shared engine —
never by loading the document into an LLM context.

## Tools & graceful degradation
- Preferred tool: **PyMuPDF**
- Fallback: **pypdf**

If the preferred backend is unavailable the skill transparently uses the
fallback or reports a documented limitation. It **never** reports success when
an operation did not actually happen.

## Validation (this skill attaches checks to its Outcome)
output not encrypted (when requested)

## Related skills
`pdf-encrypt`, `pdf-permissions`, `pdf-orchestrate`

## Example requests it handles
  * "Remove the password so it can be printed."

## Notes
Provenance: outputs cite their source page/section where relevant.
