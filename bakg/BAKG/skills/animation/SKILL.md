---
name: animation
description: Performance pipeline from blocking to polish — 12 principles in Blender practice, locomotion (human, animal, invented, multi-leg, flight, swim), acting, fighting, facial animation, lip sync, secondary motion, NLA, Graph Editor mastery.
system: BAKG
version: 2.0.0
status: production
group: performance
domains: [D61, D62, D64, D65, D66, D67, D68, D69, D70, D71, D72, D73, D74, D75, D76, D77, D78]
knowledge:
  - knowledge/domains/ch08-animation.md
  - knowledge/domains/ch07-facial.md
  - knowledge/depth/ch29-animation-depth.md
---

# animation

## Purpose

Turn keyframes into performance. Animation without a story is motion; with a story it's meaning. Deliver shots that read at small size, with clean contacts, arcs, intent, and a lock.

## Scope

D61 Facial Animation [SIT], D62 Lip Sync [SIT], D64–D78. Requires a signed-off rig. Creature motion uses D05 spec + Ch 16, but the *performance* lives here.

## Activation Conditions

- Animate, walk cycle, acting, lip sync, polish, graph editor, NLA, gait, flight, fight, secondary
- `Use animation`

## Non-Activation Conditions

- Rig not signed off (→ rigging)
- Designing the creature's skeleton logic (→ character-design / sculpting-anatomy)
- Simulating cloth as the primary task (→ costume-groom / simulation) — this skill *requests* secondary after body lock

## Instructions

1. Refuse to animate a non-final rig (economy rule 5).
2. Gather motion ref (D12). Act it out.
3. Pipeline (D64 / 29.1): blocking (stepped keys) → splining → polish. Reviews at each.
4. Principles (D65 / 29.4) in Blender practice: squash/stretch, anticipation, staging, straight-ahead vs pose-to-pose (Blender = pose-to-pose; straight-ahead for chaos), follow-through/overlap, slow-in/out, arcs, secondary, timing, exaggeration, solid drawing (volume), appeal. Plus modern: camera-relative silhouette, holds as acting.
5. Graph Editor is the instrument (29.2): handles, easing, channel cleanup, no noisy keys.
6. Timing/spacing tables at 24 fps (29.3).
7. Locomotion (D66): contact, passing, weight shift. Human (D67), animal (D68), invented (D69) from spec mass and COM.
8. Quadruped (D70), multi-leg (D71 tripod/phase), flying (D72 — 90% illusion), swimming (D73 undulation/drag).
9. Fighting (D74): telegraph, impact freeze, reaction sells the hit.
10. Acting (D75/D76): intent first; eyes lead; head leads body; weight/force readable; stillness is a weapon (horror).
11. Facial (D61): eyes/brows first, then mouth. Micro-motion. Lip sync (D62): visemes on phoneme timing, not word timing. Audio is king.
12. Secondary (D77): hand-keyed overlap for character; sim for cloth/hair after body lock.
13. Polish (D78 / 29.9): arcs, spacing, contacts, offsets. Then STOP (5.10).
14. Camera-relative: if it doesn't read in the shot camera at small size, it fails.
15. NLA/actions for cycles and reuse (29.8).
16. Shot sign-off (`checklists/animation-shot-signoff.md`).

## Procedures

### Blocking → spline → polish
Blocking: stepped, full poses, holds, contacts. Spline: interpolation, overlap offsets. Polish: tiny offsets, breathing, eye darts, cloth request.

### Multi-leg gait → Tripod → Phase
Never animate 6 legs as 3 pairs of bipeds. Stability tripod; phase diagram; gait driver if rigged.

### Lip sync → Phoneme → Viseme → Mouth shape
X-sheet or Dope Sheet against waveform. Closed forms on stops (B/P/M). Jaw + lips + tongue (if rigged). Don't over-enunciate.

### Invented motion
Mass vs speed vs limb count from spec. If gait wouldn't support mass, send back to design — do not "animate around it."

## Decision Logic

- Mocap vs hand-key: 5.14. Creatures: hand-key from animal ref.
- Stylized: exaggeration on top of real logic, not instead of it.
- Secondary: fake/drivers first; sim later.

## Inputs

- Signed-off rig, animatic timing, motion ref, shot camera, audio for dialogue, creature spec if any

## Outputs

- Shot animation (actions/NLA)
- Facial/lip-sync if implied
- Secondary notes / sim requests
- Sign-off
- Shared state: shot status blocked→splined→animated; `locks.animation` per shot

## Tools

Dope Sheet, Graph Editor, NLA, Pose library, onion/motion path, video empty for ref. Depth 29 tables.

## Constraints

Don't polish during blocking. Don't animate without the shot camera. Don't start cloth sim mid-body-change.

## Edge Cases

- Flight: body pitch, glide, wing speed sell weight; takeoff/land need anticipation.
- Horror: holds, then 2-frame impact; negative space.
- Transformation sequence: timing to music; many visibility switches; VFX owns the spectacle.

## Failure Modes & Fixes

| FAIL | FIX |
|---|---|
| Floaty | Contacts, weight shift, slower settle |
| Twinned / robotic | Offset pairs; overlap |
| Mouth flaps | Viseme chart; hold closed forms |
| Unreadable | Stage to camera; silhouette |
| Multi-leg spaghetti | Phase diagram; fewer keys; gait driver |
| Infinite polish | 5.10 lock |

## Dependencies

- NEEDS `rigging` sign-off
- Consumes preproduction timing and cinematography camera
- DRIVES simulation/costume secondary
- ⇄ rigging feedback

## Related Skills

rigging, cinematography, costume-groom, simulation, preproduction, production-finishing (sound)

## Delegation Rules

- Missing control / pop → `rigging`
- Topology collapse on squat → `modeling` via rigging feedback
- Hero cloak sim → `costume-groom` after lock
- Shot size/angle changes → `cinematography` (don't animate to a camera that will move)

## Examples

- Walk 24 fps: contact 0/12, passing 6/18, hip sway, shoulder counter, foot roll used.
- Six-legged walk: tripod A (1-3-5) / tripod B (2-4-6); body bob from mass; cloak sim after.

## Required Knowledge / Context

- `knowledge/domains/ch08-animation.md`
- `knowledge/domains/ch07-facial.md` (D61–D62)
- `knowledge/depth/ch29-animation-depth.md`

## References to Shared Resources

- `checklists/animation-shot-signoff.md`
- `workflows/character-pipeline.md`
- `workflows/creature-pipeline.md`
