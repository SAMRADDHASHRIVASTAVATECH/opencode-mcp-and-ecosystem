# Importing BAKG

BAKG is a **complete importable unit**. Copy the entire `BAKG/` folder. Do not import a single skill in isolation if you want whole-system mode — the orchestrator, registry, knowledge, and context are part of the product.

## Layout contract

```
BAKG/
  skills/<skill-id>/SKILL.md
  knowledge/…
  context/…
  orchestration/…
  registry/…
  …
```

Each skill folder contains a `SKILL.md` with YAML frontmatter:

```yaml
name: <skill-id>
description: <one line>
system: BAKG
version: 2.0.0
```

## Agent loading recipe

1. Read `README.md` and `SYSTEM.md`.
2. Load `registry/skills.yaml` and `registry/capability-index.md`.
3. Load `orchestration/modes.md` and `orchestration/router.md`.
4. Load `context/conventions.md` and `context/production-economy.md`.
5. For a user request:
   - If a single skill is named or the router returns one row → load that `SKILL.md` + its `knowledge:` list.
   - Else load `skills/bakg-orchestrator/SKILL.md` and follow it.
6. Resolve relative paths from the BAKG root.
7. Do not require network, Blender runtime, or any sibling system to *plan*. Execution advice assumes Blender 4.x.

## Individual skill import

You *may* copy one `skills/<id>/` folder plus the knowledge files it lists, plus `context/conventions.md`. That skill will operate independently but will lose orchestrator routing and some shared templates. Document that limitation if you split the package.

## Dependencies

None outside this folder. Python 3 is optional (only `scripts/validate_system.py`).

## Validation after import

```bash
python3 scripts/validate_system.py
```

## Version

`metadata/system.yaml` — BAKG 2.0.0, source graph v2.0, Blender 4.x era.

## Do not

- Rewrite internal paths to another system's folders
- Merge these skills into another ecosystem without keeping BAKG identity
- Drop `knowledge/` — skills are not wrappers; they still need the preserved operational text for depth
