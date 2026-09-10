# Screen Understanding — Canonical Reference

> Source: PART V §5.5 (OCR — Screen Understanding), extended by the component tree (PART XVII). The
> single authoritative source for screen-to-structure extraction and the `ScreenModel`.

## Purpose

The Screen Understanding capability converts screen regions into structured, machine-readable text and
interactive surface models. It is the tier-scaled OCR + UIA element-classification subset of the Desktop
Control Engine, and it provides the structural data the Workflow Engine uses to make click/type/scroll
decisions **without hardcoded coordinates**.

## Tier-scaled OCR backends (from the Capability Map)

| Tier | Backend | Notes |
|---|---|---|
| T0 | Tesseract 5.x (`eng+osd`) on CPU | Lowest resource cost |
| T1 | Tesseract + result cache | Avoids re-OCR of static regions |
| T2+ | EasyOCR or PaddleOCR with GPU | Near-instant full-screen text extraction |

## Screen Understanding layer (post-processing)

Applied to detected text to produce a `ScreenModel`:

1. **UI element classification** — buttons, input fields, labels, links, text blocks.
2. **Spatial relationship extraction** — layout, grouping, relative positions of elements.
3. **Element state detection** — enabled/disabled, checked/unchecked, focused.

## ScreenModel

A structured JSON representation of the screen's interactive surface. Fields include element type,
bounding box (in logical, display-normalized coordinates), text/label, accessibility name if available,
state, and relationships. The Workflow Engine consumes the ScreenModel to choose targets and to verify
actions. ScreenModel is computed per-display by default and merged into a global ScreenModel on request
(see `§5.9` Multi-Monitor).

## Where it runs (Environment Routing)

- `LOCAL_PROCESS` for small regions / low tiers.
- `LOCAL_SUBPROCESS` (T1+) for CPU-bound OCR.
- `LOCAL_CONTAINER` (T2+) for GPU-accelerated EasyOCR/PaddleOCR.

## Integration points

- **Desktop Control Engine** calls Screen Understanding for legacy-app automation and for any target
  that lacks an accessibility tree.
- **Browser Automation** uses the injected extension to read DOM state instead of OCR when the browser
  is a first-party target (OCR is the fallback).
- **Workflow Engine** uses the `ScreenModel` to plan and verify steps (whether the target exists, its
  state, whether the action succeeded).

## Cross-references
- Consumed by: `skills/catlx-screen-understanding/SKILL.md`.
- Delegates to / depends on: `catlx-hardware-adaptation` (CapabilityMap `ocr_backend`), `catlx-capability-routing` (environment routing).
- Source tree: `knowledge/references/folder-structure.md` (`desktop-control/ocr`, `desktop-control/screen-model`).
