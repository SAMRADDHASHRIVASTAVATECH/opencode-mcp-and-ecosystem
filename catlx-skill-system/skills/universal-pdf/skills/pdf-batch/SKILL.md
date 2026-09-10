---
name: pdf-batch
title: "Batch operations over many PDFs"
category: "PDF Management"
version: 1.0.0
engine: "registry/batch spec + core modules (streamed per-file)"
preferred_tool: "per-file engine calls + checkpointing"
fallback_tool: "—"
validation: "per-file success/failure tracked; aggregate report"
---
# Batch operations over many PDFs  (`pdf-batch`)

Batch operations over many PDFs

> Part of the **Universal PDF Management & Creation Skill Repository**.
> Category: **PDF Management**.
> Every skill is individually callable (INDIVIDUAL MODE) and may also be
> invoked automatically by the orchestrator (SYSTEM MODE).

## When to use
Run pipelines over folders of PDFs without loading them all at once.

## Operations
- inspect many
- classify
- rename
- metadata
- compress
- convert
- index
- report
- never holds every doc in context

## Engine (what actually executes this)
`universal_pdf/registry/batch spec + core modules (streamed per-file)`

All heavy lifting is done on disk / one page at a time by the shared engine —
never by loading the document into an LLM context.

## Tools & graceful degradation
- Preferred tool: **per-file engine calls + checkpointing**
- Fallback: **—**

If the preferred backend is unavailable the skill transparently uses the
fallback or reports a documented limitation. It **never** reports success when
an operation did not actually happen.

## Validation (this skill attaches checks to its Outcome)
per-file success/failure tracked; aggregate report

## Related skills
`pdf-orchestrate`, `pdf-document-state`, `pdf-validation`

## Example requests it handles
  * "Process all 100 invoices in this folder: compress, OCR, index."

## Notes
Provenance: outputs cite their source page/section where relevant.
