---
name: simulation
description: Physics infrastructure, particles, rigid/soft bodies, cloth and hair physics, Mantaflow fluids/smoke/fire, destruction, debris, and environmental weather — with fake-first and simulate-last discipline.
system: BAKG
version: 2.0.0
status: production
group: sim
domains: [D87, D88, D89, D90, D91, D92, D93, D94, D95, D96, D97, D98, D99]
knowledge:
  - knowledge/domains/ch10-simulation.md
  - knowledge/system/02d-depth-supplements.md
  - knowledge/depth/ch35-vfx-depth.md
---

# simulation

## Purpose

Add the natural world: falling, flowing, burning, tearing, weather — only when faking is harder or visibly worse. Sims are powerful, expensive, and cache-disciplined.

## Scope

D87–D99, S-11 physics infrastructure, S-12 soft bodies, fire/smoke tables in Depth 35. Hero garment construction stays in `costume-groom`; this skill owns shared physics and non-costume sims. Effect *design* is `vfx`.

## Activation Conditions

- Rigid body, soft body, cloth physics, hair physics, fluid, ocean, smoke, fire, fracture, debris, rain, force fields, caches
- `Use simulation`

## Non-Activation Conditions

- Animation body performance (→ animation) — required *before* most sims
- Magic design / layered impact recipe (→ vfx)
- Fake rain/flags (decision 5.6) — do not open a sim

## Instructions

1. Fake first (5.6 / 5.18). Distant flags, puddles, rain, dust motes: particles/shaders/drivers.
2. Simulate last: final-ish meshes + final animation.
3. Infrastructure (D88 / S-11): gravity, force fields catalog (Force, Wind, Turbulence, Vortex, Magnetic, Harmonic, Curve guide), collision, caching, **scale in meters**.
4. Collision proxies (low-poly) are standard.
5. Bake to disk in `cache/`, named per shot+version. Never rely on memory cache for production.
6. Rigid (D89): animated vs dynamic; passive colliders; apply scale.
7. Soft (D90 / S-12): goal vertex group; not for fabric (use cloth); low-poly sim + subdiv display.
8. Cloth (D91) / hair (D92): coordinate with costume-groom.
9. Fluids (D93) / water (D94): Mantaflow for hero splash/pour; Ocean modifier for seas; ripple shader for puddles.
10. Smoke (D95) / fire (D96): Mantaflow gas; tuning table in Depth 35.3. Domain size = cost.
11. Destruction (D97): Cell Fracture + rigid; debris (D98) as secondary chunks + dust particles.
12. Environmental (D99): weather, leaves, ambient — prefer particles/GN.
13. Checklist: scale → gravity → colliders → force fields → quality → bake → verify.

## Procedures

### Production rules (chapter in 8 lines)
1. Scale meters. 2. Fake first. 3. Proxies. 4. Bake disk. 5. One sim owner per shot. 6. Domain as small as possible. 7. Cache versioned. 8. QC a playblast before render.

### Fire/smoke
Fuel vs smoke density, temperature, vorticity, dissolve, noise. Render via Principled Volume. Small domain, high res only on hero.

## Decision Logic

If the audience cannot tell it was faked at shot size, fake it. Hero cloak, hero explosion, hero pour: sim.

## Inputs

- Locked animation, collision meshes, scale master, shot camera (frustum culls domain), style (stylized fire often fake)

## Outputs

- Caches on disk
- Collision collections
- Settings notes for archive
- Shared state: shot status sim'd; `locks.sim`

## Tools

Mantaflow, Rigid Body World, Cloth, Soft Body, Particles, GN simulation zones, Cell Fracture, force fields. S-11/S-12. Depth 35.

## Constraints

Wrong scale = exploding sims. Never sim full-res hero mesh. Never skip bake. Caustics/fire in glass = expensive; warn render-comp.

## Edge Cases

- Stylized fire breath: emissive curves + particles (vfx), not Mantaflow.
- Crystal magnetic creature: Magnetic force field (S-11) is a legal gag.

## Failure Modes & Fixes

| FAIL | FIX |
|---|---|
| Explode | Scale, margins, substeps, quality |
| Fall-through | Collision modifier / collection |
| Flicker between sessions | Bake disk |
| Domain too big | Crop to camera + padding |
| Soft body collapse | Add goal weights |

## Dependencies

- After animation
- Shared with costume-groom for cloth/hair
- Feeds vfx and render-comp
- Needs blender-foundations scale

## Related Skills

costume-groom, vfx, animation, environment, render-comp

## Delegation Rules

- Layered impact / magic look → `vfx` (sim may supply debris/smoke layers)
- Ocean look without sim → environment + lookdev
- If user asked "should I sim this?" → `decision-engine` 5.6

## Examples

- Hero splash: small Mantaflow domain, inflow at contact, foam particles, bake.
- Rainy city: particle rain + wetness, not fluid.

## Required Knowledge / Context

- `knowledge/domains/ch10-simulation.md`
- `knowledge/system/02d-depth-supplements.md` (S-11 S-12)
- `knowledge/depth/ch35-vfx-depth.md` (tuning tables)

## References to Shared Resources

- `workflows/sim-last.md`
- `decision-engine` 5.6 5.18
