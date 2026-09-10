---
name: pdf-chunk
title: "Context-safe chunking for large/small-model docs"
category: "PDF Management"
version: 1.0.0
engine: "core.chunk:chunk_document / chunk_text"
preferred_tool: "local chunker (page & word boundaries)"
fallback_tool: "—"
validation: "chunks>=1"
---
# Context-safe chunking for large/small-model docs  (`pdf-chunk`)

Context-safe chunking for large/small-model docs

> Part of the **Universal PDF Management & Creation Skill Repository**.
> Category: **PDF Management**.
> Every skill is individually callable (INDIVIDUAL MODE) and may also be
> invoked automatically by the orchestrator (SYSTEM MODE).

## When to use
Prepare any document for retrieval without ever filling the context window.

## Operations
- chunk by page
- chunk by max chars w/ overlap
- persist chunks + page text
- only the needed chunks are ever passed to the model

## Engine (what actually executes this)
`universal_pdf/core.chunk:chunk_document / chunk_text`

All heavy lifting is done on disk / one page at a time by the shared engine —
never by loading the document into an LLM context.

## Tools & graceful degradation
- Preferred tool: **local chunker (page & word boundaries)**
- Fallback: **—**

If the preferred backend is unavailable the skill transparently uses the
fallback or reports a documented limitation. It **never** reports success when
an operation did not actually happen.

## Validation (this skill attaches checks to its Outcome)
chunks>=1

## Related skills
`pdf-summarize`, `pdf-qa`, `pdf-index`, `pdf-provenance`

## Example requests it handles
  * "Chunk this document for later Q&A."

## Notes
Provenance: outputs cite their source page/section where relevant.
