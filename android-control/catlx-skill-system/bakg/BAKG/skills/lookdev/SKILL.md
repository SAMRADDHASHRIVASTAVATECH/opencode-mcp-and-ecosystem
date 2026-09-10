---
name: lookdev
description: UV mapping, texture creation/painting/baking/procedural, Principled materials, shaders, organic lookdev (skin/eyes/teeth/tongue/claws), and stylized/NPR shading systems.
system: BAKG
version: 2.0.0
status: production
group: shading
domains: [D25, D26, D27, D28, D29, D30, D31, D32, D33, D34, D35, D36]
knowledge:
  - knowledge/domains/ch04-lookdev.md
  - knowledge/depth/ch17-materials-encyclopedia.md
  - knowledge/depth/ch18-stylized-npr.md
  - knowledge/depth/ch32-uv-texture-baking.md
---

# lookdev

## Purpose

Make surfaces true: UVs that don't stretch, maps that carry micro-story, materials that respond to light, organic features that read as alive, or NPR systems that match the style lock. Materials are ~80% of why a model looks real or cheap.

## Scope

D25–D36 plus Depth 17 (120+ Principled recipes), Depth 18 (cel/anime/outlines/painterly), Depth 32 (UV strategy, texel density, UDIMs, baking pipeline). Lighting is `lighting`. Engine choice is `decision-engine` 5.2.

## Activation Conditions

- UV, seams, texel density, UDIM, painting, baking, Principled, SSS, eyes, toon/cel/anime shaders, material recipes
- `Use lookdev`

## Non-Activation Conditions

- Mesh still failing bend tests (→ modeling)
- Final grade/LUT (→ render-comp)
- Cloth/hair fibers (→ costume-groom) except strand materials which this skill can support

## Instructions

1. UV (D25): seams in hidden regions (inner thighs, hairline, under arms). Even texel density (Ch 32.3 table). Pack islands. UDIM for heroes if needed. No lighting in albedo.
2. Maps: albedo, roughness (the #1 realism lever), metalness (0 or 1, not 0.5), normal, optional height/displacement, masks (AO, curvature, ID).
3. Creation path: paint (D27), photo/projection (D32.8), procedural (D29), bake high→low (D28 / D32.7). Combine.
4. Principled BSDF is the universal base (unless NPR). Use Depth 17 recipes for metals, organics, liquids, stone/gems, wood, fabrics, plastics/glass, emissives. Ten node recipes in 17.10.
5. Skin (D32): SSS (radius reddish), pore-scale, roughness 0.3–0.5 varied, never plastic. Cheeks/ears/knuckles more red.
6. Eyes (D33): sclera + iris disc + cornea (IOR ~1.37), wet gloss, catchlights. Life lives here.
7. Teeth/tongue/nails: slight transmission, not bathroom-white teeth, wet tongue.
8. NPR: if style lock is toon/anime/cartoon/painterly, use Depth 18 and decisions 5.13 / 5.17. Comp for toon is mandatory (18.7).
9. Approve hero close-up under FINAL lighting, not HDRI studio only.
10. Lookdev lock.

## Procedures

### Baking pipeline (32.7)
Cage or extrusion ray; selected-to-active; bake Normal, AO, Curvature, Thickness; 16-bit or EXR; match texel density.

### Anime shading (18.3)
2–3 tone ramp via Shader-to-RGB, anime eye, face-shadow trick, selective outline. EEVEE often. Grade with stylized grading (Ch 36.6).

### Crystal/gem (for Example A)
Depth 17.5: transmission, IOR, roughness low, volume absorption if needed, Cycles preferred.

## Decision Logic

- Style lock drives PBR vs NPR.
- Keep materials PBR-pure if engine might swap.
- Background assets: procedural + shared materials; don't unique-paint everything.

## Inputs

- Deformation-ready mesh, style lock, engine, lighting preview, material callouts from sheets

## Outputs

- UV layout + texel policy
- Map set
- Material/shader graphs (or NPR system)
- Lookdev stills under final-ish light
- Shared state: `locks.lookdev`

## Tools

UV Editor, Texture Paint, Shader Editor, bake, Depth 17–18–32 tables. Optional Substance only if it genuinely helps; Blender-centered.

## Constraints

Never final-to-compressed-video from lookdev. Never bake lighting into albedo. Never skip seam hiding on heroes.

## Edge Cases

- Mixed toon character in PBR world: separate ramps, grade together.
- Wetness from rain: mask/AOV, not a new material per shot.
- Skin in EEVEE: approximate SSS; know the limit.

## Failure Modes & Fixes

| FAIL | FIX |
|---|---|
| Stretching | Recut seams; relax; check density |
| Plastic skin | SSS + roughness variation + pore |
| Dead eyes | Cornea IOR + wet + iris recess + catchlight |
| Seams obvious | Move to hidden; paint across |
| Toon looks 3D | Ramp + outline + lighting discipline + comp (18.7/18.8) |
| Fireflies on metal | Roughness > 0; clamp; Cycles settings via render-comp |

## Dependencies

- Needs `modeling` UVs on a stable mesh
- Constrained by `character-design` callouts and D138
- Affects `lighting` and `render-comp`
- NPR outline methods may use `grease-pencil`

## Related Skills

modeling, lighting, render-comp, costume-groom, character-design, decision-engine

## Delegation Rules

- Engine/samples → `render-comp` / decision 5.2
- Mood light → `lighting` (lookdev must still preview under it)
- Hair strand shader details also in `costume-groom` Depth 33.3 — coordinate

## Examples

- Realistic face: UDIM head, 4k albedo/rough/normal, Principled SSS, cornea IOR 1.37.
- Anime girl: Shader-to-RGB 3-tone, face shadow mesh or gradient, inverted-hull outline, EEVEE.

## Required Knowledge / Context

- `knowledge/domains/ch04-lookdev.md`
- `knowledge/depth/ch17-materials-encyclopedia.md`
- `knowledge/depth/ch18-stylized-npr.md`
- `knowledge/depth/ch32-uv-texture-baking.md`

## References to Shared Resources

- `checklists/lookdev-handoff.md`
- `workflows/lookdev-pipeline.md`
