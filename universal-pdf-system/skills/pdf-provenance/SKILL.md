---
name: pdf-provenance
title: "Track source provenance"
category: "PDF Management"
version: 1.0.0
engine: "core.provenance:Provenance / anchor"
preferred_tool: "content fingerprinting"
fallback_tool: "—"
validation: "derived items carry source"
---
# Track source provenance  (`pdf-provenance`)

Track source provenance

> Part of the **Universal PDF Management & Creation Skill Repository**.
> Category: **PDF Management**.
> Every skill is individually callable (INDIVIDUAL MODE) and may also be
> invoked automatically by the orchestrator (SYSTEM MODE).

## When to use
Every extracted/derived item keeps where it came from for trustworthy Q&A.

## Operations
- source path + content fingerprint
- page/section/chunk/object attribution
- extraction method + confidence
- document_id anchors

## Engine (what actually executes this)
`universal_pdf/core.provenance:Provenance / anchor`

All heavy lifting is done on disk / one page at a time by the shared engine —
never by loading the document into an LLM context.

## Tools & graceful degradation
- Preferred tool: **content fingerprinting**
- Fallback: **—**

If the preferred backend is unavailable the skill transparently uses the
fallback or reports a documented limitation. It **never** reports success when
an operation did not actually happen.

## Validation (this skill attaches checks to its Outcome)
derived items carry source

## Related skills
`pdf-qa`, `pdf-search`, `pdf-document-state`, `pdf-orchestrate`

## Example requests it handles
  * "Cite the page for every answer you give me."

## Notes
Provenance: outputs cite their source page/section where relevant.
