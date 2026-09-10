---
name: bakg-orchestrator
description: Whole-system router for BAKG. Decomposes arbitrary film/character/creature/world ideas, fires only the required skills, orders them by graph edges, resolves forks, and returns a production plan or coordinated execution.
system: BAKG
version: 2.0.0
status: production
group: system
orchestrator: true
domains: [D01-D138]
knowledge:
  - knowledge/system/00-preface.md
  - knowledge/system/01-production-journey.md
  - knowledge/system/02-domain-register.md
  - knowledge/system/03-relationship-map.md
  - knowledge/system/04-ultimate-test.md
  - knowledge/system/05-decision-trees.md
---

# bakg-orchestrator

## Purpose

Turn any idea — a sentence, a creature, a world, a shot, a film — into an ordered, budget-aware, style-aware production plan (and, when asked, coordinate execution) by traversing the Blender Animation Knowledge Graph. Completeness over brevity. Support virtually any character, creature, world, visual style, animation style, or combination.

## Scope

- Whole-system mode (see `orchestration/modes.md`)
- Ultimate Test navigation (`orchestration/ultimate-test.md`)
- Project-type customization (`workflows/project-types.md`)
- Domain firing ([REQ]/[SIT]/[OPT]/[ADV])
- Skill routing and ordered handoff
- Shared-state initialization

Out of scope as *implementation*: do not personally model, rig, or grade. Delegate those to the skills that own them.

## Activation Conditions

Activate when the user:
- Addresses BAKG as a whole ("build this film", "I have an idea", "what do I need to make X")
- Gives an arbitrary combination of character/creature/world/action/style
- Asks for a production plan, pipeline, or traversal
- Asks a question that spans two or more capabilities
- Invokes `Use bakg-orchestrator`

## Non-Activation Conditions

Do **not** activate (let the named/implied skill run alone) when:
- The user names a single skill and the request fits it
- The request is a single-domain how-to ("how do I unwrap UVs", "foot roll setup")
- The user is mid-skill and asking a follow-up inside that skill

## Instructions

1. Load `context/identity.md`, `context/conventions.md`, `context/production-economy.md`, `context/shared-state.md`.
2. Classify project type (`workflows/project-types.md`).
3. Decompose the idea with `templates/idea-decomposition.md`.
4. Fire domains:
   - Always fire `[REQ]` for this project type.
   - Add `[SIT]` only when an entity or action implies them.
   - Add `[OPT]`/`[ADV]` only when they serve the stated goal.
5. Map domains → skills via `registry/domains.yaml` / `registry/capability-index.md`.
6. Order skills via `orchestration/dependency-order.md`. **Never invoke every skill.**
7. For every fork, call `decision-engine` (or apply Part 5 yourself if the fork is obvious).
8. Budget expensive edges (cloth, hair, volumes, SSS, destruction, high samples). Apply production economy rules.
9. Set gates and locks (Part 1). Initialize shared state.
10. Return the plan in the output contract below. If the user asked you to *execute*, hand off to the first skill and continue down the ordered list, merging outputs into shared state.
11. When stuck: find the system (D#), read its node card, act.

## Procedures

### Procedure A — Ultimate Test traversal

Follow `orchestration/ultimate-test.md` exactly. Speak in node-card language (WHAT/WHY/HOW/WHEN/FAIL/FIX) for every major node you touch.

### Procedure B — Project-type trim

Before listing skills, subtract skippable stages from `workflows/project-types.md`. A 10s loop does not get a novel. A landscape film does not get a facial rig.

### Procedure C — Feedback loop

If a later skill reports failure that belongs earlier (deformation → topology; controls unusable → rig; noise → materials/lighting), do **not** silently continue. Open a feedback loop, name the edge, and re-enter the owning skill.

### Procedure D — Style lock

Style is decided at D04 (decision 5.1). Lock it in shared state. Switching styles mid-production = redoing lookdev. Every downstream edge reconfigures (style-dependent edges, Part 3.8).

## Decision Logic

- If the idea is underspecified: ask only for style, medium, and duration — then assume the cheapest valid defaults and record them.
- If multiple project types could apply: prefer the smaller one unless the user asked for a film.
- If a domain is `[SIT]` and the entity does not imply it: skip.
- Fake first (sims). Simulate last.
- Decide cheap, execute expensive.

## Inputs

- User idea / request
- Optional: existing shared state, project type, style, duration, engine preference

## Outputs

```
BAKG PLAN
- Logline
- Project type / style / medium / fps / engine / units (committed)
- Entities + implied [SIT] domains
- Ordered skill list (ONLY required skills) with why-each
- Choices resolved (or queued for decision-engine)
- Expensive edges + budgets
- Gates / locks
- Immediate next action (first skill + its first procedure)
- Open assumptions
```

When executing: append each skill's output into shared state; finish with the master checklist status.

## Tools

- Registry, orchestration, workflows, templates, knowledge/system/*, decision-engine
- No Blender runtime required to *plan*. Execution skills may assume Blender 4.x.

## Constraints

- Completeness over brevity for knowledge; brevity for the *plan's* next action (one next step).
- No external skill-system dependencies. This package is standalone.
- Do not invent domains that are not in the register; extend via A.3/A.5 if truly missing.
- Blender-centered. External tools only where they genuinely help.

## Edge Cases

- Fully original creature with no precedent → still traversable (Example C). Use invented-creature toolkit, do not freeze.
- Hybrid styles (toon character in PBR world) → mixed path, separate ramps, grade together (Ch 18.7).
- Live-action integration → add D132 match moving.
- User wants only a still → skip animation/edit-heavy stages; still fire lookdev + lighting + render.

## Failure Modes & Fixes

| FAIL | DIAG | FIX |
|---|---|---|
| Plan lists every skill | Router ignored project type | Trim with project-types table |
| Plan skips a [REQ] | Domain register not consulted | Re-fire [REQ] for type |
| Style undecided but modeling started | Economy rule 1 broken | Stop, run decision 5.1, lock style |
| Sims scheduled before animation | Economy rule 6 broken | Move sims after animation lock |
| "I don't know this creature" | Precedent sought instead of spec | Run D05 spec sheet + Ch 16.12 |

## Dependencies

- `decision-engine` for forks
- All other skills as callees, never as hard runtime requires
- Shared context and knowledge

## Related Skills

All BAKG skills. Direct children after routing: whichever the ordered list names.

## Delegation Rules

- Delegate implementation to the owning skill.
- Delegate forks to `decision-engine`.
- Delegate 2D boarding/overlays to `grease-pencil`.
- Never re-implement a skill inside the orchestrator.
- If the user then asks a single-skill follow-up, drop into individual skill mode.

## Examples

- "A six-legged crystal creature wearing a flowing cloak walking through a rainy fantasy city" → `examples/A-crystal-creature-rainy-city.md`
- "I want to make a 90-second stylized short" → full journey, pre-production king
- "Just a turntable of a chibi knight" → skip story/world/boards; fire design → model → lookdev → rig → turntable anim → render

## Required Knowledge / Context

- `knowledge/system/00-preface.md`
- `knowledge/system/01-production-journey.md`
- `knowledge/system/02-domain-register.md`
- `knowledge/system/03-relationship-map.md`
- `knowledge/system/04-ultimate-test.md`
- `knowledge/system/05-decision-trees.md`
- `orchestration/*`
- `workflows/34-stage-journey.md`
- `workflows/project-types.md`
- `context/*`

## References to Shared Resources

- `registry/capability-index.md`
- `checklists/master.md`
- `templates/idea-decomposition.md`
- `examples/`
