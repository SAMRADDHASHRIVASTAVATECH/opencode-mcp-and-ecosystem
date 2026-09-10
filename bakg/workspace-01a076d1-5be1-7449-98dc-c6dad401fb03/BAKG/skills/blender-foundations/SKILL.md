---
name: blender-foundations
description: Blender 4.x fundamentals, 3D planning (units, budgets, breakdowns), scene organization, and blockout — the load-bearing walls of every project.
system: BAKG
version: 2.0.0
status: production
group: foundation
domains: [D13, D14, D15, D16]
knowledge:
  - knowledge/domains/ch02-foundations.md
  - knowledge/system/02d-depth-supplements.md
  - knowledge/system/hotkeys.md
---

# blender-foundations

## Purpose

Make the project navigable, correctly scaled, budgeted, and blocked out before anyone spends time on detail. Weak fundamentals make every later domain 10× slower. Scale errors are the most expensive error class.

## Scope

D13 Fundamentals [REQ], D14 3D Planning [REQ], D15 Scene Organization [REQ], D16 Blockout [REQ]. Not modeling detail, not rendering settings (beyond committing engine/fps/resolution).

## Activation Conditions

- User is new to Blender, or asks about units, scale, collections, naming, linking, blockout, budgets, hotkeys
- Orchestrator fires planning/blockout
- `Use blender-foundations`

## Non-Activation Conditions

- Topology/modeling techniques (→ modeling)
- Render sample counts (→ render-comp)
- Final folder archive (→ production-finishing) — but this skill *starts* the tree

## Instructions

1. Fundamentals: data model (objects reference data-blocks; linked duplicates share meshes). Object vs Edit vs Pose vs Sculpt. Origins matter. Apply transforms (Ctrl-A) after modeling. GPU in Preferences.
2. Units: Metric, 1 unit = 1 m unless jewelry/world-scale split. Real-world sizes. Character ~1.7–1.8 m. Keep a SCALE MASTER (1 m cube + reference character) in every scene.
3. Large worlds: hero scene small; distant stuff in linked files/separate scenes.
4. Write budgets: poly (film hero 20k–200k; realtime 10k–100k), textures 2k/4k/8k per class, render time/frame, memory.
5. Shot/asset breakdown from animatic → build order.
6. Milestones with lock dates.
7. Collections by function: Assets/Characters, Assets/Props, Sets, Fx, Lights, Cameras, Rigs, Scratch. Naming: `CHR_HeroKnight_01`, `SET_CityMain_Street_02`, `PRP_Lantern_Wall_01`, `LT_Key_01`, `CAM_Shot03A`.
8. Scenes & view layers. Linked assets + library overrides. Clean unused data-blocks.
9. Blockout: every asset exists as low-detail proxy at final scale. Gate: blockout approved → modeling. Stand-in → proxy → final (never skip stand-in).
10. Commit fps, resolution, aspect, engine (with decision 5.2 if unset).

## Procedures

### Fundamentals → Data model → Object → Mesh → Component
Object → data block → mesh → verts/edges/faces → loops → selection → edit transform → normals → UVs → vertex groups → shape keys.
Object transform → location/rotation/scale → origin → parenting → local space → constraints (D53).

### Blockout → Stand-in → Proxy → Final
Approve composition, scale, and proportion in 3D before investing in detail.

### Solo studio layout (5.9 / D123)
```
project/
  00_docs/ 01_reference/ 02_concept/ 03_storyboard/
  04_assets/<type>/<asset>/  (blend, textures/, caches/)
  05_shots/<shot>.blend 06_render/<shot>/ 07_comp/ 08_edit/
  09_deliver/ cache/ backup/
```

## Decision Logic

- Physics/sim weird? Check scale first.
- Mixing cm characters in meter worlds → rebuild early.
- One naming convention, one engine, one fps — commit now.

## Inputs

- Animatic / shot list / asset list (from preproduction)
- Style, medium, target engine
- Hardware limits

## Outputs

- Unit/scale policy + scale master
- Budgets document
- Naming legend + collection scheme
- Project tree
- Blockout scene(s)
- Committed fps/resolution/engine
- Shared state: `project.*`, `budgets`, `locks.blockout`

## Tools

Blender 4.x, Outliner, Asset Browser, hotkeys (`knowledge/system/hotkeys.md`). Depth supplements S-06, S-07, S-08.

## Constraints

Do not detail during blockout. Do not leave origins random. Do not skip applying scale. Do not put 500 objects in one unsorted collection.

## Edge Cases

- Jewelry/macro: centimeters, but keep a documented conversion to the master meter world.
- Planetary scale: do not put the planet and the character in one sim space.

## Failure Modes & Fixes

| FAIL | DIAG | FIX |
|---|---|---|
| Cloth/fluid explode | Unit scale wrong | Standardize meters; rebuild |
| Rigs misalign | Origin/scale unapplied | Apply transforms; set origins deliberately |
| Unworkable scene | No collections | Rebuild collection tree |
| Infinite polish | No lock dates | Write milestones |

## Dependencies

- Consumes preproduction shot/asset list
- Required by every production skill
- Hands project tree conventions to `production-finishing`

## Related Skills

preproduction, modeling, environment, production-finishing, rigging

## Delegation Rules

- Modeling the final mesh → `modeling`
- Folder/version/QC policy depth → `production-finishing`
- Engine choice → `decision-engine` 5.2

## Examples

- New short: metric meters, 24 fps, 1920×1080, Cycles, naming legend in 00_docs, blockout of all shots in one layout file, scale master always visible.

## Required Knowledge / Context

- `knowledge/domains/ch02-foundations.md`
- `knowledge/system/02d-depth-supplements.md` (S-06 S-07 S-08)
- `knowledge/system/hotkeys.md`

## References to Shared Resources

- `context/production-economy.md`
- `workflows/34-stage-journey.md`
