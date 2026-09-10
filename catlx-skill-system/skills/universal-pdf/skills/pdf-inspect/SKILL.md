---
name: pdf-inspect
title: "Inspect a PDF into a structured profile"
category: "PDF Management"
version: 1.0.0
engine: "core.inspect:inspect"
preferred_tool: "PyMuPDF"
fallback_tool: "pypdf (permission/version facts)"
validation: "openable; page_count>0"
---
# Inspect a PDF into a structured profile  (`pdf-inspect`)

Inspect a PDF into a structured profile

> Part of the **Universal PDF Management & Creation Skill Repository**.
> Category: **PDF Management**.
> Every skill is individually callable (INDIVIDUAL MODE) and may also be
> invoked automatically by the orchestrator (SYSTEM MODE).

## When to use
Before operating on an unknown PDF, build a cheap structured profile.

## Operations
- page count
- page size/orientation
- metadata
- fonts
- image count
- links
- annotations
- forms present
- encryption/permissions
- PDF version
- embedded files
- text layer health

## Engine (what actually executes this)
`universal_pdf/core.inspect:inspect`

All heavy lifting is done on disk / one page at a time by the shared engine —
never by loading the document into an LLM context.

## Tools & graceful degradation
- Preferred tool: **PyMuPDF**
- Fallback: **pypdf (permission/version facts)**

If the preferred backend is unavailable the skill transparently uses the
fallback or reports a documented limitation. It **never** reports success when
an operation did not actually happen.

## Validation (this skill attaches checks to its Outcome)
openable; page_count>0

## Related skills
`pdf-read`, `pdf-validation`, `pdf-orchestrate`, `pdf-provenance`

## Example requests it handles
  * "What type of document is this? How many pages?"
  * "Profile this PDF: is it scanned or text?"

## Notes
Provenance: outputs cite their source page/section where relevant.
