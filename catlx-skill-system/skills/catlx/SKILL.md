---
name: catlx
description: "ROOT gateway for the CATLX Universal AI Operating System skill ecosystem. Load this first for any task about CATLX architecture, design, runtime, or deployment. It routes to the correct subsystem skill, drives automatic skill-to-skill delegation, and enforces progressive context loading. Use proactively when the user references CATLX, an AI OS, voice-first automation, hardware adaptation, memory architecture, workflow engine, security, or any of its subsystem capabilities."
metadata:
  catlx: skill-system-root
  category: gateway
  subsystem: CATLX_RUNTIME
  version: "1.0.0"
  source: CATLX_Master_Architecture_Specification (all parts)
  skill-type: router
  aliases: "catlx, catlx os, root, entry point, gateway"
  depends-on: all subsystem skills (routed, not eagerly loaded)
---

# CATLX — Skill System (Root Gateway)

You are the entry point to the **CATLX Universal AI Operating System** skill ecosystem. CATLX is a
voice-first, local-first, adaptive AI Operating System (see `../../knowledge/concepts/pillars-and-mandates.md`).
There is exactly **one** CATLX across all hardware; the runtime adapts to capability, not to an edition.

Your job is to **understand the request and route it to the correct subsystem skill**, then let that skill
work. You are a lightweight gateway — you deliberately **do not** hold the full knowledge base. You load
only what the current task needs (progressive loading) and delegate when a capability is required.

> **Windows-only scope.** This conversion targets Windows 10/11 only. USB flash-drive scenarios are
> removed. See `../../knowledge/rules/windows-rules.md`.

---

## System identity

- **What CATLX is:** voice-first, local-first, adaptive AI OS. Combines Open Interpreter, OpenHands, and
  OpenClaw-style desktop automation with a memory architecture, voice pipeline, workflow engine, telemetry
  subsystem, and an Electron OS shell.
- **Core mandates (R-rule set):** Voice-First · Local-First · Adaptive Runtime · Portability · Modularity ·
  Replay Safety · Enterprise Ready · Single Edition. See `../../knowledge/rules/architectural-rules.md`.
- **Eleven architectural pillars:** Silexis module runtime, voice pipeline, desktop control, memory,
  workflow DAG engine, AI provider router, telemetry, Electron shell, plugin ecosystem, Docker, security.

## When to load this skill (routing)

Load this skill for ANY question about CATLX, an AI OS, or any of its subsystems. Use the table below to
route to the correct subsystem skill.

| User intent / capability needed | Route to skill |
|---|---|
| Hardware tiers, capabilities, boot hardware scan, adaptive re-config, CapabilityMap | `catlx-hardware-adaptation` |
| Modules (extraction, packaging, registry), module manifests, SILEXIS | `catlx-silexis-modules` |
| Where/when a module executes (env routing), capability fallback chains | `catlx-capability-routing` |
| Wake word, STT/NLU, intents, planning, TTS, conversation context | `catlx-voice-pipeline` |
| Mouse/keyboard/window/file/browser/app automation, multi-monitor, HUD | `catlx-desktop-control` |
| OCR, screen understanding, ScreenModel | `catlx-screen-understanding` |
| Episodic/semantic/workspace/knowledge-graph memory, Memory Broker, coherence | `catlx-memory` |
| AI providers, PAL, routing/failover, cost router, local LLM | `catlx-ai-provider` |
| Workflow DAG engine, scheduling, checkpoint/replay/rollback, state machines, workflow DSL | `catlx-workflow-engine` |
| Credential vault, DPAPI, permission router, capability firewall, sandbox, audit, risk | `catlx-security` |
| Tracing, metrics, causal lineage, DuckDB, profiling, observability dashboard | `catlx-telemetry` |
| Electron shell, command palette, multi-window, tray, IPC bridge, workspace persistence | `catlx-electron-shell` |
| Plugins, plugin runtime/security/SDK/marketplace, hot reload, dependency resolution | `catlx-plugin-ecosystem` |
| Docker containers, Compose, relocatable volumes, offline mode, Swarm/K8s, Docker recovery | `catlx-docker` |
| Portability, CATLX_ROOT relative paths, bundled Node, external SSD, cross-machine identity | `catlx-portability` |
| Crash recovery, safe mode, checkpoint restoration, recovery matrix | `catlx-recovery` |
| Boot / voice / workflow / plugin / recovery lifecycle sequences | `catlx-runtime-lifecycle` |

## Skill discovery

When you (or any skill) need a capability not present in the current skill, discover it via:

- `../../INDEX.md` (project-level: `../../INDEX.md`) — the global human-readable skill index.
- `../../metadata/skills-registry.json` — machine-readable registry of all skills, capabilities, dependencies.
- `../../DEPENDENCY-GRAPH.md` — dependency and relationship edges.

Every subsystem skill declares in its own body what capabilities it owns, what it references
(`../../knowledge/...`), what it can delegate to, and how to invoke it.

## Delegation protocol (automatic skill-to-skill invocation)

OpenCode invokes skills with the `skill` tool, e.g. `skill({ name: "catlx-workflow-engine" })`, which returns
that skill's SKILL.md as context. Follow this protocol whenever a skill needs a capability it does not own:

1. **Identify the missing capability** precisely (e.g. "I need the workflow DAG scheduler").
2. **Find the best match** in `../../INDEX.md` / `../../metadata/skills-registry.json`; prefer the most specific
   skill over a generic one.
3. **Check the active skill chain** (cycle protection). If the target skill is already active, reuse its
   in-progress result instead of re-invoking. Do not re-enter an active skill.
4. **Invoke** `skill({ name: "<target>" })`, passing the **minimum necessary context** for the subtask only
   — never the whole task.
5. **Incorporate the result**; if the child reports a limitation/failure, decide whether another capability
   is needed or surface the limitation honestly (never silently pretend success).
6. **Respect recursion depth**; return control up the chain so results propagate back to the user.

## Progressive loading rules

- Load only the subsystem skill(s) and the canonical references the current task actually needs.
- Do **not** load every skill or every reference by default. Follow the minimal sufficient dependency chain.
- Do **not** copy canonical content into this root; read `../../knowledge/...` on demand.

## Cross-cutting invariants to enforce

Read `../../knowledge/rules/architectural-rules.md` before making any design decision. Key invariants:
Single Edition; adaptive runtime never hardcoded; relative paths (`CATLX_ROOT`); file-backed SQLite
registries with WAL; least privilege; single access point per concern (Memory Broker, PAL, Capability
Router); graceful degradation + deterministic recovery; replay safety; portability; local-first/offline;
machine-agnostic identity; Windows-first.

## Component lifecycle policy (reuse → install → adapt → create)

**NEVER create a new component as the default.** Before building/creating anything (a sub-skill, dependency,
reference, workflow, helper, adapter, or template), check, in order:
1. **Reuse** an existing local component (resolve aliases/equivalent capabilities first) — reuse, don't rebuild.
2. **Use** an already-registered component from the registry.
3. **Install** a suitable existing, trusted, supported component → validate → register → connect to the graph → use.
4. **Adapt** an existing compatible component via a small persistent adapter/wrapper instead of re-creating it.
5. **Create only as last resort** — then make it permanent immediately: stable id, canonical location, register,
   add to the capability index + dependency graph, add provenance, use, and allow future reuse.
6. Never reorganise/recreate already-generated components (no `Skill X 2` / `new` / `temp` variants); extend the
   existing one. Never create a second competing knowledge source; connect back to the canonical `knowledge/` layer.
   Promote any reusable artifact out of `/tmp`/scratch into the permanent ecosystem.

> Full policy: `../../knowledge/rules/component-lifecycle.md`.

## Source / provenance

- **Source document:** `CATLX_Universal_AI_OS_Specification.pdf` — Master Architecture Specification,
  Version 1.0.0, Architecture Revision A. 60 pages across Parts I–XIX.
- **Provenance:** Each subsystem skill and each `knowledge/references/*.md` file maps to specific source
  parts; see `../../SOURCE-MAP.md` and `../../COVERAGE.md`.
- **Policy:** No domain knowledge is invented. Anything inferred (e.g. Windows-only adaptations, skill
  boundaries, dependencies) is labeled as such. Canonical knowledge lives once, in `knowledge/`.
