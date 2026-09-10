---
name: pdf-validation
title: "Validate PDF & operation outputs"
category: "PDF Management"
version: 1.0.0
engine: "core.validation + per-module Outcome.checks"
preferred_tool: "uniform ValidationCheck"
fallback_tool: "—"
validation: "named checks with pass/fail"
---
# Validate PDF & operation outputs  (`pdf-validation`)

Validate PDF & operation outputs

> Part of the **Universal PDF Management & Creation Skill Repository**.
> Category: **PDF Management**.
> Every skill is individually callable (INDIVIDUAL MODE) and may also be
> invoked automatically by the orchestrator (SYSTEM MODE).

## When to use
Prove an operation actually worked before trusting it.

## Operations
- openable
- page count
- renderability
- text coverage
- redaction leak check
- output sanity

## Engine (what actually executes this)
`universal_pdf/core.validation + per-module Outcome.checks`

All heavy lifting is done on disk / one page at a time by the shared engine —
never by loading the document into an LLM context.

## Tools & graceful degradation
- Preferred tool: **uniform ValidationCheck**
- Fallback: **—**

If the preferred backend is unavailable the skill transparently uses the
fallback or reports a documented limitation. It **never** reports success when
an operation did not actually happen.

## Validation (this skill attaches checks to its Outcome)
named checks with pass/fail

## Related skills
`pdf-inspect`, `pdf-orchestrate`, `pdf-compare`

## Example requests it handles
  * "Verify the merged PDF has 40 pages and opens."

## Notes
Provenance: outputs cite their source page/section where relevant.
