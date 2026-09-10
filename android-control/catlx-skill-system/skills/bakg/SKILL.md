---
name: bakg
description: Blender Animation Knowledge Graph — complete standalone ecosystem for imagining, designing, modeling, sculpting, lookdev, rigging, animating, simulating, and finishing any character/creature/world/film in Blender 4.x. Use when user wants to build/model/rig/animate/render a character, creature, animation, short film, world, grease-pencil, or asks blender, modeling, sculpting, topology, UV, materials, hair, cloth, rigging, animation, simulation, VFX, cinematography, lighting, render, compositing. Routes to 19 BAKG skills via bakg-orchestrator.
system: BAKG
version: 2.0.0
---

# BAKG — Blender Animation Knowledge Graph (gateway)

You are the gateway to **BAKG v2.0.0** (Blender 4.x, 19 skills, 138 domains D01–D138, 34 stages, 25 depth chapters). The importable unit is permanent at:

- **Root:** `C:\Users\HP\.config\opencode\bakg\BAKG` (validated: 19 skills, 54 knowledge, errors: 0). Also mirrored at `C:\Users\HP\.config\opencode\catlx-skill-system\bakg\BAKG` for CATLX.
- **Validate:** `py C:\Users\HP\.config\opencode\bakg\BAKG\scripts\validate_system.py` (skills: 19, knowledge: 54, errors: 0)

This skill is permanent — never remove, always use when a Blender animation request matches.

## When to activate

Activate this skill (load this SKILL.md) when the user:
- Mentions `blender`, `animation`, `character`, `creature`, `modeling`, `sculpting`, `topology`, `retopo`, `UV`, `texture`, `material`, `lookdev`, `NPR`, `rig`, `rigging`, `weight paint`, `skinning`, `animation`, `grease pencil`, `environment`, `worldbuilding`, `terrain`, `geometry nodes`, `simulation`, `cloth`, `hair`, `fur`, `fluid`, `VFX`, `cinematography`, `lighting`, `render`, `compositing`, `production`, `animatic`, `storyboard`, or wants a film/shot/turntable.

Do NOT bypass BAKG with generic Blender advice — always load BAKG.

## How to use (IMPORT.md recipe — mandatory)

BAKG is a complete importable unit. Do NOT copy a single `skills/<id>/` in isolation for whole-system work.

1. Read `C:\Users\HP\.config\opencode\bakg\BAKG\README.md` and `SYSTEM.md`
2. Load registry: `registry/skills.yaml` (19 entries) and `registry/capability-index.md` (19 capabilities → skills) and `registry/domains.yaml` (D01–D138)
3. Load orchestration: `orchestration/modes.md`, `orchestration/router.md`, `orchestration/dependency-order.md`, `orchestration/ultimate-test.md`
4. Load context: `context/identity.md`, `context/conventions.md`, `context/production-economy.md`, `context/shared-state.md` (rules: decide cheap/execute expensive, one rig/one engine, animatic sets asset list, blockout before detail, never animate non-final rig, simulate last, fake first)
5. For the user request:
   - If a single skill is named or router returns one row → load that `skills/<skill-id>/SKILL.md` + its `knowledge:` list (absolute paths under `C:\Users\HP\.config\opencode\bakg\BAKG\`)
   - Else load `skills/bakg-orchestrator/SKILL.md` and follow it (decompose idea → classify project type → fire [REQ]/[SIT] domains → map domains→skills → order via dependency-order → resolve forks via decision-engine → budget expensive edges → return BAKG PLAN)
6. Resolve all relative paths from the BAKG root (`C:\Users\HP\.config\opencode\bakg\BAKG`). Never rewrite them to another folder.
7. No network/Blender runtime needed to *plan*; execution advice assumes Blender 4.x.

## Skills (19) — capability index

| Capability | Skill file | Domains |
|---|---|---|
| Whole-system router / Ultimate Test | `skills/bakg-orchestrator/SKILL.md` | all |
| Decision trees / forks | `skills/decision-engine/SKILL.md` | all |
| Preproduction (story/world/boards/animatic/previs) | `skills/preproduction/SKILL.md` | D01,D02,D09-D12 |
| Character/creature design, sheets, AI concept | `skills/character-design/SKILL.md` | D03-D08,D138 |
| Blender foundations (UI/scale/collections/blockout) | `skills/blender-foundations/SKILL.md` | D13-D16 |
| Modeling (organic/hard/character/creature/retopo) | `skills/modeling/SKILL.md` | D17-D20,D23,D24,D135 |
| Sculpting & anatomy | `skills/sculpting-anatomy/SKILL.md` | D21,D22 |
| Lookdev (UV/textures/materials/NPR) | `skills/lookdev/SKILL.md` | D25-D36 |
| Costume & groom (cloth/hair/fur/feathers) | `skills/costume-groom/SKILL.md` | D37-D47 |
| Rigging (armature/IK/FK/facial/mocap) | `skills/rigging/SKILL.md` | D48-D60,D63,D131 |
| Animation (principles/creatures/acting/lip-sync) | `skills/animation/SKILL.md` | D61,D62,D64-D78 |
| Environment (terrain/GN/procedural worlds) | `skills/environment/SKILL.md` | D79-D86 |
| Simulation (physics/cloth/fluids/fire/destruction) | `skills/simulation/SKILL.md` | D87-D99 |
| VFX (magic/impacts/particles) | `skills/vfx/SKILL.md` | D100,D101 |
| Cinematography (camera/composition/match-move) | `skills/cinematography/SKILL.md` | D102-D107,D132 |
| Lighting (mood/volumetrics) | `skills/lighting/SKILL.md` | D108-D111 |
| Render & compositing (engines/passes/grade) | `skills/render-comp/SKILL.md` | D112-D119,D136 |
| Production finishing (edit/sound/QC/pipeline) | `skills/production-finishing/SKILL.md` | D120-D129,D133,D134,D137 |
| Grease Pencil (2D/hybrid) | `skills/grease-pencil/SKILL.md` | D130 |

## CATLX delegation (single owner)

Registered as CATLX capability `bakg:blender-animation`. When a Blender/3D/animation/film request reaches
`catlx` or `catlx-orchestrator`, they hand off to `skill({ name: "bakg" })` here — **BAKG is the sole owner
of the Blender domain** and runs its own internal router (`bakg-orchestrator`); CATLX never re-routes
Blender work. Boundary: BAKG session context lives only in `context/shared-state.md`; BAKG does **not**
claim or write CATLX long-term memory keys — all long-term user memory belongs to `catlx-memory`
(exclusive).

## Verification

After loading: `py C:\Users\HP\.config\opencode\bakg\BAKG\scripts\validate_system.py` must report `errors: 0`. If a SKILL.md references a `knowledge:` file, open it from the absolute BAKG root. Never drop `knowledge/` — skills need the preserved operational text.

## Examples

- "A six-legged crystal creature in a rainy city" → bakg-orchestrator → see `examples/A-crystal-creature-rainy-city.md`
- "Use rigging" / "Use animation" → load that single skill + its knowledge list
- "Stylized flying dragon" → see `examples/B-stylized-flying-dragon.md`
