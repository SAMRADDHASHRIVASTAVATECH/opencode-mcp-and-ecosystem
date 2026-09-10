---
name: pdf-analyze
title: "Analyze a document"
category: "PDF Management"
version: 1.0.0
engine: "core.inspect + core.resource:strategy"
preferred_tool: "PyMuPDF + resource-aware strategy"
fallback_tool: "—"
validation: "profile produced"
---
# Analyze a document  (`pdf-analyze`)

Analyze a document

> Part of the **Universal PDF Management & Creation Skill Repository**.
> Category: **PDF Management**.
> Every skill is individually callable (INDIVIDUAL MODE) and may also be
> invoked automatically by the orchestrator (SYSTEM MODE).

## When to use
Characterise a document before expensive operations and pick a strategy.

## Operations
- statistical profile
- structure & resource analysis
- text-layer health
- routing hints (OCR? huge? tables?)

## Engine (what actually executes this)
`universal_pdf/core.inspect + core.resource:strategy`

All heavy lifting is done on disk / one page at a time by the shared engine —
never by loading the document into an LLM context.

## Tools & graceful degradation
- Preferred tool: **PyMuPDF + resource-aware strategy**
- Fallback: **—**

If the preferred backend is unavailable the skill transparently uses the
fallback or reports a documented limitation. It **never** reports success when
an operation did not actually happen.

## Validation (this skill attaches checks to its Outcome)
profile produced

## Related skills
`pdf-inspect`, `pdf-ocr`, `pdf-validation`, `pdf-orchestrate`

## Example requests it handles
  * "Analyze this PDF and decide whether it needs OCR."

## Notes
Provenance: outputs cite their source page/section where relevant.
