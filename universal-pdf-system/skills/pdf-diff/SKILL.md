---
name: pdf-diff
title: "Page/text diff report"
category: "PDF Management"
version: 1.0.0
engine: "core.compare:compare_pdfs + text_report"
preferred_tool: "difflib"
fallback_tool: "—"
validation: "report produced"
---
# Page/text diff report  (`pdf-diff`)

Page/text diff report

> Part of the **Universal PDF Management & Creation Skill Repository**.
> Category: **PDF Management**.
> Every skill is individually callable (INDIVIDUAL MODE) and may also be
> invoked automatically by the orchestrator (SYSTEM MODE).

## When to use
Get a readable list of added/removed/modified content between two versions.

## Operations
- revision diff
- unified text change sample
- human-readable report

## Engine (what actually executes this)
`universal_pdf/core.compare:compare_pdfs + text_report`

All heavy lifting is done on disk / one page at a time by the shared engine —
never by loading the document into an LLM context.

## Tools & graceful degradation
- Preferred tool: **difflib**
- Fallback: **—**

If the preferred backend is unavailable the skill transparently uses the
fallback or reports a documented limitation. It **never** reports success when
an operation did not actually happen.

## Validation (this skill attaches checks to its Outcome)
report produced

## Related skills
`pdf-compare`, `pdf-orchestrate`

## Example requests it handles
  * "Show a readable diff of what changed."

## Notes
Provenance: outputs cite their source page/section where relevant.
