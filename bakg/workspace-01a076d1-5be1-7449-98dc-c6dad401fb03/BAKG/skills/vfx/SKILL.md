---
name: vfx
description: Effects design — layered method for impacts, magic, energy, particles-as-theatre — making the beat readable, then integrating in comp.
system: BAKG
version: 2.0.0
status: production
group: effects
domains: [D100, D101]
knowledge:
  - knowledge/domains/ch11-vfx.md
  - knowledge/depth/ch35-vfx-depth.md
---

# vfx

## Purpose

Visual effects are the theater of a film: the impact frame, the spell, the transformation. Design in layers that serve a beat, not one giant sim.

## Scope

D100 VFX [SIT], D101 Magic/Energy [SIT], Depth 35. Physics solvers live in `simulation`; this skill designs the stack and the read.

## Activation Conditions

- Magic, energy, impacts, explosions as design, auras, trails, transformation spectacle
- `Use vfx`

## Non-Activation Conditions

- Pure cloth/hair/fire sim without an effects beat (→ simulation)
- Color glow only in grade (→ render-comp) unless it's the effect

## Instructions

1. Layered-effect method (35.1): every effect = source + body + interaction + residue + audio cue. Each layer is a separate element.
2. Time the effect to the beat. Impact frame is a hold (D74/D65).
3. Particles/GN recipes (35.2) for sparks, motes, trails.
4. Fire/smoke as a *layer* — tune via 35.3 or fake if stylized (5.6).
5. Magic systems (35.4 / D101): rules from world bible (limits!). Glows, trails, arcs, runes, auras. Fresnel edges, emission, mesh lights, GP overlays.
6. Impact & destruction (35.5): pre-break, hit frame, debris, dust, shock decal, camera shake (motivated).
7. Compositing integration (35.6): additive glows, cryptomatte, holdouts, grain match. Effects die if they don't sit in the plate.
8. Stylized transformation (Example E): many short layers on music hits, not one 200-frame sim.

## Procedures

### VFX → Effect → Layers → Beat
If a layer doesn't change the beat's read, cut it.

### Magic with rules
World bible sets fuel/cost/limit. Visual grammar consistent (color, direction, who can cast).

## Decision Logic

Fake first. Cycles if refraction/volume magic; EEVEE if additive toon glows. Outline/GP for 2D-hybrid hits.

## Inputs

- Beat, camera, style, world magic rules, animation hit frames, optional sim caches

## Outputs

- Layer list (what, when, how)
- Scene collections for fx
- Comp notes (add, screen, glow size)
- Shared state: fx designed per beat

## Tools

GN particles, emissive meshes, lights, GP, Mantaflow (via simulation), compositor. Depth 35.

## Constraints

Don't violate world magic limits. Don't bury the character. Don't skip integration tests.

## Edge Cases

- Invisible/shadow creature (Example F): VFX is *absence* + silhouette; restraint.
- Crystal creature: refractive shards as hit residue.

## Failure Modes & Fixes

| FAIL | FIX |
|---|---|
| Unreadable soup | Fewer layers; contrast; hold on impact |
| Doesn't sit in shot | Match grain/MB/color; light wrap |
| Magic with no rules | Return to world bible |
| Sim-only thinking | Redesign as layers |

## Dependencies

- May consume simulation caches
- Needs cinematography timing and lighting continuity
- NEEDS render-comp for integration
- Constrained by D02 / D138

## Related Skills

simulation, render-comp, lighting, animation, grease-pencil, environment

## Delegation Rules

- Solver setup → `simulation`
- Glow/grade → `render-comp`
- 2D overlay strokes → `grease-pencil`
- If "is this a sim?" → decision 5.6

## Examples

- Spell cast: hand rune (emission mesh) + arc bolt (GN) + hit flash (1–2 frames) + residue scorch (decal) + whoosh (sound).
- Magical-girl transform: 8 layers on 8 music hits; vis swaps; additive twinkles; toon comp.

## Required Knowledge / Context

- `knowledge/domains/ch11-vfx.md`
- `knowledge/depth/ch35-vfx-depth.md`

## References to Shared Resources

- `examples/E-anime-magical-girl.md`
- `workflows/shot-pipeline.md`
