---
name: pdf-repair
title: "Diagnose & repair damaged PDFs"
category: "PDF Management"
version: 1.0.0
engine: "core.repair:diagnose / repair_pdf"
preferred_tool: "PyMuPDF re-save (garbage)"
fallback_tool: "pypdf structural rebuild"
validation: "openable after repair; recovered page count reported"
---
# Diagnose & repair damaged PDFs  (`pdf-repair`)

Diagnose & repair damaged PDFs

> Part of the **Universal PDF Management & Creation Skill Repository**.
> Category: **PDF Management**.
> Every skill is individually callable (INDIVIDUAL MODE) and may also be
> invoked automatically by the orchestrator (SYSTEM MODE).

## When to use
Recover usable content from a malformed/corrupt PDF and say what failed.

## Operations
- openability probe
- page-tree health
- renderability
- rebuild xrefs
- per-page rescue
- report unrecovered content

## Engine (what actually executes this)
`universal_pdf/core.repair:diagnose / repair_pdf`

All heavy lifting is done on disk / one page at a time by the shared engine —
never by loading the document into an LLM context.

## Tools & graceful degradation
- Preferred tool: **PyMuPDF re-save (garbage)**
- Fallback: **pypdf structural rebuild**

If the preferred backend is unavailable the skill transparently uses the
fallback or reports a documented limitation. It **never** reports success when
an operation did not actually happen.

## Validation (this skill attaches checks to its Outcome)
openable after repair; recovered page count reported

## Related skills
`pdf-validation`, `pdf-compress`, `pdf-orchestrate`

## Example requests it handles
  * "This PDF won't open - repair it."

## Notes
Provenance: outputs cite their source page/section where relevant.
