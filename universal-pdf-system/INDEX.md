# Universal PDF System — Index

Master navigation. Read in this order for the fastest path to understanding.

## 1. Orientation
- [README.md](README.md) — what this is and a quick start
- [MANIFEST.md](MANIFEST.md) — complete file inventory

## 2. Architecture & design
- [ARCHITECTURE.md](ARCHITECTURE.md) — layers, routing, dependency graph
- [docs/DESIGN-NOTES.md](docs/DESIGN-NOTES.md) — scale/weak-model/state/recovery
- [DEPENDENCIES.md](DEPENDENCIES.md) — libraries, optional engines
- [LIMITATIONS.md](LIMITATIONS.md) — honest limits & degradation map

## 3. Skills
- [skills/INDEX.md](skills/INDEX.md) — all 47 skills
- [skills/UNIVERSAL_PDF.md](skills/UNIVERSAL_PDF.md) — master orchestrator skill
- [docs/CAPABILITIES.md](docs/CAPABILITIES.md) — capability matrix
- [registry/dependency-graph.json](registry/dependency-graph.json) — machine-readable graph

## 4. Using it
- [docs/INSTALL.md](docs/INSTALL.md) — install & import
- [docs/USAGE.md](docs/USAGE.md) — individual & system mode
- [workflows/](workflows/) — reusable end-to-end workflows
- [examples/](examples/) — runnable examples
- [templates/](templates/) — document / content templates

## 5. Tests
- [tests/](tests/) — pytest suite (skills + orchestration + large-doc)
- Run: `python -m pytest tests/ -q`

## 6. Developer
- [scripts/generate_skills.py](scripts/generate_skills.py) — regenerate skills/registry
- [scripts/generate_docs.py](scripts/generate_docs.py) — regenerate this + manifest
- [registry/config.json](registry/config.json) — runtime configuration