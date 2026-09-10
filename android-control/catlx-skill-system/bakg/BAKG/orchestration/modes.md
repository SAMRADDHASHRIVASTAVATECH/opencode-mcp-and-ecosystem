# Operating Modes

## Individual skill mode

Trigger: the user names a skill, or the request is clearly inside one capability.

```
Use <skill-name>
```

or implicit: "How do I unwrap this character?" → `lookdev` (D25).

Rules:
- Operate independently.
- Load that skill's SKILL.md and its listed knowledge files.
- Read shared context (`context/`) and shared state if present.
- Do **not** invoke the full orchestrator.
- You MAY consult `decision-engine` for a fork inside your scope.
- You MAY delegate a **narrow** sub-question to a related skill (see that skill's Delegation Rules) and then resume.
- Return that skill's expected outputs.

## Whole-system mode

Trigger: an idea, a film, a creature, a shot, or a multi-stage request that spans more than one capability.

```
User Request
     ↓
bakg-orchestrator
     ↓
Decompose → Fire domains → Map to skills → Order by edges
     ↓
Only the required skills (never all of them)
     ↓
Shared context / knowledge / state
     ↓
Final Result
```

Rules:
- Orchestrator determines required capabilities.
- Do **not** automatically invoke every skill.
- Fire all `[REQ]` domains for the project type; add `[SIT]` only when the entity/action implies them; add `[OPT]`/`[ADV]` only when they improve the stated goal.
- Resolve forks via `decision-engine`.
- Execute in Part 1 journey order with QC gates.
- When stuck: find the system (D#), read its node card, act.

## Escalation

If an individual skill discovers the request actually spans the whole pipeline, it should:
1. Say so.
2. Hand off to `bakg-orchestrator`.
3. Pass along any state it already produced.
