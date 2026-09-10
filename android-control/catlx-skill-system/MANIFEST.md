# CATLX Skill System — Manifest

> Machine-readable manifest of the skill ecosystem. The canonical machine-readable registry is
> `metadata/skills-registry.json` (generated from the `SKILL.md` frontmatter by `scripts/build_registry.py`).
> This file is the human-readable summary of that registry and the ecosystem metadata.

## Ecosystem metadata

| Field | Value |
|---|---|
| `name` | CATLX Universal AI Operating System skill ecosystem |
| `version` | 1.0.0 |
| `target_runtime` | OpenCode (`SKILL.md` + `skill` tool) |
| `root_skill` | `catlx` |
| `orchestrator_skill` | `catlx-orchestrator` (Universal Mode) |
| `skill_count` | 20 (1 orchestrator + 18 subsystem/root + 1 integration: `antigravity-last-resort`) |
| `source_document` | `CATLX_Universal_AI_OS_Specification.pdf` (Master Architecture Specification, v1.0.0, Rev A) |
| `platform` | Windows 10 / 11 only |
| `scope_exclusions` | Phone integration (Part VI) removed by user request; USB performance tiering (portability) — removed deliberately |
| `canonical_knowledge_dir` | `knowledge/` |
| `component_lifecycle_policy` | `knowledge/rules/component-lifecycle.md` (reuse → install → adapt → create; last-resort creation) |

## Skill manifest

| id | path | description |
|---|---|---|
| `catlx-orchestrator` | `skills/catlx-orchestrator/SKILL.md` | Universal Orchestrator (auto-routing entry) |
| `catlx` | `skills/catlx/SKILL.md` | Root gateway + router |
| `catlx-hardware-adaptation` | `skills/catlx-hardware-adaptation/SKILL.md` | Tiers, capability matrix, CapabilityRouter, re-adaptation |
| `catlx-silexis-modules` | `skills/catlx-silexis-modules/SKILL.md` | Module lifecycle + registry |
| `catlx-capability-routing` | `skills/catlx-capability-routing/SKILL.md` | Env routing + fallback + registries + GUI sync |
| `catlx-voice-pipeline` | `skills/catlx-voice-pipeline/SKILL.md` | Voice-first pipeline |
| `catlx-desktop-control` | `skills/catlx-desktop-control/SKILL.md` | Desktop Control Engine |
| `catlx-screen-understanding` | `skills/catlx-screen-understanding/SKILL.md` | OCR + ScreenModel |
| `catlx-memory` | `skills/catlx-memory/SKILL.md` | Memory architecture + Memory Broker |
| `catlx-ai-provider` | `skills/catlx-ai-provider/SKILL.md` | PAL, routing/failover, local LLM |
| `catlx-workflow-engine` | `skills/catlx-workflow-engine/SKILL.md` | Workflow DAG engine |
| `catlx-security` | `skills/catlx-security/SKILL.md` | Security layer |
| `catlx-telemetry` | `skills/catlx-telemetry/SKILL.md` | Telemetry/observability |
| `catlx-electron-shell` | `skills/catlx-electron-shell/SKILL.md` | Electron OS shell |
| `catlx-plugin-ecosystem` | `skills/catlx-plugin-ecosystem/SKILL.md` | Plugin ecosystem |
| `catlx-docker` | `skills/catlx-docker/SKILL.md` | Docker architecture |
| `catlx-portability` | `skills/catlx-portability/SKILL.md` | Portability (USB-free) |
| `catlx-recovery` | `skills/catlx-recovery/SKILL.md` | Recovery architecture |
| `catlx-runtime-lifecycle` | `skills/catlx-runtime-lifecycle/SKILL.md` | Lifecycle sequences |
| `antigravity-last-resort` | `skills/antigravity-last-resort/SKILL.md` | Final escalation bridge — headless `agy` (last resort only; validates & integrates; graceful degradation) |

> Full per-skill fields (capabilities, dependencies, delegation targets, references, source) are in
> `metadata/skills-registry.json` and `INDEX.md`.

## Dependencies & relationships

- **Per-skill `depends_on`** (static capability prerequisites) — see `metadata/skills-registry.json`
  (`depends_on`) and `DEPENDENCY-GRAPH.md`.
- **Per-skill `delegates_to`** (dynamic routing targets) — see `DEPENDENCY-GRAPH.md`.
- **Canonical knowledge dependencies** — each skill references `knowledge/` files (single source of truth).

## Supporting artifacts

| Artifact | Path |
|---|---|
| Global index | `INDEX.md` |
| Dependency graph | `DEPENDENCY-GRAPH.md` |
| Dependency graph (machine) | `metadata/dependency-graph.json` |
| Capability index + intent map | `metadata/capability-index.json` |
| Source map | `SOURCE-MAP.md` |
| Coverage matrix | `COVERAGE.md` |
| Workflow example | `workflows/summarize-clipboard.yaml` |
| Templates | `templates/module-manifest.json`, `plugin-manifest.json`, `providers.yaml`, `permissions.yaml`, `capabilities.yaml`, `docker-compose.fragment.yml` |
| Examples | `examples/capability-map.json`, `screen-model.json`, `stt-fallback-chain.md`, `voice-command-lifecycle.md` |
| Canonical knowledge | `knowledge/concepts/`, `knowledge/rules/`, `knowledge/references/` |
| Registry generator + validator | `scripts/build_registry.py` |

## Extensibility

To add a new skill later: create `skills/<new-name>/SKILL.md` with valid frontmatter (name = folder,
description), declare `metadata.depends-on`, reference canonical knowledge, and route to existing skills via
the `skill` tool. Re-run `python scripts/build_registry.py` to regenerate the registry and re-validate.
The index, dependency graph, source map, and coverage matrix are regenerated from the registry/artifacts —
so a new skill discovers itself without rewriting the ecosystem.
