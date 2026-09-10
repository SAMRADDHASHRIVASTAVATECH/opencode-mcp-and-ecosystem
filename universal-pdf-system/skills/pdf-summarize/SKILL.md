---
name: pdf-summarize
title: "Summarize with bounded context"
category: "PDF Management"
version: 1.0.0
engine: "core.summarize:summarize"
preferred_tool: "local extractive engine"
fallback_tool: "optional injected LLM (abstractive)"
validation: "summarized; output within configured context size"
---
# Summarize with bounded context  (`pdf-summarize`)

Summarize with bounded context

> Part of the **Universal PDF Management & Creation Skill Repository**.
> Category: **PDF Management**.
> Every skill is individually callable (INDIVIDUAL MODE) and may also be
> invoked automatically by the orchestrator (SYSTEM MODE).

## When to use
Produce a summary of any size document that fits a small model's context.

## Operations
- extractive summary
- bucket summaries for huge docs
- hierarchical summary
- persist to knowledge store
- optional abstractive via injected LLM

## Engine (what actually executes this)
`universal_pdf/core.summarize:summarize`

All heavy lifting is done on disk / one page at a time by the shared engine —
never by loading the document into an LLM context.

## Tools & graceful degradation
- Preferred tool: **local extractive engine**
- Fallback: **optional injected LLM (abstractive)**

If the preferred backend is unavailable the skill transparently uses the
fallback or reports a documented limitation. It **never** reports success when
an operation did not actually happen.

## Validation (this skill attaches checks to its Outcome)
summarized; output within configured context size

## Related skills
`pdf-chunk`, `pdf-qa`, `pdf-search`, `pdf-orchestrate`

## Example requests it handles
  * "Summarize this book in one page."
  * "Give me a chapter-by-chapter summary."

## Notes
Provenance: outputs cite their source page/section where relevant.
