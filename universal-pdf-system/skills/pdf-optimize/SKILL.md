---
name: pdf-optimize
title: "Optimize with quality profiles"
category: "PDF Management"
version: 1.0.0
engine: "core.compress:compress_pdf(profile=...)"
preferred_tool: "PyMuPDF"
fallback_tool: "structural-only cleanup"
validation: "openable; size reported per profile"
---
# Optimize with quality profiles  (`pdf-optimize`)

Optimize with quality profiles

> Part of the **Universal PDF Management & Creation Skill Repository**.
> Category: **PDF Management**.
> Every skill is individually callable (INDIVIDUAL MODE) and may also be
> invoked automatically by the orchestrator (SYSTEM MODE).

## When to use
Choose the right quality/size tradeoff for the destination.

## Operations
- maximum_quality
- balanced
- small_size
- web_optimized
- archive_optimized
- never silently destroy quality

## Engine (what actually executes this)
`universal_pdf/core.compress:compress_pdf(profile=...)`

All heavy lifting is done on disk / one page at a time by the shared engine —
never by loading the document into an LLM context.

## Tools & graceful degradation
- Preferred tool: **PyMuPDF**
- Fallback: **structural-only cleanup**

If the preferred backend is unavailable the skill transparently uses the
fallback or reports a documented limitation. It **never** reports success when
an operation did not actually happen.

## Validation (this skill attaches checks to its Outcome)
openable; size reported per profile

## Related skills
`pdf-compress`, `pdf-validation`, `pdf-orchestrate`

## Example requests it handles
  * "Optimize for archival (maximum quality)."
  * "Produce a small-size version for email."

## Notes
Provenance: outputs cite their source page/section where relevant.
