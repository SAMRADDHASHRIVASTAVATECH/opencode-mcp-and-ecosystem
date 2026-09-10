---
name: cinematography
description: Camera object, shot language, composition, lens and perspective, shot design per beat, camera movement, continuity, and match moving for live-action integration.
system: BAKG
version: 2.0.0
status: production
group: image
domains: [D102, D103, D104, D105, D106, D107, D132]
knowledge:
  - knowledge/domains/ch12-cinematography.md
  - knowledge/depth/ch21-cinematography-theory.md
  - knowledge/system/02d-depth-supplements.md
---

# cinematography

## Purpose

The camera is the audience's eye. Decide what they see, when, from where, and why — serving the beat, not the "cool" angle.

## Scope

D102–D107, D132 match moving (S-17), Depth 21 shot grammar, composition systems, continuity, pacing, transitions.

## Activation Conditions

- Camera, lens, DoF, shot size, 180 rule, composition, camera move, match move / camera track
- `Use cinematography`

## Non-Activation Conditions

- Lighting setups (→ lighting)
- Animatic drawing (→ preproduction / grease-pencil) unless converting boards to 3D cameras
- Final cut (→ production-finishing) though continuity rules bind the editor

## Instructions

1. One camera object per shot; lens from D105; sensor; DoF decision (5.7).
2. Shot language (D103 / Ch 21): coverage, 180° rule, eyeline, continuity.
3. Composition (D104 / 21.2): rule of thirds, golden, silhouette, negative space, leading lines, frame within frame. Read at small size.
4. Lens (D105): long = compressed/intimate or surveillance; wide = space/distortion/power. Match real focal lengths for live-action (D132).
5. Shot design (D106 / 21.4 / 38.4): size/angle/move decided per beat. Don't change all three at once without reason.
6. Movement (D107): motivated only. Dolly, crane, handheld, shake. Hard stops = weight. Cameras obey the 12 principles.
7. Match moving (D132 / S-17): Clip editor detect/solve, error < 0.5 px good, > 1.5 re-track; ground plane; test cube must not slide; then CG; match grain/MB.
8. Continuity & editing rules (21.3) — coordinate with production-finishing.

## Procedures

### Shot design table
Close-up = emotion; medium = acting; wide = geography/power. Low angle = power; high = vulnerability. Dutch = unease (don't overuse).

### Motivated move
If the camera moves, a character/thought/reveal moves it. No sightseeing.

## Decision Logic

- Previs cameras come from boards.
- Horror (Example F): low POV, Dutch, ECU candle, silhouette creature.
- DoF: hero CU realism render; otherwise cheap in comp.

## Inputs

- Boards/animatic, beat list, style, set scale, whether live-action plate

## Outputs

- Camera per shot (focal length, film back, move)
- Composition notes
- Match-move solve if any
- Shared state: cameras locked for animation

## Tools

Camera object, camera locking, motion tracking, DoF, graph editor on camera. Ch 21 tables. S-17.

## Constraints

Don't violate 180 without a cut that resets. Don't animate characters to a camera you plan to replace. Don't ignore solve error.

## Edge Cases

- Orthographic stylized: legal; document it.
- Tiny creature vs giant mech: two scales, two lenses, same continuity.

## Failure Modes & Fixes

| FAIL | FIX |
|---|---|
| Unmotivated move | Kill the move or attach to a beat |
| Crossing the line | Reverse shot / cutaway |
| Wobbly CG in plate | Re-track; ground plane; test cube |
| Unreadable staging | Simpler size; silhouette |

## Dependencies

- Constrained by story/boards
- Constrains animation and lighting
- Match move feeds render-comp integration

## Related Skills

preproduction, animation, lighting, render-comp, grease-pencil

## Delegation Rules

- Mood light → lighting
- Final cut/pacing → production-finishing
- GP boards → grease-pencil
- If only "what lens for a portrait" → answer here (85–135 mm equivalent typical)

## Examples

- Dialogue: 180 line, OTS pair, CU for the turn.
- Dawn mech wake: wide establishing flooded street, low angle on waking, longer lens on eye-light.

## Required Knowledge / Context

- `knowledge/domains/ch12-cinematography.md`
- `knowledge/depth/ch21-cinematography-theory.md`
- S-17 match moving

## References to Shared Resources

- `workflows/shot-pipeline.md`
- `templates/shot-record.md`
