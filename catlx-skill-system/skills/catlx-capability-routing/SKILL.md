---
name: catlx-capability-routing
description: "Handles CATLX capability and environment routing: where a module's work executes (LOCAL_PROCESS, LOCAL_SUBPROCESS, LOCAL_CONTAINER, REMOTE_API), transparent capability fallback chains (e.g. speech-to-text), adaptive runtime evolution, file-backed registries, and live GUI synchronization over the WebSocket bus. Use when the user asks how CATLX picks an execution environment, routes a capability request, falls back when a module is unavailable, or how runtime state syncs to the GUI."
metadata:
  catlx: subsystem
  category: architecture
  subsystem: Core_Runtime
  capability: capability-environment-routing
  version: "1.0.0"
  source: "PART III §3.3-3.7"
  aliases: "capability routing, environment routing, routing, fallback, execution environment, registries, config routing"
  depends-on: "catlx-hardware-adaptation"
---

# CATLX — Capability & Environment Routing

This skill owns **where CATLX executes work** and **how it guarantees the best available capability for the
current hardware**, falling back transparently when the best module is unavailable. It also covers the
file-backed registries that make state crash-safe and the WebSocket bus that keeps the GUI live.

> Canonical detail: `../../knowledge/references/silexis-and-routing.md` (§3.3–3.7),
> `../../knowledge/references/data-registries.md`, `../../knowledge/references/hardware-adaptation.md`.

---

## Purpose

Environment Routing determines where a module's work is executed, and Capability Routing guarantees every
request is served by the best available capability for the current hardware state — falling back to the
next-best option transparently rather than failing.

## When to activate

- User asks which execution environment is used for a module or why a heavy task ran in a container.
- Configuring capabilities.yaml routing rules or a fallback chain.
- Debugging a capability that used a fallback engine (e.g. STT).
- Understanding file-backed registries or live GUI sync.

## What this skill handles

1. **Environment routing** — choose among four execution environments by hardware tier and
   module-declared preference:
   - `LOCAL_PROCESS` — Node.js worker thread (T0; all tiers for fast light modules; e.g. Intent Parser, Memory Broker)
   - `LOCAL_SUBPROCESS` — isolated OS subprocess + IPC pipe (T1+; native bindings/CPU load; e.g. OCR, STT)
   - `LOCAL_CONTAINER` — Docker container under Compose (T2+; heavy ML/GPU; e.g. Whisper STT, Coqui TTS, LLM server)
   - `REMOTE_API` — HTTP call to external provider (all tiers; when local unavailable; e.g. Google AI Studio, Groq, HF)
2. **Capability routing & fallback** — on a capability request (e.g. `transcribe audio`), query the
   CapabilityMap for the strategy, route to the matching module, and fall back to the next-best option when
   the best is unavailable. Preserve the exact STT fallback chain (see `../../examples/stt-fallback-chain.md`).
3. **File-backed registries** — all persistent state is a SQLite DB in `/data/registries/` with WAL (see
   `../../knowledge/references/data-registries.md`): `modules.db`, `workflows.db`, `memory.db`,
   `credentials.db`, `plugins.db` (+ `telemetry.duckdb`).
4. **Adaptive runtime evolution** — nightly (or on-demand) analysis produces config recommendations:
   hot-swap modules, adjust memory-depth parameters, revise workflow-parallelism limits.
5. **Live GUI synchronization** — broadcast every runtime-state change over the WebSocket bus on `:7701`;
   the Electron shell updates within < 16 ms; no polling, no full-page refresh.

## Requirements / constraints

- **R2 (adaptive):** routing decisions come from the CapabilityMap (see `catlx-hardware-adaptation`), never
  hardcoded.
- **R4 (WAL):** registry writes are transactional with a WAL; replayed before reads on recovery.
- Fallback must be **transparent** — the user must not be required to choose an engine.
- Windows-only network/container enforcement via Windows Filtering Platform and Docker Desktop/WSL2.

## Canonical knowledge it reads

`../../knowledge/references/silexis-and-routing.md` · `../../knowledge/references/data-registries.md` ·
`../../knowledge/references/hardware-adaptation.md` · `../../knowledge/rules/windows-rules.md`.

## Delegation

- **Determine tier/capability values** → delegate to `catlx-hardware-adaptation`
  (`skill({ name: "catlx-hardware-adaptation" })`).
- **A module's build/packaging/registry** → delegate to `catlx-silexis-modules`
  (`skill({ name: "catlx-silexis-modules" })`).
- **Container-based environment** → delegate to `catlx-docker` (`skill({ name: "catlx-docker" })`).
- **GUI rendering of live state** → delegate to `catlx-electron-shell`
  (`skill({ name: "catlx-electron-shell" })`); the bus is the source of events.
- **Registering a module's capabilities with the router** (plugin lifecycle) → delegate to
  `catlx-plugin-ecosystem` (`skill({ name: "catlx-plugin-ecosystem" })`).

## Edge cases & warnings

- **Degraded availability:** if a top-tier module is degraded (e.g. GPU busy), fall back to the next
  priority engine — never fail hard if a lower-priority option exists.
- **Offline:** `REMOTE_API` is disabled in offline mode; route to local model servers instead
  (see `catlx-docker` / `catlx-ai-provider`).
- **Air-gap / proxy:** environment routing respects the detected network conditions.
- **Registry integrity:** on recovery the WAL replays before any subsystem reads a registry.

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

- **Source:** PART III §3.3–3.7 (environment routing, runtime adaptation & capability routing, fallback
  chain, file-backed registries, adaptive runtime evolution, live GUI synchronization).
- **Inferred/adapted:** Windows Filtering Platform/Docker Desktop references; no domain content invented.
