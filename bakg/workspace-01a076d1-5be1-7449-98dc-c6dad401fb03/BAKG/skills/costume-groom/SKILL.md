---
name: costume-groom
description: Clothing design and 3D tailoring, cloth sim, accessories, armor, props-as-worn, curves hair, GN fur, feathers, grooming, and strand dynamics.
system: BAKG
version: 2.0.0
status: production
group: groom
domains: [D37, D38, D39, D40, D41, D42, D43, D44, D45, D46, D47]
knowledge:
  - knowledge/domains/ch05-costume-groom.md
  - knowledge/depth/ch33-hair-fur-feathers.md
  - knowledge/depth/ch34-cloth-costume.md
---

# costume-groom

## Purpose

Turn a character into a person and a creature into a being: garments that read era/culture/climate, grooms that read species, armor that can move, props that can be held. Design must respect sim cost.

## Scope

D37–D47, Depth 33, Depth 34. Generic environment props also exist in `environment` (D84); held/worn props live here. Cloth *physics infrastructure* is shared with `simulation` (D88/D91) — this skill owns garment intent and hero cloth.

## Activation Conditions

- Clothes, cloak, armor, hair, fur, feathers, groom, belts, jewelry, held props
- `Use costume-groom`

## Non-Activation Conditions

- Body mesh not locked (→ modeling)
- World scatter props (→ environment)
- Generic rigid-body debris (→ simulation)
- Final lighting of fabrics (→ lookdev materials + lighting)

## Instructions

1. Design garments with fabric weight in mind (D37). A flowing cloak is a sim budget; a tactical vest is not.
2. Construct for sim (D38): pattern pieces or body-offset meshes; even-ish quads; sewing springs if patterned; pinning at locked areas (waist, shoulders).
3. Cloth sim (D39): collision proxies (low-poly), quality, shrinkage, bending, damping. Bake to disk. Hero only — fake distant cloth (5.6).
4. Accessories (D40): separate objects, hook/constraint to bones, not merged.
5. Armor (D41): rigid plates on a flexible underlayer; weight to bones or constraint; avoid cloth-sim metal.
6. Props (D42): handle empty/bone at the grip; Child Of or parent; space switching (28.11) for grab/drop. Scale vs hand. Asset catalog.
7. Hair (D43): curves hair (4.x standard). Guides → interpolate → groom brushes (33.2) → strand material (33.3).
8. Fur (D44): GN fur or curves + noise; density budget (33.8). Alpha cards for realtime/background.
9. Feathers (D45): construction + instancing; wing hierarchy with rig.
10. Dynamics (D47): after animation lock. Fake sway with drivers if possible.
11. Approve groom **in motion**, not T-pose.

## Procedures

### Fabric behavior library
Use Depth 34.3: silk vs wool vs leather vs denim → mass, bending, damping, friction.

### Hair curves workflow (33.1)
Add hair curves → generate on scalp vertex group → grow → comb/clump/frizz → children → EEVEE/Cycles hair BSDF (melanin, roughness).

### Armor on soft
Hard plates bone-parented; cloth or deforming suit underneath; collision between them; don't sim the plate.

## Decision Logic

- Decision 5.5 for hair/fur/feathers system.
- Decision 5.6 for sim vs fake.
- Background characters: cards, not 100k strands.

## Inputs

- Locked character mesh, style, climate (world bible), animation (for dynamics), poly/sim budgets

## Outputs

- Garment meshes + pin groups
- Armor/accessory objects with handles
- Groom (curves/GN)
- Sim caches if hero cloth/hair
- Shared state: costume/groom approved in motion

## Tools

Cloth modifier, Collision, curves sculpt brushes, Geometry Nodes, particle instances, Child Of. Depth 33–34. Built-in over add-on.

## Constraints

Simulate last. Never merge props into the character mesh. Never skip collision proxies. Document caches per shot+version.

## Edge Cases

- Crystal creature cloak (Example A): sim the hero cloak only; wetness from lookdev mask; no fur.
- Magical-girl transformation: costume *change* is VFX layers + maybe multiple garment visibilities, not one sim.

## Failure Modes & Fixes

| FAIL | FIX |
|---|---|
| Jellyfish cloth | Construction density + bending + pinning |
| Exploding sim | Scale meters; collision margin; quality |
| Hands float on props | Add handle; constraint |
| Bald spots / popping hair | Guides, density, collision, children |
| Viewport death | Budget table 33.8; viewport children down |

## Dependencies

- Needs modeling + lookdev materials
- Needs rigging for weights/constraints
- Delegates dynamics infrastructure to `simulation`
- After `animation` for final dyn
- Feeds render cost

## Related Skills

modeling, lookdev, rigging, animation, simulation, vfx, environment

## Delegation Rules

- Force fields, gravity, cache policy → `simulation`
- Strand/fabric Principled values → `lookdev` Ch 17.7
- Wing bone setup → `rigging` Ch 28.7
- Distant flags → fake; don't open a sim here

## Examples

- Hero wool cloak: patterned construction, pin at clasps, collision proxy body, bake disk.
- Mammal: GN fur layers, short density, no dynamics on BG plates.

## Required Knowledge / Context

- `knowledge/domains/ch05-costume-groom.md`
- `knowledge/depth/ch33-hair-fur-feathers.md`
- `knowledge/depth/ch34-cloth-costume.md`
- S-10 props supplement

## References to Shared Resources

- `workflows/sim-last.md`
- `decision-engine` 5.5 5.6
