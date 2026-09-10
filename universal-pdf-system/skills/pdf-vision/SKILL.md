---
name: pdf-vision
title: "Visual interpretation of pages/figures"
category: "PDF Management"
version: 1.0.0
engine: "core.vision:describe_page  (register a provider first)"
preferred_tool: "pluggable vision provider (agent/LLM)"
fallback_tool: "text/OCR extraction"
validation: "description returned when provider present"
---
# Visual interpretation of pages/figures  (`pdf-vision`)

Visual interpretation of pages/figures

> Part of the **Universal PDF Management & Creation Skill Repository**.
> Category: **PDF Management**.
> Every skill is individually callable (INDIVIDUAL MODE) and may also be
> invoked automatically by the orchestrator (SYSTEM MODE).

## When to use
Only invoke vision when text/OCR is insufficient to answer the request.

## Operations
- describe a rendered page
- interpret charts/graphs/diagrams/forms
- graceful fallback to text/OCR when no vision model

## Engine (what actually executes this)
`universal_pdf/core.vision:describe_page  (register a provider first)`

All heavy lifting is done on disk / one page at a time by the shared engine —
never by loading the document into an LLM context.

## Tools & graceful degradation
- Preferred tool: **pluggable vision provider (agent/LLM)**
- Fallback: **text/OCR extraction**

If the preferred backend is unavailable the skill transparently uses the
fallback or reports a documented limitation. It **never** reports success when
an operation did not actually happen.

## Validation (this skill attaches checks to its Outcome)
description returned when provider present

## Related skills
`pdf-ocr`, `pdf-render`, `pdf-extract`, `pdf-orchestrate`

## Example requests it handles
  * "What does the chart on page 12 show?"
  * "Describe the diagram on page 3."

## Notes
Provenance: outputs cite their source page/section where relevant.
