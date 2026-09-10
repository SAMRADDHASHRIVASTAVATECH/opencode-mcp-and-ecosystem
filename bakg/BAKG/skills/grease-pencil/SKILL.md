---
name: grease-pencil
description: Grease Pencil 3 (Blender 4.3+) object model, 2D drawing and animation, GP materials and looks, classic 2D inside Blender, and hybrid 2D-3D pipelines.
system: BAKG
version: 2.0.0
status: production
group: hybrid
domains: [D130]
knowledge:
  - knowledge/depth/ch40-grease-pencil.md
  - knowledge/domains/ch01-preproduction.md
---

# grease-pencil

## Purpose

2D inside Blender: boards, animatics, 2D characters, overlays, cleanup sketches, and hybrid 2D-3D shots that live or die in compositing.

## Scope

D130 [OPT], Depth 40. Story structure still `preproduction`. Final 3D lookdev is `lookdev`. Comp of hybrids is `render-comp`.

## Activation Conditions

- Grease Pencil, 2D animation in Blender, GP boards, 2D overlays, hybrid 2D-3D
- `Use grease-pencil`

## Non-Activation Conditions

- Pure 3D character pipeline with no 2D (skip)
- Photoshop concept painting outside Blender (character-design may still use it)
- Final grade (→ render-comp)

## Instructions

1. GP3 object model (40.1): object → layers → strokes/fills; in 3D space.
2. Drawing & animation (40.2): onion skin, Dope Sheet, keyframe strokes, interpolate carefully.
3. Materials & looks (40.3): make it look like 2D, not 3D-with-lines. Lights optional; often self-display.
4. Classic 2D workflow (40.4): rough → cleanup → fill → FX layers.
5. Hybrid pipelines (40.5): GP characters over 3D sets; GP FX over 3D; 3D characters with GP outlines (also Ch 18.4).
6. Performance (40.6): stroke budget, simplify, viewport.
7. Comp rule: render GP and 3D as separate passes with matching color management (AgX) and grade together. The 2D/3D discrepancy is a grade/lighting problem more than a stroke problem.
8. For boards: camera notation still required (preproduction D09).

## Procedures

### Boarding in GP
Draw in camera view; one layer per character/bg; export frames to VSE animatic.

### Hybrid shot
3D scene holdout or depth; GP in scene or as overlay collection; view layers; comp.

## Decision Logic

Use GP when 2D is the look or the fastest board. Don't replace a 3D pipeline that needs 3D.

## Inputs

- Boards need / 2D look / overlay FX / hybrid intent, cameras, style

## Outputs

- GP objects/layers
- 2D animation or boards
- View-layer/comp notes for hybrid
- Shared state: boards source = GP if so

## Tools

Grease Pencil 3 (4.3+), onion skin, GP modifiers, Line Art modifier (related outline method). Depth 40.

## Constraints

GP3 rewrite in 4.3 — don't assume GP2 workflows. Don't mix color management. Don't infinite-stroke a fill that a material can do.

## Edge Cases

- Anime outlines: Line Art vs GP vs hull (5.17) — pick one hero method.
- Magical-girl 2D FX over 3D body: this skill + vfx + render-comp.

## Failure Modes & Fixes

| FAIL | FIX |
|---|---|
| Looks like 3D lines on a model | GP materials; lighting off; comp |
| Lag | Stroke budget; simplify (40.6) |
| Drift vs 3D | Parent to camera or 3D empty; same focal |
| Board without camera notes | Add D106 notation |

## Dependencies

- Feeds preproduction animatic
- Feeds render-comp hybrids
- Optional outline method for lookdev NPR

## Related Skills

preproduction, lookdev, vfx, render-comp, cinematography

## Delegation Rules

- Story beats → preproduction
- Toon shader body → lookdev Ch 18
- Comp merge → render-comp Ch 36
- If user wants a full 2D film in GP, stay here for craft; still use preproduction for story

## Examples

- Animatic: GP boards in camera, VSE cut to temp music.
- Hybrid: 3D city, GP rain streaks and character, graded together.

## Required Knowledge / Context

- `knowledge/depth/ch40-grease-pencil.md`
- `knowledge/domains/ch01-preproduction.md` (D130, D09, D10)

## References to Shared Resources

- `decision-engine` 5.17
- `examples/E-anime-magical-girl.md`
