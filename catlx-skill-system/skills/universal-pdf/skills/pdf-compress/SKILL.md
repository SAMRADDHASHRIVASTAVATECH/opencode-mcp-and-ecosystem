---
name: pdf-compress
title: "Reduce file size"
category: "PDF Management"
version: 1.0.0
engine: "core.compress:compress_pdf(profile=...)"
preferred_tool: "PyMuPDF rewrite_images + garbage/deflate"
fallback_tool: "structural-only cleanup"
validation: "openable; final_size <= original"
---
# Reduce file size  (`pdf-compress`)

Reduce file size

> Part of the **Universal PDF Management & Creation Skill Repository**.
> Category: **PDF Management**.
> Every skill is individually callable (INDIVIDUAL MODE) and may also be
> invoked automatically by the orchestrator (SYSTEM MODE).

## When to use
Shrink a PDF for email/web while choosing a quality profile.

## Operations
- structural cleanup
- image recompression
- reported savings
- quality/size profiles

## Engine (what actually executes this)
`universal_pdf/core.compress:compress_pdf(profile=...)`

All heavy lifting is done on disk / one page at a time by the shared engine —
never by loading the document into an LLM context.

## Tools & graceful degradation
- Preferred tool: **PyMuPDF rewrite_images + garbage/deflate**
- Fallback: **structural-only cleanup**

If the preferred backend is unavailable the skill transparently uses the
fallback or reports a documented limitation. It **never** reports success when
an operation did not actually happen.

## Validation (this skill attaches checks to its Outcome)
openable; final_size <= original

## Related skills
`pdf-optimize`, `pdf-repair`, `pdf-orchestrate`

## Example requests it handles
  * "Compress this PDF as much as possible."
  * "Make a web-optimized copy."

## Notes
Provenance: outputs cite their source page/section where relevant.
