# Router — What Capability Do I Need?

The orchestrator (and any skill that is unsure) uses this router.

## 1. Classify the request

| Signal in the request | Capability | Skill |
|---|---|---|
| "I have an idea", full film, "what do I need", arbitrary creature/world combo | Navigation | bakg-orchestrator |
| "which should I pick", style/engine/rig/sim-vs-fake | Choice | decision-engine |
| story, script, beat, world bible, board, animatic, previs, motion ref | Pre-production | preproduction |
| silhouette, character design, creature spec, turnaround, AI concept, style guide | Design | character-design |
| how Blender works, scale, collections, naming, blockout | Foundations | blender-foundations |
| model, box model, boolean, retopo, topology, edge flow | Modeling | modeling |
| sculpt, anatomy, proportions, dyntopo, multires | Sculpt/anatomy | sculpting-anatomy |
| UV, texture, bake, Principled, SSS, skin, eyes, toon/cel/anime shader | Lookdev | lookdev |
| cloth, garment, armor, accessory, hair, fur, feather, groom | Costume/groom | costume-groom |
| rig, IK, FK, weights, skinning, corrective, facial rig, mocap | Rigging | rigging |
| animate, walk cycle, acting, lip sync, polish, 12 principles, gait | Animation | animation |
| environment, terrain, city, scatter, geometry nodes, set dressing | Environment | environment |
| rigid body, cloth sim, fluid, smoke, fire, fracture, rain | Simulation | simulation |
| magic, impact, energy, layered effect | VFX | vfx |
| camera, lens, shot size, composition, 180 rule, match move | Cinematography | cinematography |
| light, HDRI, key/fill/rim, fog, volume, mood | Lighting | lighting |
| samples, denoise, Cycles/EEVEE, EXR, compositor, grade | Render/comp | render-comp |
| edit, sound, QC, deliver, archive, folders, python, USD, farm, LOD, EEVEE game | Production | production-finishing |
| grease pencil, 2D animation, hybrid 2D-3D | Grease Pencil | grease-pencil |

## 2. Multi-signal requests

If two or more rows fire, enter whole-system mode. Build the ordered skill list from Part 3 edges (see `orchestration/dependency-order.md`).

## 3. Never-all rule

A 10-second social loop does not need storyboarding, worldbuilding, or lip sync. A landscape film does not need facial rigs. Consult `workflows/project-types.md` before adding [SIT] skills.

## 4. Questions the router must be able to answer

- What capability do I need?
- Which skill provides it?
- What does that skill depend on?
- What context does it need?
- What knowledge does it need?
- Can it delegate to another skill?
- What can consume its output?
- How does it participate in the larger system?

Answers live in `registry/skills.yaml`, `registry/capability-index.md`, `dependencies/skill-graph.yaml`, and each skill's SKILL.md.
