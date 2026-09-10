# Ultimate Test Navigation Method

Learn this once. This is how BAKG is meant to be used.

Take an arbitrary idea and answer, using this system:

1. DESIGN IT → preproduction + character-design (D03–D08)
2. MODEL/SCULPT IT → modeling + sculpting-anatomy (D17–D24)
3. TEXTURE/MATERIAL IT → lookdev (D25–D36)
4. CLOTHE + GROOM IT → costume-groom (D37–D47)
5. RIG + DEFORM IT → rigging (D48–D63)
6. ANIMATE IT → animation (D64–D78)
7. WORLD IT → environment (D79–D86)
8. SIMULATE IT → simulation (D87–D99)
9. LIGHT + FILM IT → vfx + cinematography + lighting (D100–D111)
10. RENDER + FINISH IT → render-comp + production-finishing (D112–D129)

## The general navigation recipe (print this)

1. Decompose idea → entities + actions.
2. For each entity: organic/hard/hybrid? humanoid/creature/object? style?
3. Fire `[REQ]` domains; add `[SIT]` domains the entity/action implies.
4. Follow dependency edges (Part 3) — build the ordered task list.
5. Resolve every choice node with `decision-engine`.
6. Budget the expensive edges; set locks and gates (Part 1).
7. Execute in Part 1's journey order, with QC gates (D127).
8. When stuck: find the *system* the problem belongs to (D#), read its node card (WHAT/WHY/HOW/WHEN/FAIL/FIX), and act.

## Decomposition template

```
IDEA: <one sentence: subject + action + setting + mood>
ENTITIES:
  - name / class (character|creature|prop|environment|effect)
    organic/hard/hybrid:
    style:
    implied [SIT] domains:
ACTIONS:
  - verb → animation/sim/vfx domains
SETTING:
  - climate / TOD / palette → environment + lighting
STYLE:
  - decision tree 5.1
REQ DOMAINS: always-on for this project type
SIT DOMAINS: implied
OPT/ADV: only if they serve the idea
SKILL ORDER: from edges
CHOICES TO RESOLVE: from Part 5
GATES: from Part 1
```

Worked examples live in `examples/` and the full traversals in `knowledge/system/04-ultimate-test.md`.
