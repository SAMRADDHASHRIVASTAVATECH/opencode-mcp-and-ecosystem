# CATLX Skill System — Source Map

> Maps each source location → canonical knowledge → generated skill/reference/workflow. This is the
> traceability record: "where did this knowledge come from?" Paths are relative to this repo.
> **Source document:** `CATLX_Universal_AI_OS_Specification.pdf` — Master Architecture Specification,
> Version 1.0.0, Architecture Revision A, 2025 · CATLX Systems Division. Internal/Confidential.

## Standards for provenance

- **Exact** = quoted/structurally faithful to the source (tables, lists, JSON, YAML).
- **Adapted** = source content mapped to the Windows-only / USB-free target; the change is noted.
- **Inferred** = structural/routing/metadata I added (not domain knowledge); labeled as such.

## Source → generated mapping

| Source location | Semantic purpose | Canonical knowledge | Generated artifact | Type | Status |
|---|---|---|---|---|---|
| §1.1 What CATLX Is | System identity | `knowledge/concepts/pillars-and-mandates.md` | `skills/catlx/SKILL.md` | skill (root) | Exact |
| §1.2 Core Design Mandates | 8 mandates table | `knowledge/concepts/pillars-and-mandates.md` | `knowledge/rules/architectural-rules.md` (R1, R2, R10, R11, R15 …) | rules | Exact |
| §1.3 Architectural Pillars | 11 pillars | `knowledge/concepts/pillars-and-mandates.md` | `INDEX.md` (skill→pillar mapping) | reference | Exact |
| §2.1–2.2 Philosophy of One, Tiers | Tier definitions | `knowledge/references/hardware-adaptation.md` | `skills/catlx-hardware-adaptation/SKILL.md` | skill | Adapted (Windows OS-target rows) |
| §2.3 Capability Matrix | Auto-config matrix | `knowledge/references/hardware-adaptation.md` | `skills/catlx-hardware-adaptation/SKILL.md` | skill | Exact |
| §2.4 Profiler + Decision Tree | Boot scan & CapabilityMap | `knowledge/references/hardware-adaptation.md` | `skills/catlx-hardware-adaptation/SKILL.md`; `templates/capabilities.yaml`; `examples/capability-map.json` | skill/asset | Exact |
| §2.5 Runtime Re-Adaptation | Re-adaptation event | `knowledge/references/hardware-adaptation.md` | `knowledge/rules/architectural-rules.md` (R2) | rule | Exact |
| §3.1–3.2 Module Lifecycle | Extraction→Registry | `knowledge/references/silexis-and-routing.md` | `skills/catlx-silexis-modules/SKILL.md`; `templates/module-manifest.json` | skill/asset | Exact |
| §3.3 Environment Routing | 4 exec environments | `knowledge/references/silexis-and-routing.md` | `skills/catlx-capability-routing/SKILL.md`; `templates/capabilities.yaml` | skill/asset | Exact |
| §3.4 Capability Routing + fallback | Routing + STT chain | `knowledge/references/silexis-and-routing.md` | `skills/catlx-capability-routing/SKILL.md`; `examples/stt-fallback-chain.md` | skill/asset | Exact |
| §3.5 File-Backed Registries | Registry + WAL | `knowledge/references/silexis-and-routing.md`; `knowledge/references/data-registries.md` | `knowledge/rules/architectural-rules.md` (R4) | rule/reference | Exact |
| §3.6–3.7 Evolution + GUI sync | Recommendations, WS bus | `knowledge/references/silexis-and-routing.md` | `skills/catlx-capability-routing/SKILL.md` | skill | Exact |
| §4.1–4.2 Voice pipeline | Voice primary + 10 stages | `knowledge/references/voice-pipeline.md` | `skills/catlx-voice-pipeline/SKILL.md` | skill | Exact |
| §4.3–4.5 Wake word, context, streaming | UW config, context, TTS | `knowledge/references/voice-pipeline.md` | `skills/catlx-voice-pipeline/SKILL.md` | skill | Exact |
| §4.6 Voice lifecycle | Lifecycle | `knowledge/references/voice-pipeline.md` | `examples/voice-command-lifecycle.md`; `knowledge/references/runtime-lifecycle.md` §18.2 | example/reference | Exact |
| §5.1–5.4 DCE overview/mouse/keyboard/window | DCE | `knowledge/references/desktop-control.md` | `skills/catlx-desktop-control/SKILL.md` | skill | Adapted (Windows: SendInput, UIAutomation) |
| §5.5 OCR + Screen Understanding | OCR/ScreenModel | `knowledge/references/screen-understanding.md` | `skills/catlx-screen-understanding/SKILL.md`; `examples/screen-model.json` | skill/asset | Exact |
| §5.6–5.11 Browser/app/file/monitor/HUD/notifications | DCE + shell | `knowledge/references/desktop-control.md` | `skills/catlx-desktop-control/SKILL.md` | skill | Adapted (Windows paths) |
| §6.1–6.4 Phone philosophy + Android app + iOS + transports | Phone integration | (removed) | n/a | — | **Removed by user request** — skill `catlx-phone-integration` deleted |
| §7.1–7.11 Memory architecture | Memory stores/broker/RAG | `knowledge/references/memory-architecture.md` | `skills/catlx-memory/SKILL.md` | skill | Exact |
| §8.1–8.5 AI provider | PAL/providers/routing/local | `knowledge/references/ai-provider.md` | `skills/catlx-ai-provider/SKILL.md`; `templates/providers.yaml` | skill/asset | Exact |
| §9.1–9.9 Workflow engine | DAG/scheduling/DSL | `knowledge/references/workflow-engine.md` | `skills/catlx-workflow-engine/SKILL.md`; `workflows/summarize-clipboard.yaml` | skill/asset | Exact |
| §10.1–10.9 Security | Security layer | `knowledge/references/security.md` | `skills/catlx-security/SKILL.md`; `templates/permissions.yaml` | skill/asset | Adapted (DPAPI/AppContainer/WFP) |
| §11.1–11.7 Telemetry | Tracing/lineage/DuckDB | `knowledge/references/telemetry.md` | `skills/catlx-telemetry/SKILL.md` | skill | Exact |
| §12.1–12.7 Electron shell | Shell/palette/tray/IPC | `knowledge/references/electron-shell.md` | `skills/catlx-electron-shell/SKILL.md` | skill | Adapted (Windows tint) |
| §13.1–13.7 Plugin ecosystem | Plugin runtime/security | `knowledge/references/plugin-ecosystem.md` | `skills/catlx-plugin-ecosystem/SKILL.md`; `templates/plugin-manifest.json` | skill/asset | Exact |
| §14.1–14.7 Docker | Container layer | `knowledge/references/docker.md` | `skills/catlx-docker/SKILL.md`; `templates/docker-compose.fragment.yml` | skill/asset | Adapted (Docker Desktop/WSL2; USB removed) |
| §15.1–15.6 Portability | Portability/identity | `knowledge/references/portability.md` | `skills/catlx-portability/SKILL.md` | skill | Adapted (USB removed) |
| §15.7 USB performance | USB tiering | (removed) | n/a | — | **Removed (scope)** |
| §16.1–16.5 Recovery | Recovery matrix | `knowledge/references/recovery.md` | `skills/catlx-recovery/SKILL.md` | skill | Exact |
| §17.1 Component tree | Module hierarchy | `knowledge/references/component-tree.md` | `INDEX.md`; `skills/*/SKILL.md` | reference | Exact |
| §17.2 Folder structure | Runtime layout | `knowledge/references/folder-structure.md` | `knowledge/references/folder-structure.md` (header notes) | reference | Adapted (Windows launcher.exe) |
| §18.1–18.5 Runtime lifecycle | Boot/voice/workflow/plugin/recovery | `knowledge/references/runtime-lifecycle.md` | `skills/catlx-runtime-lifecycle/SKILL.md` | skill | Exact |
| §19.1–19.5 Roadmap | Forward plan | `knowledge/references/roadmap.md` | (context, not a skill) | reference | Exact (scope=context) |

## Cross-cutting policy (added, not from the source)

- `knowledge/rules/component-lifecycle.md` — the **reuse → install → adapt → create** policy. Derived from the
  ecosystem design requirement (not a CATLX source section). It governs how this skill system obtains missing
  capabilities. Referenced by every skill and the orchestrator. Type: **policy/inferred-structural**.

## Inferred (not sourced, labeled)

- Skill boundaries, dependency edges, delegation targets, registry/manifest/dependency-graph/source-map/coverage
  structure, and the Windows-only/USB-free adaptations. These are **structural/metadata** additions, not
  domain knowledge from the source. They are labeled "Inferred" in each skill body where relevant.

### Universal Orchestrator (meta-skill)

| Generated artifact | Type | Source basis | Status |
|---|---|---|---|
| `skills/catlx-orchestrator/SKILL.md` | skill (orchestrator / router) | Derived meta-skill over the whole canonical system | **Inferred (structural)** — no source-derived domain content |
| `metadata/capability-index.json` | routing core (intent→skill) | Generated from each skill's purpose + source parts it covers | **Inferred (structural)** — capability phrases are derived, not invented domain facts |

The orchestrator and capability index are routing **infrastructure** that reads the canonical
`metadata/skills-registry.json` and `knowledge/`; they are not a second knowledge base.

### Integration: Antigravity last-resort bridge (external, not from the CATLX source)

| Generated artifact | Type | Source basis | Status |
|---|---|---|---|
| `skills/antigravity-last-resort/SKILL.md` | skill (integration / escalation) | **External tool** (Google Antigravity CLI `agy`, headless mode). Not part of the CATLX source document; added as a native escalation layer. | **External (labeled)** — depends on `catlx-ai-provider`, `catlx-capability-routing` |
| `skills/antigravity-last-resort/scripts/ag.py` | wrapper | External CLI wrapper (availability check + `-p --output-format json` headless run + graceful degradation) | External |
| `skills/antigravity-last-resort/knowledge/antigravity-cli.md` | reference | Docs: https://antigravity.google/docs/cli/headless/ | External |
