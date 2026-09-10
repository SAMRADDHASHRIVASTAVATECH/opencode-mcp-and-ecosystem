---
name: catlx-recovery
description: "Handles the CATLX recovery architecture: crash recovery via the PID lockfile, Safe Mode, Recovery Mode, checkpoint integrity verification and restoration, and the full recovery coverage matrix (process crash, power loss, corruption, provider failover, container crash, plugin corruption, OOM, vector index corruption, config corruption). Use when the user asks about CATLX crash recovery, safe mode, recovery mode, restoring a workflow from a checkpoint, or how CATLX recovers from failures."
metadata:
  catlx: subsystem
  category: resilience
  subsystem: Recovery
  capability: recovery
  version: "1.0.0"
  source: "PART XVI §16.1-16.5"
  aliases: "recovery, crash, safe mode, checkpoint restore, resilience, restore, troubleshoot"
  depends-on: "catlx-ai-provider, catlx-memory, catlx-security, catlx-docker"
---

# CATLX — Recovery Architecture

This skill owns **graceful degradation and deterministic recovery**. Recovery is first-class, not a bolt-on.
CATLX must recover from any failure mode — crash, power loss, corrupted DB, failed provider, rogue plugin —
without manual intervention beyond a single voice command or button press.

> Canonical detail: `../../knowledge/references/recovery.md`. Load on demand.

---

## Purpose

Guarantee that any failure leaves the system in a known, recoverable state, with no data loss and minimal
user action.

## When to activate

- User asks how CATLX recovers from a crash, power loss, corruption, or provider/docker/plugin failure.
- Configuring Safe/Recovery Mode, checkpoint restore, or a recovery matrix step.
- Debugging a workflow that won't resume, or a corrupted store.

## What this skill handles

1. **Crash recovery** — check the PID lockfile at `/data/runtime/catlx.pid`; if it exists but the process is
   gone, run: load workspace snapshot → replay WAL journals → find `RUNNING` workflows → evaluate safe resume
   from last checkpoint → present "Found 2 interrupted workflows. Resume them?" → on confirmation resume from
   checkpoints → write new PID lockfile → normal startup.
2. **Safe Mode** — triggered by user request, 3 crashes within 5 minutes, or a security event warranting
   isolation. Only core runtime services; no plugins; no user workflows; no AI provider calls; minimal UI.
3. **Recovery Mode** — start with the last-known-good configuration snapshot; disable plugins that were errored
   or caused the last crash; run a config health check and present results before resuming normal operation.
4. **Checkpoint restoration** — checkpoints are JSON blobs in `workflows.db` (step-output snapshot, DAG state,
   input-parameter hash). The Checkpoint Restorer re-hashes inputs and compares; **if the hash does not match,
   restart from the beginning** rather than resume, to prevent undefined behavior from corrupted state.
5. **Recovery coverage matrix** — process crash, power loss, corrupted SQLite, failed AI provider, container
   crash, corrupted plugin, OOM, corrupted vector index, configuration corruption (full
   table in `../../knowledge/references/recovery.md` §16.5).

## Requirements / constraints

- **R7 (graceful degradation + deterministic recovery).**
- **R4 (WAL + replay):** registers are crash-safe; replay before read.
- Recovery options presented to the user: **Resume / Rollback / Ignore**.

## Canonical knowledge it reads

`../../knowledge/references/recovery.md` · `../../knowledge/references/runtime-lifecycle.md` ·
`../../knowledge/references/data-registries.md` · `../../knowledge/rules/architectural-rules.md`.

## Delegation

- **Workflow checkpoint resume / rollback** → delegate to `catlx-workflow-engine`
  (`skill({ name: "catlx-workflow-engine" })`).
- **Provider failover / queue retry** → delegate to `catlx-ai-provider`
  (`skill({ name: "catlx-ai-provider" })`).
- **Container crash / restart / degradation** → delegate to `catlx-docker`
  (`skill({ name: "catlx-docker" })`).
- **Memory compression / downgrade on OOM** → delegate to `catlx-memory`
  (`skill({ name: "catlx-memory" })`).
- **Safe-mode / security-event isolation** → delegate to `catlx-security`
  (`skill({ name: "catlx-security" })`).

## Edge cases & warnings

- **Checkpoint hash mismatch** — restart from the beginning, never resume corrupted state.
- **Stale PID** — only initiate recovery when the PID is genuinely absent; otherwise treat as running.
- **OOM** — graceful capability downgrade + memory compression, not a hard crash.
- **Corrupted vector index** — rebuild from embedding data in `memory.db`.
- **Corrupted plugin** — disable, notify, offer clean uninstall.

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

- **Source:** PART XVI §16.1–16.5 (recovery philosophy, crash recovery, safe mode, checkpoint restoration,
  recovery coverage matrix).
- **Inferred:** none; the recovery matrix is preserved in full.
