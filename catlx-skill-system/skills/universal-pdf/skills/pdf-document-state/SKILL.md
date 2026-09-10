---
name: pdf-document-state
title: "Persistent per-document knowledge state"
category: "PDF Management"
version: 1.0.0
engine: "core.state:DocumentStore + core.provenance"
preferred_tool: "SQLite knowledge store"
fallback_tool: "—"
validation: "state persists; resumable"
---
# Persistent per-document knowledge state  (`pdf-document-state`)

Persistent per-document knowledge state

> Part of the **Universal PDF Management & Creation Skill Repository**.
> Category: **PDF Management**.
> Every skill is individually callable (INDIVIDUAL MODE) and may also be
> invoked automatically by the orchestrator (SYSTEM MODE).

## When to use
Keep structured knowledge per PDF so later operations never re-parse.

## Operations
- register documents
- store pages/chunks/tables/images/sections/metadata
- pipeline step status
- summaries
- validation & error log
- provenance anchor (document_id)

## Engine (what actually executes this)
`universal_pdf/core.state:DocumentStore + core.provenance`

All heavy lifting is done on disk / one page at a time by the shared engine —
never by loading the document into an LLM context.

## Tools & graceful degradation
- Preferred tool: **SQLite knowledge store**
- Fallback: **—**

If the preferred backend is unavailable the skill transparently uses the
fallback or reports a documented limitation. It **never** reports success when
an operation did not actually happen.

## Validation (this skill attaches checks to its Outcome)
state persists; resumable

## Related skills
`pdf-chunk`, `pdf-index`, `pdf-provenance`, `pdf-orchestrate`

## Example requests it handles
  * "Cache this document's structure for reuse."
  * "Resume processing from where it stopped."

## Notes
Provenance: outputs cite their source page/section where relevant.
