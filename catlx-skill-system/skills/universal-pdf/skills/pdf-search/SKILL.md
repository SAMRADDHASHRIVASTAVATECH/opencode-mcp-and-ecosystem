---
name: pdf-search
title: "Search within a PDF"
category: "PDF Management"
version: 1.0.0
engine: "core.search:search_document / find_mentions_all"
preferred_tool: "PyMuPDF text layer streaming"
fallback_tool: "persisted index (large docs)"
validation: "searched; hits carry page"
---
# Search within a PDF  (`pdf-search`)

Search within a PDF

> Part of the **Universal PDF Management & Creation Skill Repository**.
> Category: **PDF Management**.
> Every skill is individually callable (INDIVIDUAL MODE) and may also be
> invoked automatically by the orchestrator (SYSTEM MODE).

## When to use
Find every mention of a term/phrase with its source page.

## Operations
- exact/phrase search
- keyword search
- regex search
- single-page search
- whole-document mention scan (streamed)
- source page in every result

## Engine (what actually executes this)
`universal_pdf/core.search:search_document / find_mentions_all`

All heavy lifting is done on disk / one page at a time by the shared engine —
never by loading the document into an LLM context.

## Tools & graceful degradation
- Preferred tool: **PyMuPDF text layer streaming**
- Fallback: **persisted index (large docs)**

If the preferred backend is unavailable the skill transparently uses the
fallback or reports a documented limitation. It **never** reports success when
an operation did not actually happen.

## Validation (this skill attaches checks to its Outcome)
searched; hits carry page

## Related skills
`pdf-index`, `pdf-chunk`, `pdf-read`, `pdf-orchestrate`

## Example requests it handles
  * "Find every mention of 'quantum' in this 5,000 page book."
  * "Show me where the phrase 'terms of service' appears."

## Notes
Provenance: outputs cite their source page/section where relevant.
