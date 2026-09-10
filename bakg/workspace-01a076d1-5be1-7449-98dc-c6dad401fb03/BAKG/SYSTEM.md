# BAKG System Architecture

BAKG (Blender Animation Knowledge Graph) is a **complete, standalone, interconnected skill ecosystem**. It is not one skill, not a loose collection of skills, and not a simple document conversion. It is the operational form of *The Ultimate Blender Animation Knowledge Graph* v2.0 (Blender 4.x era).

## Identity

See `context/identity.md`. Portable. No dependency on any other skill system. Relative references only.

## Two modes

See `orchestration/modes.md`.

1. **Individual skill mode** — `Use <skill-name>`
2. **Whole-system mode** — orchestrator fires only the required skills

## Layer cake

```
User Request
    ↓
orchestration/          router, Ultimate Test, delegation, modes, dependency order
    ↓
skills/                 19 operational skills (SKILL.md each)
    ↕
context/                conventions, economy rules, shared state, identity
    ↕
knowledge/              full domain + depth operational text (preserved from source)
    ↕
workflows/              34-stage journey, project types, character/creature/shot/lookdev/sim
    ↕
registry/               skills, domains D01–D138, capability index
    ↕
dependencies/           skill graph
    ↕
templates/ checklists/ examples/ metadata/
```

## Skills (19)

| Skill | Role |
|---|---|
| `bakg-orchestrator` | Whole-system router, Ultimate Test |
| `decision-engine` | Part 5 choice libraries |
| `preproduction` | Story, world, boards, animatic, previs, motion ref |
| `character-design` | Concept, design, creature spec, sheets, AI concept, style |
| `blender-foundations` | UI, scale, collections, blockout |
| `modeling` | Organic/hard-surface/character/creature, retopo, topology |
| `sculpting-anatomy` | Anatomy libraries, sculpting craft |
| `lookdev` | UV, textures, materials, NPR |
| `costume-groom` | Clothes, armor, hair, fur, feathers |
| `rigging` | Skeleton through facial rig and mocap |
| `animation` | Principles through polish, creature motion, lip sync |
| `environment` | Worlds, terrain, GN, dressing |
| `simulation` | Physics, fluids, fire, destruction, weather |
| `vfx` | Layered effects, magic, impacts |
| `cinematography` | Camera, composition, shot design, match move |
| `lighting` | Lights, shadows, atmosphere, mood recipes |
| `render-comp` | Engines, passes, comp, grade |
| `production-finishing` | Edit, sound, pipeline, QC, deliver, archive, python, realtime |
| `grease-pencil` | 2D and hybrid 2D-3D |

## Knowledge preservation

Source chapters are preserved in `knowledge/` (not summarized away). Skills operationalize them: activation, procedures, I/O, failure modes, delegation. If information is shared, it lives in `knowledge/` + `context/`. If it is a relationship, it lives in `orchestration/` + `dependencies/`.

## Graph

138 L1 domains, 34 stages, 25 depth chapters (16–40), 18 depth supplements (S-01…S-18), 19 decision trees, 6 worked Ultimate Test examples.

## Extension

Use `templates/node-card.md` and Appendix A.5. New domains D139+. Completeness over brevity is binding.

## Validation

```
python3 scripts/validate_system.py
```
