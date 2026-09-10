# CATLX Skill System — Coverage Matrix

> Verifies that the entire source document is represented. For each meaningful source block we record the
> source location, semantic purpose, generated destination, artifact type, and coverage status. Any block
> that is not represented is treated as **orphaned knowledge** and repaired. This is the audit for the
> "no major orphaned knowledge" and "full source coverage" requirements.

## Coverage status legend

- **COVERED** — represented in canonical knowledge + a derived skill/reference/workflow.
- **COVERED (context)** — represented as reference/rule but deliberately not a standalone skill (it is not an
  executable capability).
- **COVERED (removed, scoped)** — intentionally excluded per the Windows-only / USB-free requirement; the
  exclusion is documented in SOURCE-MAP.md and the relevant skill.

## Coverage by part

| # | Part / Section | Semantic purpose | Generated destination | Type | Status |
|---|---|---|---|---|---|
| I | §1.1 What CATLX Is | Identity | `knowledge/concepts/pillars-and-mandates.md`; `skills/catlx/SKILL.md` | concept/skill | **COVERED** |
| I | §1.2 Core Design Mandates | 8 mandates | `knowledge/concepts/pillars-and-mandates.md` → `knowledge/rules/architectural-rules.md` | concept/rule | **COVERED** |
| I | §1.3 Architectural Pillars | 11 pillars | `knowledge/concepts/pillars-and-mandates.md`; `INDEX.md` | concept/ref | **COVERED** |
| II | §2.1–2.3 Tiers + capability matrix | Hardware tiers | `knowledge/references/hardware-adaptation.md` → `skills/catlx-hardware-adaptation/SKILL.md` | ref/skill | **COVERED** |
| II | §2.4 Profiler + decision tree | Boot scan, CapabilityMap | `hardware-adaptation.md`; `templates/capabilities.yaml`; `examples/capability-map.json` | ref/asset | **COVERED** |
| II | §2.5 Runtime re-adaptation | Re-adaption | `hardware-adaptation.md`; `architectural-rules.md` (R2) | ref/rule | **COVERED** |
| III | §3.1–3.2 SILEXIS module lifecycle | Module extract/build/registry | `silexis-and-routing.md` → `skills/catlx-silexis-modules/SKILL.md`; `templates/module-manifest.json` | ref/skill/asset | **COVERED** |
| III | §3.3 Environment routing | 4 exec envs | `silexis-and-routing.md` → `skills/catlx-capability-routing/SKILL.md`; `templates/capabilities.yaml` | ref/skill/asset | **COVERED** |
| III | §3.4 Capability routing + fallback | Routing + STT chain | `silexis-and-routing.md`; `examples/stt-fallback-chain.md` | ref/asset | **COVERED** |
| III | §3.5 File-backed registries | Registries + WAL | `silexis-and-routing.md`; `data-registries.md`; `architectural-rules.md` (R4) | ref/rule | **COVERED** |
| III | §3.6–3.7 Evolution + GUI sync | Recommendations, WS bus | `silexis-and-routing.md` → `skills/catlx-capability-routing/SKILL.md` | ref/skill | **COVERED** |
| IV | §4.1–4.2 Voice pipeline | 10 stages | `voice-pipeline.md` → `skills/catlx-voice-pipeline/SKILL.md` | ref/skill | **COVERED** |
| IV | §4.3–4.5 Wake word/context/streaming | UW, context, TTS | `voice-pipeline.md` → `skills/catlx-voice-pipeline/SKILL.md` | ref/skill | **COVERED** |
| IV | §4.6 Voice lifecycle | Lifecycle | `voice-pipeline.md`; `examples/voice-command-lifecycle.md`; `runtime-lifecycle.md` | ref/example | **COVERED** |
| V | §5.1–5.4 DCE overview/mouse/keyboard/window | DCE | `desktop-control.md` → `skills/catlx-desktop-control/SKILL.md` | ref/skill | **COVERED** |
| V | §5.5 OCR + Screen understanding | OCR/ScreenModel | `screen-understanding.md` → `skills/catlx-screen-understanding/SKILL.md`; `examples/screen-model.json` | ref/skill/asset | **COVERED** |
| V | §5.6–5.11 Browser/app/file/monitor/HUD/notifications | DCE + shell | `desktop-control.md` → `skills/catlx-desktop-control/SKILL.md` | ref/skill | **COVERED** |
| VI | §6.1–6.4 Phone philosophy, Android app, iOS, transports | Phone integration | n/a | — | **REMOVED** — skill `catlx-phone-integration` deleted by user request; not covered |
| VII | §7.1–7.11 Memory architecture | Memory stores/broker/RAG | `memory-architecture.md` → `skills/catlx-memory/SKILL.md` | ref/skill | **COVERED** |
| VIII | §8.1–8.5 AI provider | PAL/providers/routing/local | `ai-provider.md` → `skills/catlx-ai-provider/SKILL.md`; `templates/providers.yaml` | ref/skill/asset | **COVERED** |
| IX | §9.1–9.9 Workflow engine | DAG/scheduling/DSL | `workflow-engine.md` → `skills/catlx-workflow-engine/SKILL.md`; `workflows/summarize-clipboard.yaml` | ref/skill/asset | **COVERED** |
| X | §10.1–10.9 Security | Security layer | `security.md` → `skills/catlx-security/SKILL.md`; `templates/permissions.yaml` | ref/skill/asset | **COVERED** |
| XI | §11.1–11.7 Telemetry | Tracing/lineage/DuckDB | `telemetry.md` → `skills/catlx-telemetry/SKILL.md` | ref/skill | **COVERED** |
| XII | §12.1–12.7 Electron shell | Shell/palette/tray/IPC | `electron-shell.md` → `skills/catlx-electron-shell/SKILL.md` | ref/skill | **COVERED** |
| XIII | §13.1–13.7 Plugin ecosystem | Plugin runtime/security | `plugin-ecosystem.md` → `skills/catlx-plugin-ecosystem/SKILL.md`; `templates/plugin-manifest.json` | ref/skill/asset | **COVERED** |
| XIV | §14.1–14.7 Docker | Container layer | `docker.md` → `skills/catlx-docker/SKILL.md` | ref/skill | **COVERED** |
| XV | §15.1–15.6 Portability | Portability/identity | `portability.md` → `skills/catlx-portability/SKILL.md` | ref/skill | **COVERED** |
| XV | §15.7 USB performance | USB tiering | n/a | — | **COVERED (removed, scoped)** — explicitly excluded |
| XVI | §16.1–16.5 Recovery | Recovery matrix | `recovery.md` → `skills/catlx-recovery/SKILL.md` | ref/skill | **COVERED** |
| XVII | §17.1 Component tree | Module hierarchy | `component-tree.md`; `INDEX.md` | ref | **COVERED** |
| XVII | §17.2 Folder structure | Runtime layout | `folder-structure.md`; `data-registries.md` | ref | **COVERED** |
| XVIII | §18.1–18.5 Runtime lifecycle | Boot/voice/workflow/plugin/recovery | `runtime-lifecycle.md` → `skills/catlx-runtime-lifecycle/SKILL.md` | ref/skill | **COVERED** |
| XIX | §19.1–19.4 Phases | Forward plan | `roadmap.md` | ref | **COVERED (context)** |
| XIX | §19.5 Long-term vision | Vision | `roadmap.md` | ref | **COVERED (context)** |

## Cross-cutting coverage (no orphans)

The following recurring concerns are each addressed canonically (not duplicated per skill):

- **Windows-only adaptation** → `knowledge/rules/windows-rules.md`; referenced by every skill.
- **Architectural invariants (R1–R15)** → `knowledge/rules/architectural-rules.md`.
- **Component lifecycle policy (reuse → install → adapt → create; last-resort creation)** →
  `knowledge/rules/component-lifecycle.md`; referenced by every skill (including the orchestrator) and honored
  in their SKILL.md bodies.
- **Terminology** → `knowledge/concepts/glossary.md`.
- **Ports/endpoints/stores** → `knowledge/references/data-registries.md`.
- **CapabilityMap** → `templates/capabilities.yaml` + `examples/capability-map.json`.
- **Workflow DSL** → `workflows/summarize-clipboard.yaml` + `templates/`.

## Orphaned-knowledge check (per requirement 58–59)

Every meaningful source block maps to at least one generated artifact. The only deliberately orphaned
material is the **USB/phone** content (§6 phone integration, §15.7) which is excluded by explicit scope and
documented in `SOURCE-MAP.md` — this is a scoped exclusion, not accidental loss. The **roadmap**
(§19) is preserved as reference/context, not dropped.

## Orphaned-skill check (per requirement 61)

Every generated skill has a purpose, is reachable from `INDEX.md`/`skills-registry.json`, is independently
callable, and is tied to source knowledge. No dead-end skills were created. The roadmap was deliberately
**not** converted into a skill because it is planning context, not an executable capability.

### Orchestrator coverage note

`catlx-orchestrator` is a **meta-skill** (a router/coordinator). It is reachable from the index/registry, is
independently callable, and routes to all 18 subsystem skills. It intentionally contains **no source-derived
domain knowledge** — it is not a duplicate knowledge base. Its provenance is marked "derived meta-skill /
structural metadata (inferred)" in `SOURCE-MAP.md` and its own SKILL.md. Thus it does not create orphaned
knowledge and does not duplicate canonical content.

### Integration skill: antigravity-last-resort (external, non-source)

`antigravity-last-resort` is an **external integration** skill (Google Antigravity CLI `agy`) added as the
system's final escalation bridge. It is **not** derived from the CATLX source document and is therefore not a
coverage row; it is recorded in `SOURCE-MAP.md` under "Integration: Antigravity last-resort bridge (external)".
It is reachable from `INDEX.md`/`skills-registry.json`, independently callable, registered in the capability
index and dependency graph, and is NOT a duplicate of any source-derived knowledge. Its last-resort policy
lives in `AGENTS.md` and its SKILL.md.
