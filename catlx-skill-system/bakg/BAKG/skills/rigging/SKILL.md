---
name: rigging
description: Skeleton design, IK/FK, constraints, drivers, controllers, weight painting, skinning, deformation, correctives, facial rigs, eye systems, advanced subsystems (foot roll, hands, wings, tails, multi-leg, space switching), auto-rig, and mocap retarget.
system: BAKG
version: 2.0.0
status: production
group: puppet
domains: [D48, D49, D50, D51, D52, D53, D54, D55, D56, D57, D58, D59, D60, D63, D131]
knowledge:
  - knowledge/domains/ch06-rigging.md
  - knowledge/domains/ch07-facial.md
  - knowledge/depth/ch19-shapekeys-drivers.md
  - knowledge/depth/ch20-autorign-mocap.md
  - knowledge/depth/ch28-advanced-rigging.md
---

# rigging

## Purpose

Turn a model into a puppet the animator can perform with: one control = one job, deformation that holds volume, a facial system when the character acts, and a sign-off test before any animation.

## Scope

D48–D60, D63, D131, Depth 19/20/28. Facial *animation* and lip sync timing are `animation` (D61/D62) but this skill builds the face machine.

## Activation Conditions

- Rig, armature, IK, FK, weights, skinning, drivers, shape keys, facial rig, eye aim, mocap retarget, foot roll, space switch
- Feedback from animation: controls unusable
- `Use rigging`

## Non-Activation Conditions

- Topology still failing bend tests (→ modeling first)
- Acting/performance (→ animation)
- Soft-body jiggle as physics (→ simulation) unless a jiggle *rig* (28.10)

## Instructions

1. Do not rig a non-final mesh for final animation (economy rule 5). Test-rig at blockout is OK.
2. Pick rig type (decision 5.4) and facial method (5.12).
3. Build order (5.19 / Ch 6):
   1. Skeleton placement & roll (D49). Bone Collections (4.x). Consistent orientations. Avoid gimbal traps.
   2. Deform bones vs control bones vs mechanical (D50). BBones for spines/tails.
   3. IK limbs with pole targets (D51); FK for arcs (D52); IK/FK switch without pops.
   4. Spine/torso (28.3), shoulders/clavicles (28.4), foot roll (28.1), hands (28.2).
   5. Constraints (D53): Copy, Limit, Damped Track, Child Of, Armature, Stretch To, Floor.
   6. Drivers (D54) where automation earns its keep (Ch 19 recipes) — not for everything.
   7. Controllers with custom shapes (D55). Readable in silhouette.
   8. Bind (D57) + weight paint (D56). Auto weights as start, not finish.
   9. Deformation tests (D58). Volume loss → correctives (D59) or topology feedback.
   10. Facial (D60): jaw, brows, eyes, lips. Shape-key library (19.2, 60+ keys) for realistic; bones for stylized; mixed for creatures.
   11. Eye systems (D63): gaze aim, eyelids follow, pupils, blink. Eyes precede head.
   12. Specials: mechanical (28.6), wings (28.7), tail/tentacle (28.8), multi-leg gait (28.9), jiggle/squash (28.10), space switching (28.11).
4. Mocap (D131 / Ch 20): acquire → cleanup → retarget to this rig; still hand-key face/hands/eyes for hero (5.14).
5. Run `templates/rig-signoff.md`. Animator must pose an acting beat without fighting the rig.
6. Separate rig file from shot files (D123). Link + overrides.

## Procedures

### IK → Leg IK → Foot IK → Foot Controller
Pivot, orientation, rotation limits, pole vector, heel roll, ball, toe, bank.

### Facial rig → Control map → Expression
Controls drive keys or bones. Phoneme set must exist before lip sync animation.

### Eye system → Gaze → Hierarchy
Aim bone at target; eyelids; saccades are animated later; pupil dilation shape key or scale.

### Space switching
Grab/drop props: world space ↔ hand space via Child Of influence or space-switch custom property. See 28.11.

## Decision Logic

- Rig only what the animation needs. Background: 3–5 face keys.
- If deformation fails: topology first (`modeling`), weights second, correctives third.
- Rigify/Auto-Rig Pro are accelerators after you understand the graph (D134 rule).

## Inputs

- Deformation-ready mesh, joint ranges (Ch 16), sheet (expression range), locomotion class, whether dialogue, prop interactions

## Outputs

- Control rig + deform rig
- Weight groups
- Facial system
- Sign-off report
- Shared state: `locks.rig`

## Tools

Armature, Pose Mode, constraints, drivers, shape keys, Rigify (built-in), optional Auto-Rig Pro. Ch 19 driver language. Ch 28 node cards.

## Constraints

Never animate on a moving rig target. Never leave deform bones as the animator interface. Never skip pole targets on IK legs. Bone Collections replaced bone groups in 4.x.

## Edge Cases

- 6-legged crystal creature: per-leg IK + gait driver; no Hollywood face unless it acts.
- Mech: no soft deform; pistons and limit rot.
- Stretchy cartoon: Stretch To + squash root; topology must support it.

## Failure Modes & Fixes

| FAIL | FIX |
|---|---|
| IK pop on switch | Match poses; use blending; or snap operators |
| Candy wrapper | Loops (modeling) then weight |
| Gimbal | Change rotation order / use quaternion on that control |
| Unusable controls | Rebuild UX; one job per control |
| Face breaks at phonemes | Missing keys; add viseme set |
| Mocap sliding feet | Foot lock / cleanup (Ch 20) |

## Dependencies

- NEEDS topology (`modeling`)
- Consumes anatomy ranges (`sculpting-anatomy`)
- DRIVES `animation`
- ⇄ animation feedback
- Facial keys Depth 19; mocap Depth 20

## Related Skills

modeling, animation, costume-groom, sculpting-anatomy, decision-engine

## Delegation Rules

- Topology fix → `modeling` (do not hide with weights)
- Performance → `animation`
- Cloth/hair bind meshes → `costume-groom`
- Driver recipes beyond 12 → read Ch 19; don't invent fragile Python drivers when a constraint works

## Examples

- Biped hero: IK/FK arms/legs, foot roll, 3-bone BBone spine, clavicles, 60-key face, eye aim, sign-off squat+reach+dialogue.
- Dragon: wing fold + IK tip, tail BBone, 4-leg IK, no lips visemes if it doesn't speak.

## Required Knowledge / Context

- `knowledge/domains/ch06-rigging.md`
- `knowledge/domains/ch07-facial.md`
- `knowledge/depth/ch19-shapekeys-drivers.md`
- `knowledge/depth/ch20-autorign-mocap.md`
- `knowledge/depth/ch28-advanced-rigging.md`

## References to Shared Resources

- `templates/rig-signoff.md`
- `decision-engine` 5.4 5.12 5.14 5.19
