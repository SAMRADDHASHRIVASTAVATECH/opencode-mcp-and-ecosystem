---
name: environment
description: Environment production, terrain, architecture, nature, set dressing and environmental storytelling, props libraries, Geometry Nodes, and procedural systems — worlds as characters.
system: BAKG
version: 2.0.0
status: production
group: world
domains: [D79, D80, D81, D82, D83, D84, D85, D86]
knowledge:
  - knowledge/domains/ch09-environment.md
  - knowledge/depth/ch27-worldbuilding.md
  - knowledge/depth/ch37-environment-terrain.md
---

# environment

## Purpose

Build worlds that set mood, tell history, and frame the action. Hero vs background split is the performance save. Every world-bible layer must produce a visual consequence.

## Scope

D79–D86, Depth 27, Depth 37. World *rules* originate in `preproduction` (D02). Lighting the world is `lighting`. Weather sims may delegate to `simulation`.

## Activation Conditions

- Environment, terrain, city, vegetation scatter, modular kits, set dressing, Geometry Nodes, procedural generators
- `Use environment`

## Non-Activation Conditions

- World bible text only (→ preproduction)
- Hero character modeling (→ modeling)
- Volume fog look (→ lighting) though this skill may place practical emitters

## Instructions

1. Pipeline order (37.1): blockout volumes → terrain → architecture kit → nature scatter → set dressing → lighting integration → hero/background split.
2. Terrain (D80/37.2): sculpt, ANT Landscape, heightmaps, displacement. Keep hero ground clean for contacts.
3. Architecture (D81/37.4): modular kits, repeating modules, trim sheets, vertex color wear.
4. Nature (D82/37.3): GN scatter with density, slope, collision, LOD. Sapling for trees as a start.
5. Set dressing (D83/27.2): ten environmental-storytelling techniques — show don't tell. Case study: rainy fantasy city (27.3).
6. Props & assets (D84): Asset Browser, reuse, LOD. Don't unique-model every cup.
7. Geometry Nodes (D85): fields, attributes, instances. Simulation zones (4.x) for stateful setups. Instancing is the default for repetition.
8. Procedural systems (D86): parameterized node groups; expose only what dressers need.
9. Water (37.5): Ocean modifier for oceans; shader ripples for puddles; hero splash only if needed.
10. Performance (37.7): hero/background split, instances, LODs, proxies.
11. Palette systems (27.4 / D138) and weather/TOD world systems (27.5) — coordinate with lighting.

## Procedures

### World-layer system (27.1)
Each layer (climate, culture, tech, history, magic) → visual consequences in materials, dress, wear, signage, vegetation.

### GN scatter
Distribute points → density by vertex group/slope/noise → instance collection → realize only when needed → LOD by camera distance.

### Hero/background
Hero: unique, contact-accurate, sim-ready. Background: instances, cards, lower texel density.

## Decision Logic

- Modular + procedural for cities/backgrounds (5.3).
- Fake distant motion (5.6).
- Scale map: world → set → shot (27.6). Don't load the city when the shot is a doorway.

## Inputs

- World bible, shot cameras, scale master, style, budgets

## Outputs

- Environment scene(s) with collections
- Terrain / kits / scatter systems
- Dressing that serves beats
- LOD/proxy policy
- Shared state: env ready for lighting

## Tools

GN, ANT Landscape, Sapling, Asset Browser, Ocean modifier, geometry nodes instancing. Depth 27/37.

## Constraints

Don't scatter millions without instancing. Don't put hero collision on high-poly trees. Don't contradict world bible palette.

## Edge Cases

- Flooded city (Example D): water plane + wet materials + debris dressing; hero splash optional.
- Abstract: GN + sims may *be* the environment.

## Failure Modes & Fixes

| FAIL | FIX |
|---|---|
| Viewport death | Split hero/BG; instances; hide scatter |
| Floating dressing | Snap; collision; scale |
| Generic set | Apply 27.2 techniques to the beat |
| Repetition obvious | Noise density; kit variation; trim |

## Dependencies

- Consumes preproduction bible and blender-foundations scale
- Needs modeling/lookdev for hero pieces
- Drives lighting and cinematography staging
- May delegate weather to simulation

## Related Skills

preproduction, modeling, lookdev, lighting, cinematography, simulation, production-finishing

## Delegation Rules

- Rain particles / wetness maps → simulation + lookdev
- Mood recipes → lighting
- Shot framing that requires set rebuild → cinematography feedback

## Examples

- Rainy fantasy city: modular timber/stone kit, wet albedo, puddle planes, GN market scatter, warm window emission, hero street only in shot file.

## Required Knowledge / Context

- `knowledge/domains/ch09-environment.md`
- `knowledge/depth/ch27-worldbuilding.md`
- `knowledge/depth/ch37-environment-terrain.md`

## References to Shared Resources

- `examples/A-crystal-creature-rainy-city.md`
- `templates/world-bible.md`
