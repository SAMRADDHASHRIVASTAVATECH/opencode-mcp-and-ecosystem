---
name: decision-engine
description: Resolves every major BAKG fork — style, engine, modeling workflow, rig type, hair/fur, sim vs fake, DoF/MB, formats, when to stop, facial method, shading style, mocap vs hand-key, realtime vs offline, base mesh, outline method, weather, rig build order.
system: BAKG
version: 2.0.0
status: production
group: system
domains: [choice-nodes]
knowledge:
  - knowledge/system/05-decision-trees.md
---

# decision-engine

## Purpose

When a fork appears in a traversal or inside a skill, pick the option using the documented choice libraries — not taste, not "it depends" without a rule.

## Scope

Part 5 trees 5.1–5.19 and the style-dependent edges (Part 3.8). Does not execute the chosen workflow; returns the choice plus consequences.

## Activation Conditions

- User asks "which / should I / Cycles or EEVEE / sim or fake / IK or FK / toon or realistic"
- Orchestrator or any skill hits a documented fork
- `Use decision-engine`

## Non-Activation Conditions

- The choice is already locked in shared state
- The question is how to *build* the chosen system (that belongs to the owning skill)
- No fork exists (pure procedure)

## Instructions

1. Identify the tree (5.1–5.19).
2. Ask only the missing condition that the table needs.
3. Return: choice, why, what it reconfigures downstream, what it forbids.
4. Write the lock into shared state when the choice is production-binding (style, engine, fps, naming, rig type).

## Procedures

### 5.1 Style & look (fires at D04)
Realistic → anatomy, SSS, Cycles.
Cartoon/game/toon, fast → stylized, EEVEE.
Anime → 2-tone Shader-to-RGB, bold palettes.
Abstract → GN + sims + comp.
Hybrid → match grounding (lighting/render) to the hero element.
**Rule:** decide at D04; switching mid-production = redoing lookdev.

### 5.2 Render engine (D113)
Film realism / refraction / SSS / volumes / time available → Cycles.
Realtime, stylized, tight deadline, long film → EEVEE.
Game pipeline → EEVEE or export.
Blockout/previs → Workbench.
Hybrid iterate EEVEE, hero Cycles — keep materials PBR-pure so the swap is settings, not re-lookdev.

### 5.3 Modeling workflow
Realistic human/creature film → sculpt-first → retopo → bake.
Stylized boxy/cute → box-model + subdiv.
Hard-surface → box + bevels + booleans + modifiers.
City/backgrounds → modular + procedural.
Original creature → sculpt-first + spec sheet.
Hero prop → hybrid box + sculpt detail + bake.

### 5.4 Rig type
Biped → FK/IK switch + FK/BBone spine + stretch option.
Quadruped → 4× leg IK + spine BBone + neck + tail.
6+ legs → per-leg IK + gait driver.
Snake/tentacle/tail → BBone or FK + stretch.
Wings → feather-row hierarchy + IK wingtip + fold.
Mechanical → constrained axis, pistons, no soft deform.
Cartoon stretchy → Stretch-to + squash/stretch global.
Realistic facial → shape-key + bone control rig.
Stylized facial → bone-driven.
Minimal prop → single bone/constraint. Do not over-rig.

### 5.5 Hair / fur / feathers
Hero film hair → curves + manual groom + dynamics.
Stylized hair → curves + simple sim or driver sway.
Mammal fur → GN fur or curves + noise.
Feathers → GN instances + wing hierarchy.
Background → low-density or alpha cards.
Realtime → cards/planes or low strand counts.

### 5.6 / 5.18 Sim vs fake
**Rule: fake first.** Sim only when faking is harder or visibly worse.
Hero cloak → sim. Distant flag → vertex sway driver.
Ocean → Ocean modifier. Puddle → ripple shader.
Hero splash → sim or splash assets. Stylized fire breath → emissive curve + particles + glow.
Realistic fire → sim. Rain → particles + wetness, not fluid.
Jiggle → drivers/bones or soft body.

### 5.7 DoF & motion blur
Stylized/cheap DoF → comp Defocus on Z.
Hero close-up realism → render DoF.
Fast action MB → render 2–8% shutter.
Cheap MB → vector blur in comp.
Heavy scene → comp both; render MB off.

### 5.8 Format & color
Final frames → EXR multilayer.
Edit master → ProRes 422 HQ / DNxHR.
Web → H.264/H.265 CRF 18–23.
Color → AgX. Film emulation → ACES/LUTs in comp.

### 5.9 Project structure
See production-finishing and `knowledge/system/05-decision-trees.md` 5.9 tree.

### 5.10 When to stop
Animation reads, contacts clean, second-eyes approved → lock animation.
Hero materials approved under final lighting → lock lookdev.
Caches stable → lock sims.
Test frames clean, budget met → lock render.
Pacing works, grade done, QC passed → deliver.
Locks are promises. Honor them.

### 5.11 Add-ons
Learn the system first, add the speed tool second. Document the manifest. Built-in > add-on where equal. License-check assets.

### 5.12 Facial rig method
Realistic hero + lip sync → shape-key library + control rig (Ch 19).
Stylized → bone-driven.
Creature → bones + few species keys.
Mocap face → ARKit-named blendshapes.
Background → 3–5 keys. Never over-build.
Toon drawn expressions → shape keys + GP overlay.

### 5.13 Shading style
Physical → Principled + maps.
Cel → Shader-to-RGB ramp + hull outline.
Anime → 2–3 tone + anime eye + face-shadow + selective outline.
Cartoon → bold 2-tone, thick hull.
Painterly → UV-perturb noise + soft comp.
Game → stylized PBR + ramp.
Mixed → separate ramps, grade together.

### 5.14 Mocap vs hand-key
Realistic human body, fast → mocap + foot fixes.
Stylized/exaggerated → hand-key.
Creatures → hand-key from animal ref.
Dialogue CU → hand-key face/eyes; mocap body if useful.
Hybrid (industry standard) → mocap body + hand-key face/hands/eyes.

### 5.15 Offline vs real-time
Film realism → Cycles. Stylized film / long runtime → EEVEE. Game/web → export pipeline (Ch 25).

### 5.16 Base mesh source
Build vs Rigify/base mesh vs scan. Film hero often sculpt-from-base or scan+retopo. Stylized often box or base mesh.

### 5.17 Outline method
Four methods in Ch 18.4 — pick per need (inverted hull, line art modifier, freestyle, GP).

### 5.19 Rig build order
The checklist is the tree. Follow `templates/rig-signoff.md` and Ch 6/28 order: skeleton → orientations → deform bones → IK/FK → spine/hands/feet → constraints → controllers → weights → correctives → facial → sign-off.

## Inputs

- Fork id or natural-language choice
- Project style, medium, budgets, whether hero vs background

## Outputs

```
CHOICE
- tree: 5.x
- pick: ...
- because: ...
- lock?: yes/no
- reconfigures: [downstream domains/skills]
- forbids: ...
```

## Tools

- `knowledge/system/05-decision-trees.md` (full tables)
- Shared state locks

## Constraints

Do not invent a fifth engine or a sixth style path without using A.3 extension protocol. Do not override a lock without calling out a feedback loop.

## Edge Cases

Conflicting signals ("realistic anime") → treat as hybrid; ask which element is hero. Mixed toon/PBR is legal (5.13 mixed).

## Failure Modes & Fixes

| FAIL | FIX |
|---|---|
| "It depends" with no table | Re-run the matching 5.x tree |
| Style changed after lookdev | Flag redo; do not patch |
| Sim chosen for background rain | Switch to fake (5.6) |

## Dependencies

None required. Consumes shared state. Produces locks that all skills must respect.

## Related Skills

All skills consume this. Closest: `bakg-orchestrator`.

## Delegation Rules

After choosing, hand back to the caller. If the caller was the user, name the skill that should execute next.

## Examples

- "Cycles or EEVEE for a rainy city with crystal refraction?" → Cycles (refraction/SSS/volumes).
- "Should I sim the distant flags?" → No. Vertex sway driver.
- "Bone face or blendshapes for a talking realistic hero?" → Shape-key library + control rig (5.12).

## Required Knowledge / Context

- `knowledge/system/05-decision-trees.md`
- `knowledge/system/03-relationship-map.md` (section 3.8 style-dependent edges)
- `context/production-economy.md`

## References to Shared Resources

- `orchestration/ultimate-test.md`
- `templates/idea-decomposition.md`
