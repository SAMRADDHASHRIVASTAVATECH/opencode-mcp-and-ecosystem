---
name: character-design
description: Character/creature concept, silhouette and shape language, spec sheets, reference boards, AI concept exploration, and style guides — the cheapest high-impact decisions in the pipeline.
system: BAKG
version: 2.0.0
status: production
group: creative
domains: [D03, D04, D05, D06, D07, D08, D138]
knowledge:
  - knowledge/domains/ch01-preproduction.md
  - knowledge/system/02d-depth-supplements.md
  - knowledge/depth/ch16-anatomy-proportions.md
  - knowledge/depth/ch39-ai-concept.md
---

# character-design

## Purpose

Make personality readable at a glance (silhouette first, then color, then detail) and produce the contracts 3D will obey: character sheets, creature spec sheets, reference boards, style rules.

## Scope

D03 Character Concept [SIT], D04 Character Design [REQ], D05 Creature Design [SIT], D06 AI Concept [OPT], D07 Reference [REQ], D08 Character Sheets [SIT — required for any character], D138 Style Guides [SIT]. Does not model, sculpt, or rig.

## Activation Conditions

- User asks to design a character or creature, silhouette, proportions, turnaround, expression sheet, style guide, or AI concepts
- Orchestrator fires design stages
- `Use character-design`

## Non-Activation Conditions

- Modeling/sculpting execution (→ modeling / sculpting-anatomy)
- Acting/performance (→ animation)
- World visual build (→ environment)
- Pure story beats without a character (→ preproduction)

## Instructions

1. Concept before drawing (D03): role, 3–5 adjectives, temperament, energy, physical capability, movement style, age, flaw. Personality must be readable in silhouette and motion.
2. Thumbnails: 10–20 black silhouettes. Pick 3–5. Blur test: if unrecognizable, silhouette fails. Never "fix it in 3D."
3. Shape language: round=soft/friendly, angular=aggressive, vertical=authority, horizontal=stability/weight.
4. Palette: 2–3 dominant + 1 accent; avoid equal-value colors.
5. Detail hierarchy: eye lands on face/hands/emblem.
6. Proportions (lock with Ch 16 numbers):
   - Realistic human ~7–8 heads; heroic 8–9; stylized 2–5; chibi 1–2.
7. Creature: fill `templates/creature-spec.md`. Real-world anchor ("it's like a ___ but ___"). Run the four believability checks. If no, fix design not animation.
8. Reference boards (D07) per asset: anatomy, material, lighting, motion, style. PureRef or image planes. Study ritual before modeling.
9. Character sheets (D08): turnaround (same height line), proportion grid, 6–12 expressions, hands/feet, scale vs env, material callouts.
10. AI (D06) is CONCEPT / REFERENCE / EXPLORATION only — never a production asset. Translate to a human-cleaned sheet before 3D. ControlNet for useful structure. See Depth 39.
11. Write style rules (D138) that lookdev, lighting, and animation must obey.
12. Lock design before blockout.

## Procedures

### Design → Shape language → Silhouette → Readability
Silhouette → value contrast → negative space → focal detail → hierarchy → color → texture callout → material plan.
Proportions → head ratio → limb ratio → center of mass → posture → weight feel → motion implication.

### Creature spec → downstream
Locomotion class drives D69–D73. Surface plan drives D32/D44/D45/Ch 17. Sensory plan drives head + D60. Functional extras get rigs.

### AI-to-3D bridge (critical rule)
Choose best variant → redraw as clean sheet (D08) → resolve proportions/consistency → then D19/D20 modeling. Do not retopo an AI image and call it a character.

## Decision Logic

- Style unset → decision 5.1, then lock.
- Creature vs character: if non-human anatomy, D05 is mandatory.
- AI optional; never a substitute for the sheet.
- Background characters: simpler sheets, still a silhouette and scale.

## Inputs

- Story role, world constraints, style, medium
- Optional sketches or AI images

## Outputs

- Concept sheet
- Approved silhouette + shape language + palette
- Character sheet (or creature spec)
- Reference board list
- Style rules (D138)
- Proportion numbers
- Shared state: `characters[]` / `creatures[]` / `style_rules`

## Tools

Thumbnailing (any 2D), PureRef, Blender image planes, optional local SD/SDXL/ComfyUI (Depth 39). Ch 16 proportion tables.

## Constraints

No front-only sheets. No designing the body before personality. No AI as final. No extra limbs the rig cannot support unless mechanical.

## Edge Cases

- Hybrid humanoid-creature: both D04 and D05.
- Mechanical character: shape language still applies; surface is hard-surface (D18).
- Multi-character show: scale sheet is mandatory.

## Failure Modes & Fixes

| MIST | FIX |
|---|---|
| Pretty but lifeless | Return to D03 personality |
| Front-only | Draw side/back now |
| Too much detail everywhere | Restore hierarchy |
| Wings on an elephant | Fail believability; redesign mass |
| 8 legs animated like 2 pairs | Spec locomotion class; later D71 |
| AI used as production asset | Human-clean the sheet |

## Dependencies

- Consumes `preproduction` world/story
- Drives `modeling`, `sculpting-anatomy`, `lookdev`, `costume-groom`, `rigging`, `animation`
- Delegates proportion numbers to `sculpting-anatomy` (Ch 16)
- Delegates AI toolkit depth to `knowledge/depth/ch39-ai-concept.md`

## Related Skills

preproduction, sculpting-anatomy, modeling, lookdev, costume-groom, grease-pencil

## Delegation Rules

- Anatomy tables / joint ranges → `sculpting-anatomy`
- "How do I model this sheet" → `modeling`
- Clothing as design intent stays here; construction → `costume-groom`
- Whole-film idea → `bakg-orchestrator`

## Examples

- Chibi knight: 2 heads, round shapes, 2-color + gold accent, turnaround, 6 expressions, scale vs castle door.
- Six-legged crystal creature: spec locomotion multi-leg 6, mass medium, surface crystal (Ch 17 gems), cloak as costume not body, no fur.

## Required Knowledge / Context

- `knowledge/domains/ch01-preproduction.md` (D03–D08)
- `knowledge/system/02d-depth-supplements.md` (S-01, S-02, S-03)
- `knowledge/depth/ch16-anatomy-proportions.md`
- `knowledge/depth/ch39-ai-concept.md`

## References to Shared Resources

- `templates/character-sheet.md`
- `templates/creature-spec.md`
- `examples/C-original-creature.md`
