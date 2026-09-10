---
name: catlx-runtime-lifecycle
description: "Handles the CATLX runtime lifecycle sequences: the full boot sequence, the detailed voice-command lifecycle, the workflow lifecycle, the plugin lifecycle, and the recovery lifecycle, each as ordered step sequences. Use when the user asks about CATLX startup/boot order, what happens on wake word, how a workflow runs step by step, how a plugin is installed/uninstalled, or the recovery sequence."
metadata:
  catlx: subsystem
  category: lifecycle
  subsystem: Runtime_Lifecycle
  capability: lifecycle-sequences
  version: "1.0.0"
  source: "PART XVIII §18.1-18.5"
  aliases: "lifecycle, boot, startup, runtime sequences, initialize, boot sequence"
  depends-on: "catlx-recovery, catlx-voice-pipeline, catlx-workflow-engine, catlx-plugin-ecosystem, catlx-electron-shell, catlx-security"
---

# CATLX — Runtime Lifecycle Sequences

This skill owns the **ordered end-to-end sequences** that tie the subsystems together: how CATLX boots, how a
voice command flows, how a workflow runs, how a plugin is installed, and how recovery proceeds.

> Canonical detail: `../../knowledge/references/runtime-lifecycle.md`. The voice sequence is also in
> `../../examples/voice-command-lifecycle.md`. Load on demand.

---

## Purpose

Give the exact, ordered step sequences so that no stage is skipped or performed out of order. Use these as the
authoritative procedural truth for orchestrating CATLX behavior.

## When to activate

- User asks about startup/boot order, or "what happens when CATLX starts."
- Tracing a voice command, a workflow run, a plugin install, or a recovery end-to-end.
- Verifying a specific stage (e.g. when the Capability Router runs vs the Memory Broker).

## What this skill handles

1. **Boot sequence** (§18.1) — launcher detects `CATLX_ROOT` → stale-PID check → Hardware Profiler (< 50 ms) →
   Capability Router emits `CapabilityMap` → databases open (WAL replay) → Module Registry scanned in
   dependency order → Event Bus on `:7701` → Security Layer → Memory Broker → AI Provider Layer (health/local
   servers T1+) → Workflow Engine scheduler → Voice Pipeline (wake word + mic) → Plugin Runtime →
   Electron Shell/HUD → write PID lockfile → emit `system.ready` → restore workspace →
   operational.
2. **Voice command lifecycle** (§18.2) — wake word → capture → VAD (800 ms) → STT → context → NLU
   (`IntentObject`, confidence < 0.75 → disambiguate/loop) → Workflow Planner → Permission validation → DAG
   execute → per-step checkpoint + TTS/HUD → completion → Memory Broker writes EpisodicRecord → monitoring.
3. **Workflow lifecycle** (§18.3) — load YAML/dynamic → validate DAG (no cycles, deps present, modules
   available) → create execution context (run ID, input snapshot, rollback log) → schedule → dispatch root
   nodes → per-node module invoke → store output/unlock dependents → on failure retry policy → on FAILED offer
   rollback → on success COMPLETED → emit completion → archive run.
4. **Plugin lifecycle** (§18.4) — package (marketplace/local) → signature verify → manifest parse → capability
   grant review → store grants in `plugins.db` → resolve/vendor deps → build/validate → register → load into
   sandbox → `initialize()` → register capabilities with router → available → update (hot-swap or restart
   flag) → uninstall (`cleanup()`, deregister, destroy sandbox, remove files).
5. **Recovery lifecycle** (§18.5) — crash detected via stale PID → Recovery Mode flag / Safe Mode UI → replay
   WAL → load workspace snapshot → find `RUNNING` workflows → verify checkpoint hash → present Resume/Rollback/
   Ignore → execute chosen action → clear flag → continue boot.

## Requirements / constraints

- **R8 (replay safety):** all lifecycle steps that mutate state are checkpointed.
- **R7 (deterministic recovery):** recovery sequence is deterministic; `Recovery Mode` flag cleared only when
  complete.
- Windows-first paths and mechanisms apply throughout (see `../../knowledge/rules/windows-rules.md`).

## Canonical knowledge it reads

`../../knowledge/references/runtime-lifecycle.md` · `../../knowledge/references/recovery.md` ·
`../../knowledge/references/workflow-engine.md` · `../../knowledge/references/voice-pipeline.md` ·
`../../knowledge/references/plugin-ecosystem.md` · `../../knowledge/references/data-registries.md`.

## Delegation

Because these sequences cross subsystems, delegate to the owning skill when a specific stage needs detail:
`catlx-voice-pipeline`, `catlx-workflow-engine`, `catlx-plugin-ecosystem`, `catlx-electron-shell`,
`catlx-security`, `catlx-recovery`, `catlx-hardware-adaptation`, `catlx-capability-routing`. Use
`skill({ name: "<target>" })` and pass the specific stage as the minimum context.

## Edge cases & warnings

- **Boot ordering:** the Capability Router must emit the CapabilityMap before any subsystem initializes.
- **Stale PID:** a genuine crash triggers recovery; a live PID must not be treated as stale.
- **Confidence loop:** NLU must loop on disambiguation only while confidence < threshold; avoid infinite loops
  (cap the number of clarification turns).
- **Plugin/unit ordering at boot:** modules and plugins load in dependency order.

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

- **Source:** PART XVIII §18.1–18.5 (boot, voice command lifecycle detailed, workflow lifecycle, plugin
  lifecycle, recovery lifecycle).
- **Inferred:** none; sequences preserved as ordered steps.
