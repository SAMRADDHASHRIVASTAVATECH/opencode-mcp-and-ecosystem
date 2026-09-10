---
name: pdf-qa
title: "Question answering over a document"
category: "PDF Management"
version: 1.0.0
engine: "core.qa:answer  (uses index/chunks + an injected reasoning callable)"
preferred_tool: "retrieval over index/chunks"
fallback_tool: "no-model: returns retrieved evidence"
validation: "answer grounded in retrieved pages"
---
# Question answering over a document  (`pdf-qa`)

Question answering over a document

> Part of the **Universal PDF Management & Creation Skill Repository**.
> Category: **PDF Management**.
> Every skill is individually callable (INDIVIDUAL MODE) and may also be
> invoked automatically by the orchestrator (SYSTEM MODE).

## When to use
Answer questions against a document, giving page citations.

## Operations
- locate relevant pages/chunks
- extract evidence with provenance
- compose an answer from context only
- no document in the model context

## Engine (what actually executes this)
`universal_pdf/core.qa:answer  (uses index/chunks + an injected reasoning callable)`

All heavy lifting is done on disk / one page at a time by the shared engine —
never by loading the document into an LLM context.

## Tools & graceful degradation
- Preferred tool: **retrieval over index/chunks**
- Fallback: **no-model: returns retrieved evidence**

If the preferred backend is unavailable the skill transparently uses the
fallback or reports a documented limitation. It **never** reports success when
an operation did not actually happen.

## Validation (this skill attaches checks to its Outcome)
answer grounded in retrieved pages

## Related skills
`pdf-chunk`, `pdf-search`, `pdf-summarize`, `pdf-orchestrate`

## Example requests it handles
  * "Which section discusses pricing?"
  * "Summarize the refund policy from this 10k-page doc."

## Notes
Provenance: outputs cite their source page/section where relevant.
