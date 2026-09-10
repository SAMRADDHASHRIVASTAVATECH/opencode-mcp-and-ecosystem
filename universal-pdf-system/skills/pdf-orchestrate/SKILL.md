---
name: pdf-orchestrate
title: "Universal PDF Orchestrator (SYSTEM MODE)"
category: "PDF Management"
version: 1.0.0
engine: "universal_pdf.orchestration:orchestrator (see ORCHESTRATION.md + dispatch registry)"
preferred_tool: "pluggable dispatch"
fallback_tool: "manual per-skill fallback"
validation: "each sub-op validated; final output openable"
---
# Universal PDF Orchestrator (SYSTEM MODE)  (`pdf-orchestrate`)

Universal PDF Orchestrator (SYSTEM MODE)

> Part of the **Universal PDF Management & Creation Skill Repository**.
> Category: **PDF Management**.
> Every skill is individually callable (INDIVIDUAL MODE) and may also be
> invoked automatically by the orchestrator (SYSTEM MODE).

## When to use
Entry point that routes any request through the correct PDF skills.

## Operations
- parse a natural request into an intent
- choose and order the needed skills
- run individual mode or system mode
- produce a single report/artifact
- respect resource & capability limits

## Engine (what actually executes this)
`universal_pdf/universal_pdf.orchestration:orchestrator (see ORCHESTRATION.md + dispatch registry)`

All heavy lifting is done on disk / one page at a time by the shared engine —
never by loading the document into an LLM context.

## Tools & graceful degradation
- Preferred tool: **pluggable dispatch**
- Fallback: **manual per-skill fallback**

If the preferred backend is unavailable the skill transparently uses the
fallback or reports a documented limitation. It **never** reports success when
an operation did not actually happen.

## Validation (this skill attaches checks to its Outcome)
each sub-op validated; final output openable

## Related skills
`pdf-create`, `pdf-merge`, `pdf-summarize`, `pdf-search`, `pdf-ocr`, `pdf-redact`

## Example requests it handles
  * "Read this, summarize, and give citations."
  * "Merge, compress, and add a watermark."

## Notes
Provenance: outputs cite their source page/section where relevant.
