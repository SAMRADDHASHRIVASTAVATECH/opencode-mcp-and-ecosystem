---
name: pdf-permissions
title: "Permission handling"
category: "PDF Management"
version: 1.0.0
engine: "core.security:encrypt(permissions=...) + inspect(security)"
preferred_tool: "PyMuPDF permissions"
fallback_tool: "pypdf permissions_flag"
validation: "flags reported / applied"
---
# Permission handling  (`pdf-permissions`)

Permission handling

> Part of the **Universal PDF Management & Creation Skill Repository**.
> Category: **PDF Management**.
> Every skill is individually callable (INDIVIDUAL MODE) and may also be
> invoked automatically by the orchestrator (SYSTEM MODE).

## When to use
Control and inspect DRM-style usage permissions (legitimate management).

## Operations
- read permission flags
- set permissions while encrypting

## Engine (what actually executes this)
`universal_pdf/core.security:encrypt(permissions=...) + inspect(security)`

All heavy lifting is done on disk / one page at a time by the shared engine —
never by loading the document into an LLM context.

## Tools & graceful degradation
- Preferred tool: **PyMuPDF permissions**
- Fallback: **pypdf permissions_flag**

If the preferred backend is unavailable the skill transparently uses the
fallback or reports a documented limitation. It **never** reports success when
an operation did not actually happen.

## Validation (this skill attaches checks to its Outcome)
flags reported / applied

## Related skills
`pdf-encrypt`, `pdf-inspect`, `pdf-orchestrate`

## Example requests it handles
  * "What operations are permitted on this PDF?"

## Notes
Provenance: outputs cite their source page/section where relevant.
