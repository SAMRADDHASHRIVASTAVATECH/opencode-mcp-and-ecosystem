# CATLX Skill System — Global Skill Index

> This is the global discovery index for the CATLX skill ecosystem. Use it to route a request or a missing
> capability to the correct skill. Skills are loaded by OpenCode via the `skill` tool:
> `skill({ name: "<skill-name>" })`. Each entry lists id, purpose, capabilities, dependencies, delegation
> targets, references (canonical knowledge), and source locations.
> Machine-readable form: `metadata/skills-registry.json`. Dependency edges: `DEPENDENCY-GRAPH.md`.
> Provenance: `SOURCE-MAP.md` · `COVERAGE.md`.

## 1. Entry points

| Skill | Purpose | Invoke when |
|---|---|---|
| **`catlx-orchestrator`** (Universal Mode) | Automatic front door. Understands a natural-language request, routes it to the right subsystem skill from the registry/capability index, then lets that skill auto-delegate recursively and synthesizes the result. Lightweight router; not a knowledge base. | Activate once, then ask in plain English (explain X, fix a problem, why is X failing, what's wrong, deploy/configure, analyze this). Use for any request that doesn't name a skill. |
| **`catlx`** (root, Direct Mode) | Manual entry + router. Routes to the right subsystem; drives automatic delegation and progressive loading. | Any CATLX / AI-OS question, or when the user names a subsystem. |

## 2. Subsystem skills

| Skill | Purpose (capabilities) | Dependencies | Delegation targets | References | Source |
|---|---|---|---|---|---|
| **`catlx-hardware-adaptation`** | Tier detection (T0–T3), capability matrix, boot scan, Capability Router → CapabilityMap, runtime re-adaptation | *(none — foundation)* | `catlx-capability-routing`, `catlx-voice-pipeline`, `catlx-screen-understanding`, `catlx-telemetry`, `catlx-electron-shell`, `catlx-security` | `hardware-adaptation`, `component-tree`, `folder-structure`, `architectural-rules` | Part II §2.1–2.5 |
| **`catlx-silexis-modules`** | Module lifecycle (extraction/analysis/build/packaging), module registry (SQLite, REST :7700), manifests, capability tokens, dependency graph | `catlx-capability-routing` | `catlx-capability-routing`, `catlx-docker`, `catlx-plugin-ecosystem` | `silexis-and-routing`, `folder-structure`, `data-registries` | Part III §3.1–3.2 |
| **`catlx-capability-routing`** | Environment routing (LOCAL_PROCESS/SUBPROCESS/CONTAINER/REMOTE_API), capability fallback chains, adaptive runtime evolution, file-backed registries, live GUI sync (:7701) | `catlx-hardware-adaptation` | `catlx-hardware-adaptation`, `catlx-silexis-modules`, `catlx-docker`, `catlx-electron-shell`, `catlx-plugin-ecosystem` | `silexis-and-routing`, `data-registries`, `hardware-adaptation`, `windows-rules` | Part III §3.3–3.7 |
| **`catlx-voice-pipeline`** | 10-stage voice pipeline, wake word, STT/NLU/intent, disambiguation, continuous context, streamed TTS, lifecycle | `catlx-ai-provider`, `catlx-memory`, `catlx-capability-routing` | `catlx-ai-provider`, `catlx-workflow-engine`, `catlx-memory`, `catlx-capability-routing`, `catlx-desktop-control` | `voice-pipeline`, `runtime-lifecycle`, `hardware-adaptation` | Part IV §4.1–4.6 |
| **`catlx-desktop-control`** | Mouse/keyboard/window/file/browser/app automation, multi-monitor, HUD, notifications | `catlx-electron-shell`, `catlx-security` | `catlx-screen-understanding`, `catlx-security`, `catlx-electron-shell`, `catlx-workflow-engine`, `catlx-capability-routing` | `desktop-control`, `screen-understanding`, `windows-rules`, `security` | Part V §5.1–5.4, 5.6–5.11 |
| **`catlx-screen-understanding`** | OCR backends (tier-scaled), UI element classification/state, spatial extraction, ScreenModel | `catlx-hardware-adaptation`, `catlx-security` | `catlx-hardware-adaptation`, `catlx-capability-routing`, `catlx-desktop-control`, `catlx-security`, `catlx-docker` | `screen-understanding`, `desktop-control`, `hardware-adaptation`, `security` | Part V §5.5 |
| **`catlx-memory`** | Episodic/semantic/workspace/knowledge-graph stores, Memory Broker, coherence protocol, compression, RAG retrieval, long-term persistence | `catlx-ai-provider` | `catlx-ai-provider`, `catlx-workflow-engine`, `catlx-hardware-adaptation`, `catlx-portability` | `memory-architecture`, `data-registries`, `architectural-rules` | Part VII §7.1–7.11 |
| **`catlx-ai-provider`** | PAL, current/future providers, routing & failover protocol, cost router, local LLM (llama.cpp/vLLM, OpenAI-compatible) | `catlx-capability-routing` | `catlx-memory`, `catlx-hardware-adaptation`, `catlx-docker`, `catlx-capability-routing`, `catlx-security` | `ai-provider`, `memory-architecture`, `hardware-adaptation` | Part VIII §8.1–8.5 |
| **`catlx-workflow-engine`** | DAG model, 4 scheduling modes, checkpoint/replay/rollback, recovery & resilience, state machines, YAML DSL | `catlx-capability-routing`, `catlx-ai-provider`, `catlx-memory`, `catlx-security` | `catlx-capability-routing`, `catlx-ai-provider`, `catlx-memory`, `catlx-desktop-control`, `catlx-security`, `catlx-docker`, `catlx-recovery`, `catlx-telemetry` | `workflow-engine`, `runtime-lifecycle`, `data-registries` | Part IX §9.1–9.9 |
| **`catlx-security`** | Least-privilege model, DPAPI credential vault, Windows Credential Manager, permission router, capability firewall (AppContainer/WFP), sandbox, audit logs, risk detection, safe/recovery modes | `catlx-docker` | `catlx-docker`, `catlx-recovery`, `catlx-telemetry`, `catlx-plugin-ecosystem`, `catlx-hardware-adaptation` | `security`, `windows-rules`, `data-registries`, `architectural-rules` | Part X §10.1–10.9 |
| **`catlx-telemetry`** | Distributed tracing/correlation, causal lineage, metrics, DuckDB, profiling, observability dashboard/CLI | *(none — foundation)* | `catlx-electron-shell`, `catlx-ai-provider`, `catlx-workflow-engine`, `catlx-hardware-adaptation` | `telemetry`, `data-registries`, `hardware-adaptation` | Part XI §11.1–11.7 |
| **`catlx-electron-shell`** | OS-layer shell, window roles, command palette (fuse.js), multi-window, tray runtime, IPC security (contextBridge), workspace persistence | `catlx-capability-routing`, `catlx-telemetry` | `catlx-hardware-adaptation`, `catlx-telemetry`, `catlx-memory`, `catlx-capability-routing`, `catlx-desktop-control` | `electron-shell`, `windows-rules`, `data-registries` | Part XII §12.1–12.7 |
| **`catlx-plugin-ecosystem`** | Plugin runtime, signed security + capability grants, @catlx/plugin-sdk, marketplace, hot reload, PnP-style dependency resolution + API shims | `catlx-silexis-modules`, `catlx-security`, `catlx-electron-shell`, `catlx-docker` | `catlx-security`, `catlx-silexis-modules`, `catlx-electron-shell`, `catlx-docker`, `catlx-capability-routing` | `plugin-ecosystem`, `security`, `folder-structure`, `data-registries` | Part XIII §13.1–13.7 |
| **`catlx-docker`** | Container strategy, core service containers, Compose + overrides, relocatable volumes (CATLX_ROOT), offline mode, Swarm/K8s, Docker recovery | `catlx-hardware-adaptation` | `catlx-capability-routing`, `catlx-recovery`, `catlx-portability`, `catlx-security`, `catlx-silexis-modules` | `docker`, `windows-rules`, `portability`, `data-registries` | Part XIV §14.1–14.7 |
| **`catlx-portability`** | CATLX_ROOT relative paths, bundled Node, database portability, portable external NVMe SSD config, machine-agnostic identity. USB removed. | `catlx-hardware-adaptation` | `catlx-hardware-adaptation`, `catlx-docker`, `catlx-memory`, `catlx-capability-routing` | `portability`, `folder-structure`, `windows-rules`, `architectural-rules` | Part XV §15.1–15.6 (USB removed) |
| **`catlx-recovery`** | Crash recovery (PID lockfile), safe/recovery modes, checkpoint integrity + restore, recovery coverage matrix | `catlx-ai-provider`, `catlx-memory`, `catlx-security`, `catlx-docker` | `catlx-workflow-engine`, `catlx-ai-provider`, `catlx-docker`, `catlx-memory`, `catlx-security` | `recovery`, `runtime-lifecycle`, `data-registries` | Part XVI §16.1–16.5 |
| **`catlx-runtime-lifecycle`** | Boot, voice, workflow, plugin, recovery sequences (ordered steps) | `catlx-recovery`, `catlx-voice-pipeline`, `catlx-workflow-engine`, `catlx-plugin-ecosystem`, `catlx-electron-shell`, `catlx-security` | `catlx-voice-pipeline`, `catlx-workflow-engine`, `catlx-plugin-ecosystem`, `catlx-electron-shell`, `catlx-security`, `catlx-recovery`, `catlx-hardware-adaptation`, `catlx-capability-routing` | `runtime-lifecycle`, `recovery`, `workflow-engine`, `voice-pipeline`, `plugin-ecosystem` | Part XVIII §18.1–18.5 |
| **`antigravity-last-resort`** *(integration)* | Final escalation bridge — headless Google Antigravity (`agy`) invoked ONLY after the native stack (incl. retries/refinement/verification) is exhausted; validates & integrates the returned result; graceful degradation | `catlx-ai-provider`, `catlx-capability-routing` | *(none — terminal)* | `antigravity-cli` (inside skill) | External tool: Google Antigravity CLI (agy) |

## 3. Canonical knowledge (`knowledge/`)

| Area | Files | Used by |
|---|---|---|
| Concepts | `concepts/glossary.md`, `concepts/pillars-and-mandates.md` | All skills |
| Rules | `rules/architectural-rules.md` (R1–R15), `rules/windows-rules.md`, `rules/component-lifecycle.md` (reuse→install→adapt→create) | All skills; Windows-specific; cross-cutting |
| References | 20 files in `references/` (hardware-adaptation … runtime-lifecycle, + component-tree, folder-structure, data-registries, roadmap) | Skill-specific |

## 4. Workflows, examples, templates

- Workflows: `workflows/summarize-clipboard.yaml` (exact §9.9 DSL example).
- Examples: `examples/capability-map.json`, `examples/screen-model.json`, `examples/stt-fallback-chain.md`,
  `examples/voice-command-lifecycle.md`.
- Templates: `templates/module-manifest.json`, `templates/plugin-manifest.json`, `templates/providers.yaml`,
  `templates/permissions.yaml`, `templates/capabilities.yaml`, `templates/docker-compose.fragment.yml`.

## 4. Deterministic routing for small models

- `metadata/capability-index.json` — **capability index + intent map** (78 intent→skill entries) + per-skill
  capabilities, aliases, dependencies, delegation targets, references, workflows, routing hints. This is the
  deterministic routing core for the orchestrator and for small/2B–3B local models.
- `metadata/skills-registry.json` — canonical registry (ids, capabilities, aliases, `depends_on`, source).
- `metadata/dependency-graph.json` — `depends_on` (acyclic) + `delegates_to` (guarded) edges.

> **Note:** The roadmap (Part XIX, `references/roadmap.md`) is planning **context**, not an executable
> capability; it is classified in `COVERAGE.md` as a "context/scope" item rather than a skill.
