---
name: preproduction
description: Story, world bible, storyboard, animatic, previs, and motion reference — the cheap, high-information decisions that set shot count, asset list, and production scope.
system: BAKG
version: 2.0.0
status: production
group: creative
domains: [D01, D02, D09, D10, D11, D12]
knowledge:
  - knowledge/domains/ch01-preproduction.md
  - knowledge/depth/ch38-story-board-animatic.md
  - knowledge/depth/ch27-worldbuilding.md
---

# preproduction

## Purpose

Decide what the film means and what it needs. Every hour here saves days of rework. Produce the contracts that 3D will execute: logline, beats, world bible, boards, animatic, previs, motion ref, shot list.

## Scope

D01 Story & Script [SIT], D02 Worldbuilding [SIT], D09 Storyboard [SIT], D10 Animatics [SIT], D11 Previs [SIT], D12 Motion Reference [SIT]. World *visual* build is `environment`. Character look is `character-design`. 2D drawing craft is `grease-pencil`.

## Activation Conditions

- User asks for story, script, beats, world rules, boards, animatic, previs, motion reference, shot list
- Orchestrator fires pre-production stages
- `Use preproduction`

## Non-Activation Conditions

- Single looping turntable with no narrative (micro-story only; do not over-write)
- Pure visual design of a character (→ character-design)
- Building the 3D city (→ environment)
- Final editing of rendered shots (→ production-finishing)

## Instructions

1. Write the one-sentence premise (subject + action + setting + mood) and 3 emotional goals.
2. If duration > a loop: write beats (each beat = 1–3 shots). A 2-min film needs ~30–60 seconds of story beats, not a novel.
3. Write a 1–3 page world bible (`templates/world-bible.md`). Distill into design constraints.
4. Do not design bodies here — hand personality to `character-design`.
5. Board every beat with camera notation (size/angle/move). Prefer Grease Pencil (`grease-pencil`) or imported images.
6. Cut an animatic to audio in VSE. If it's boring here, 3D will not save it. Lock the animatic.
7. Previs: cameras + primitive stand-ins. Verify the camera can see the action.
8. Motion ref: film the actions; 60 fps+; matching angles.
9. Emit shot list → asset list → pipeline plan (D14, hand to blender-foundations).
10. Commit fps, resolution, engine, naming. Run `checklists/preproduction-handoff.md`.

## Procedures

### Story → Structure → Beat → Shot → Moment
Beat → emotional change → action required → camera distance (D106) → duration → staging → animation intensity → edit rhythm.

**The Beat node:** smallest unit of story change. 1 beat ≈ 1–3 s for loops, 5–15 s for narrative shorts. Board every beat.

### World bible → visual consequences
A rainy city demands cloaks, wet surfaces, puddles, reflections, moody lighting, dripping sounds. Surface one rule per scene; show don't tell. Magic needs explicit limits or stakes die.

### Animatic as contract
The animatic sets shot count, duration, and therefore the asset list and the budget. Lock it before expensive modeling.

### Previs
Place cameras from boards; blocks for characters; cubes for sets; GP strokes for camera paths; Workbench/EEVEE viewport captures; cut in VSE.

## Decision Logic

- No story needed for a pure turntable — write a micro-story (setup→action→payoff) only.
- Skip boards for a single looping shot if staging is obvious; never skip animatic on a multi-shot film.
- Pick ONE frame rate (24 film / 25 PAL / 30–60 web/game) before any animation.
- Delegate shot grammar details to `cinematography` (Ch 21) when boarding.

## Inputs

- Idea / logline / duration / medium
- Style (or request decision 5.1)
- Optional existing script or boards

## Outputs

- Logline, emotional goals, beat list
- World bible
- Shot list with camera notation and durations
- Asset list derived from shots
- Animatic status (locked?)
- Previs notes
- Motion-ref list
- Committed fps / resolution / engine / naming
- Handoff checklist result
- Updates to shared state: `story`, `world`, `shots`

## Tools

Blender VSE, Grease Pencil, phone camera for motion ref, PureRef for boards (external). Knowledge: Ch 1, Depth 38, Depth 27.

## Constraints

Do not over-write. Do not polish the animatic. Do not previs at final quality. Do not board the "nice" shot instead of the story shot.

## Edge Cases

- Dialogue-heavy → also plan D62 lip sync and Ch 23 sound early.
- Experimental/abstract → skip character stages; keep beat structure for pacing.
- Game cutscene → boards/animatic partial; reuse game cameras/assets.

## Failure Modes & Fixes

| MIST/FAIL | FIX |
|---|---|
| Overwriting a 2-min film | Cut to emotional core |
| Beat cannot be boarded simply | Simplify the beat |
| Magic with no rules | Add limits |
| No camera notation | Add size/angle/move per shot |
| Animatic without audio | Recut to scratch audio |
| Skipping animatic on multi-shot | Stop 3D; make animatic |
| Motion from imagination for complex action | Film it |

## Dependencies

- `character-design` consumes world constraints and story roles
- `cinematography` consumes boards
- `blender-foundations` consumes shot/asset list
- `grease-pencil` for boarding inside Blender
- `decision-engine` 5.1 if style unset

## Related Skills

bakg-orchestrator, character-design, grease-pencil, cinematography, environment, production-finishing (editing/sound)

## Delegation Rules

- Character look → `character-design`
- Shot grammar tables → `cinematography`
- Drawing craft / GP3 → `grease-pencil`
- 3D set build → `environment`
- If the user wants the whole film from a sentence → `bakg-orchestrator`

## Examples

- 90s short: write 8–12 beats, board, animatic to temp music, lock, then 3D.
- Rainy city world bible: climate rain, palette desat blue-green, magic = crystals only at night (limit), visual consequences: cloaks, wet cobbles, reflections, warm windows.

## Required Knowledge / Context

- `knowledge/domains/ch01-preproduction.md`
- `knowledge/depth/ch38-story-board-animatic.md`
- `knowledge/depth/ch27-worldbuilding.md`
- `knowledge/system/01-production-journey.md`

## References to Shared Resources

- `templates/world-bible.md`
- `templates/shot-record.md`
- `checklists/preproduction-handoff.md`
- `workflows/34-stage-journey.md`
