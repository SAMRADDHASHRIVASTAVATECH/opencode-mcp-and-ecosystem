# BAKG Conventions

## Domain numbers

Domain numbers (e.g., `D17`) refer to the Master Domain Register (`knowledge/system/02-domain-register.md`). Cross-references appear as `D17 → D23` or "see D17 (Organic Modeling)".

## Status markers

Every pipeline stage and every domain carries a status:

| Marker | Meaning | Example |
|---|---|---|
| `[REQ]` | REQUIRED — no project can skip it | modeling, rigging, rendering |
| `[OPT]` | OPTIONAL — adds quality, skippable | storyboard for a single looping shot |
| `[SIT]` | SITUATION-DEPENDENT — needed only for certain project types | lip sync only if characters speak |
| `[ADV]` | ADVANCED — power tools for complex/high-end work | correctives, AOVs, custom drivers |

## Hierarchical levels

| Level | Meaning | Example (Rigging branch) |
|---|---|---|
| L1 | Domain | Rigging |
| L2 | Discipline/System | Character Rigging |
| L3 | System | Leg Rig |
| L4 | Technique/Method | IK |
| L5 | Variation/Component | Foot IK |
| L6 | Practical Detail | Foot Controller |
| L7+ | Micro-detail | pivot, pole vector, heel roll |

Anywhere a Level-6 item still contains independent knowledge, it is broken down further.

## Node card labels

Major nodes are documented with a full node card. Labels used throughout BAKG:

| Label | Field | Label | Field |
|---|---|---|---|
| DEF | What it is | PARAM | Important parameters & settings |
| WHY | Why it exists | FLOW | Workflow (steps) |
| HOW | How it works | MIST | Common mistakes |
| USE | When to use it | FAIL | Failure modes |
| AVOID | When NOT to use it | DIAG | How to diagnose |
| OPT | Available options | FIX | Fixes / troubleshooting |
| ALT | Alternative methods | PERF | Optimization & performance |
| PRO | Advantages | BEG/INT/ADV | Beginner / Intermediate / Advanced |
| CON | Disadvantages | PROD | Production considerations |
| PRE | Prerequisites | EDGES | Related nodes |
| DEP | Dependencies | STATUS | REQ / OPT / SIT / ADV |
| AFF | What it affects | | |

## Blender as central tool

Blender is the central tool. External tools (ZBrush, Substance, Stable Diffusion, PureRef, DaVinci Resolve, etc.) appear only where they genuinely improve a Blender-centered workflow.

Version notes refer to **Blender 4.x**. Where a feature changed across 4.x versions it is flagged.

## Style-agnostic default

Everything is written to support realistic, stylized, anime, cartoon, fantasy, sci-fi, monster, animal, robot, humanoid, hybrid, multi-limbed, flying, swimming, and fully original designs. No single style is assumed.

## Relative paths

All knowledge, workflow, template, and skill references inside BAKG are relative to the BAKG root. Example: `knowledge/domains/ch06-rigging.md`.
