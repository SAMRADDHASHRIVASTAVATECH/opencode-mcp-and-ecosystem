---
name: pdf-index
title: "Build a reusable search index"
category: "PDF Management"
version: 1.0.0
engine: "core.search:build_index"
preferred_tool: "positional inverted index (JSON)"
fallback_tool: "SQLite/DB backend for huge corpora"
validation: "indexed terms > 0"
---
# Build a reusable search index  (`pdf-index`)

Build a reusable search index

> Part of the **Universal PDF Management & Creation Skill Repository**.
> Category: **PDF Management**.
> Every skill is individually callable (INDIVIDUAL MODE) and may also be
> invoked automatically by the orchestrator (SYSTEM MODE).

## When to use
For huge or repeatedly-queried documents, index once then retrieve fast.

## Operations
- positional term index
- page-level inverted index
- persisted JSON
- reuse across queries without re-parsing

## Engine (what actually executes this)
`universal_pdf/core.search:build_index`

All heavy lifting is done on disk / one page at a time by the shared engine —
never by loading the document into an LLM context.

## Tools & graceful degradation
- Preferred tool: **positional inverted index (JSON)**
- Fallback: **SQLite/DB backend for huge corpora**

If the preferred backend is unavailable the skill transparently uses the
fallback or reports a documented limitation. It **never** reports success when
an operation did not actually happen.

## Validation (this skill attaches checks to its Outcome)
indexed terms > 0

## Related skills
`pdf-search`, `pdf-chunk`, `pdf-document-state`, `pdf-orchestrate`

## Example requests it handles
  * "Index this manual so I can query it repeatedly."

## Notes
Provenance: outputs cite their source page/section where relevant.
