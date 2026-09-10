# BAKG — Blender Animation Knowledge Graph

A complete, standalone, interconnected skill ecosystem for imagining, designing, building, animating, and finishing any character, creature, world, and animated film in **Blender 4.x** — from a single idea to the final master.

This folder is the **importable unit**. It does not depend on any other skill system.

## What this is

Not a course. Not a feature list. A **knowledge graph** in skill-system form:

- 19 interconnected skills
- 138 domains (D01–D138)
- 34 production stages
- 25 depth chapters + 18 supplements
- Decision trees, workflows, checklists, templates, worked examples
- An orchestrator that fires **only the skills a task needs**

Every node is meant to answer: WHAT it is · WHY it exists · HOW it works · WHEN to use it · WHAT choices exist · WHAT can fail · HOW to fix it.

## Quick start

### Whole-system mode

Give BAKG an idea:

> A six-legged crystal creature wearing a flowing cloak walking through a rainy fantasy city

The orchestrator (`skills/bakg-orchestrator/SKILL.md`) decomposes it, fires implied domains, orders skills by graph edges, and returns a plan. See `examples/A-crystal-creature-rainy-city.md`.

### Individual skill mode

```
Use rigging
Use lookdev
Use animation
```

Each skill can run alone using shared context and knowledge.

### Navigation recipe

1. Decompose idea → entities + actions
2. Organic/hard/hybrid? humanoid/creature/object? style?
3. Fire `[REQ]`; add `[SIT]` only when implied
4. Follow edges (`orchestration/dependency-order.md`)
5. Resolve forks (`skills/decision-engine/SKILL.md`)
6. Budget expensive edges; set locks
7. Execute Part 1 order with QC gates
8. When stuck: find the D#, read its node card, act

## Layout

```
BAKG/
├── README.md  INDEX.md  MANIFEST.md  IMPORT.md  SYSTEM.md
├── skills/                 19 skills, each with SKILL.md
├── knowledge/              full operational source (domains, depth, system)
├── context/                identity, conventions, economy, shared state
├── orchestration/          modes, router, Ultimate Test, delegation
├── workflows/              34-stage journey, project types, pipelines
├── registry/               skills, domains, capability index
├── dependencies/           skill graph
├── templates/  checklists/  examples/
├── metadata/   scripts/
```

Read `SYSTEM.md` for architecture. Read `INDEX.md` to find anything. Read `IMPORT.md` to load this package into another agent environment.

## Standing rules

From `context/production-economy.md`:

1. Decide cheap, execute expensive
2. One rig, one engine, one naming convention
3. The animatic sets the asset list
4. Block out everything before detailing anything
5. Never animate a non-final rig
6. Simulate last
7. Render once, grade twice
8. Back up decisions, not just files

**Fake first.** Sim only when faking is harder or visibly worse.

## Source

Compiled from *The Ultimate Blender Animation Knowledge Graph* v2.0 (August 2026, Blender 4.x). Completeness over brevity. Style-agnostic: realistic, stylized, anime, cartoon, fantasy, sci-fi, creature, mechanical, hybrid, original.

## Validate

```bash
python3 scripts/validate_system.py
```
