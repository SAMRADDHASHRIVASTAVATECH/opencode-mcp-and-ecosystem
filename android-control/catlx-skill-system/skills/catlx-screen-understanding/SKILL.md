---
name: catlx-screen-understanding
description: "Handles CATLX OCR and screen understanding: tier-scaled OCR backends (Tesseract, EasyOCR, PaddleOCR), post-processing to classify UI elements and detect their state, spatial relationship extraction, and the ScreenModel JSON that lets the Workflow Engine act without hardcoded coordinates. Use when the user asks about OCR, reading the screen, screen models, UI element classification, or how CATLX understands what's on screen."
metadata:
  catlx: subsystem
  category: interface
  subsystem: Desktop_Control_Engine
  capability: screen-understanding
  version: "1.0.0"
  source: "PART V §5.5"
  aliases: "ocr, screen reading, screen understanding, screen model, screenshot, vision"
  depends-on: "catlx-hardware-adaptation, catlx-security"
---

# CATLX — OCR & Screen Understanding

This skill owns **reading the screen as structured data**: converting screen regions to text and then to a
structured `ScreenModel` of the interactive surface that downstream automation uses. This is a distinct,
tier-scaled capability within the Desktop Control Engine.

> Canonical detail: `../../knowledge/references/screen-understanding.md` and
> `../../knowledge/references/desktop-control.md` §5.5. Example output: `../examples` (see
> `../../examples/screen-model.json`). Load on demand.

---

## Purpose

Produce machine-readable structure from pixels so the Workflow Engine and DCE can click, type, and verify
actions WITHOUT hardcoded coordinates, and can work with legacy apps that lack accessibility trees.

## When to activate

- User asks how CATLX reads/understands the screen, or about OCR and screen models.
- Automating a legacy app (no UIAutomation tree).
- Verifying a UI action by reading screen state.

## What this skill handles

1. **Tier-scaled OCR backends** (from CapabilityMap `ocr_backend`):
   - T0: Tesseract 5.x (`eng+osd`) on CPU.
   - T1: Tesseract + result cache (avoid re-OCR of static regions).
   - T2+: EasyOCR / PaddleOCR with GPU for near-instant full-screen extraction.
2. **Screen Understanding post-processing** — from raw detected text: UI element classification (buttons,
   input fields, labels, links, text blocks), spatial relationship extraction, and element state detection
   (enabled/disabled, checked/unchecked, focused).
3. **`ScreenModel`** — a structured JSON of the screen's interactive surface: element type, bounding box,
   label/accessibility name, state, and spatial relationships. Example in `../../examples/screen-model.json`.
4. **Per-display + global merge** — ScreenModels are computed per display by default and merged into a
   global ScreenModel on request (multi-monitor).

## Requirements / constraints

- Environment routing picks the OCR execution context: `LOCAL_PROCESS` (small regions), `LOCAL_SUBPROCESS`
  (T1+ CPU OCR), `LOCAL_CONTAINER` (T2+ GPU EasyOCR/PaddleOCR).
- **R5:** screen read is gated by the permission router (global toggle + per-app exclusions).
- The `ScreenModel` is the contract the Workflow Engine consumes; do not bypass it with raw coordinates.

## Canonical knowledge it reads

`../../knowledge/references/screen-understanding.md` · `../../knowledge/references/desktop-control.md` ·
`../../knowledge/references/hardware-adaptation.md` · `../../knowledge/references/security.md`.

## Delegation

- **Which OCR backend per tier** → delegate to `catlx-hardware-adaptation`
  (`skill({ name: "catlx-hardware-adaptation" })`).
- **Where OCR executes + fallback** → delegate to `catlx-capability-routing`
  (`skill({ name: "catlx-capability-routing" })`).
- **Acting on the ScreenModel (click/type)** → delegate to `catlx-desktop-control`
  (`skill({ name: "catlx-desktop-control" })`).
- **Permission for screen capture** → delegate to `catlx-security`
  (`skill({ name: "catlx-security" })`).
- **GPU container (T2+ EasyOCR)** → delegate to `catlx-docker` (`skill({ name: "catlx-docker" })`).

## Edge cases & warnings

- **Static regions:** use the result cache on T1 to avoid wasteful re-OCR.
- **Dynamic content / animation:** re-OCR the affected region; never trust stale ScreenModel state.
- **Full-screen capture cost:** prefer targeted regions; use GPU/container on T2+ for full-screen.
- **Per-app exclusions:** respect the permission router's screen-read exclusions (e.g. password managers).
- Security risk of reading sensitive screen content — audit and gate.

## Component lifecycle policy (reuse → install → adapt → create)

**NEVER create a new component as the default.** Before building/creating anything (a sub-skill, dependency,
reference, workflow, helper, adapter, or template), check, in order:
1. **Reuse** an existing local component (resolve aliases/equivalent capabilities first) — reuse, don't rebuild.
2. **Use** an already-registered component from the registry.
3. **Install** a suitable existing, trusted, supported component → validate → register → connect to the graph → use.
4. **Adapt** an existing compatible component via a small persistent adapter/wrapper instead of re-creating it.
5. **Create only as last resort** — then make it permanent immediately: stable id, canonical location, register,
   add to the capability index + dependency graph, add provenance, use, and allow future reuse.
6. Never reorganise/recreate already-generated components (no `Skill X 2` / `new` / `temp` variants); extend the
   existing one. Never create a second competing knowledge source; connect back to the canonical `knowledge/` layer.
   Promote any reusable artifact out of `/tmp`/scratch into the permanent ecosystem.

> Full policy: `../../knowledge/rules/component-lifecycle.md`.

## Source / provenance

- **Source:** PART V §5.5 (OCR — Screen Understanding) as a tier-scaled, post-processed capability; echoed in
  the component tree (PART XVII §17.1: OCR Engine, Screen Understanding Layer).
- **Inferred/adapted:** Windows OCR (Tesseract/EasyOCR/PaddleOCR run on Windows); the ScreenModel structure is
  a faithful representation of the source's elements/state/spatial requirements.
