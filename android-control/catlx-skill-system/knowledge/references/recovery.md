# Recovery Architecture — Canonical Reference

> Source: PART XVI — RECOVERY ARCHITECTURE. The single authoritative source for the recovery philosophy,
> crash recovery, safe mode, checkpoint restoration, and the recovery coverage matrix.

## 16.1 Recovery Philosophy
CATLX is an autonomous system that takes real-world actions. Recovery is a first-class design concern, not
a bolt-on feature. Every subsystem is designed for graceful degradation and deterministic recovery from any
failure mode — crash, power loss, corrupted database, failed provider, or rogue plugin — without manual
intervention beyond a single voice command or button press.

## 16.2 Crash Recovery
On startup CATLX checks for a **PID lockfile** at `/data/runtime/catlx.pid`. If the lockfile exists but no
process with that PID is running, a crash recovery sequence is initiated:

1. Load the last workspace snapshot from `/data/snapshots/workspace-latest.json`.
2. Check all databases for WAL journals; replay uncommitted transactions.
3. Check all active workflow records in `workflows.db`; identify any in state `RUNNING`.
4. For each interrupted workflow, evaluate whether it is safe to resume from the last checkpoint.
5. Present the recovery summary to the user: "Found 2 interrupted workflows. Resume them?"
6. On user confirmation (voice or click): resume workflows from checkpoints.
7. Write a new PID lockfile; proceed to normal startup.

## 16.3 Safe Mode
Triggered by: explicit user request, **three consecutive crashes within 5 minutes**, or a security event
that warrants isolation. In Safe Mode: only core runtime services start, no plugins load, no user-defined
workflows run, all AI provider calls are disabled, and the dashboard shows a minimal safe-mode interface.
The user diagnoses and fixes the issue before returning to normal operation.

## 16.4 Checkpoint Restoration
Workflow checkpoints are stored as JSON blobs in `workflows.db`. Each includes: a snapshot of all step
outputs so far, the current DAG execution state (which nodes are complete/pending/running), and a hash of
the input parameters for deterministic replay verification. The **Checkpoint Restorer** validates each
checkpoint's integrity before resuming: it re-hashes the input parameters and compares to the stored hash.
If the hash does not match, the workflow is **restarted from the beginning** rather than resumed, to prevent
undefined behavior from corrupted state.

## 16.5 Recovery Coverage Matrix

| Failure mode | Recovery mechanism |
|---|---|
| CATLX process crash | PID file detection → workspace restore → workflow resume from checkpoint |
| Power loss mid-workflow | WAL journal replay → checkpoint resume |
| Corrupted SQLite database | WAL journal replay → last-known-good snapshot restore from backup |
| Failed AI provider | Provider failover → local model fallback → request queue with retry |
| Docker container crash | Container auto-restart → capability degradation → fallback routing |
| Corrupted plugin | Plugin disabled → user notified → clean uninstall offered |
| Out-of-memory event | Graceful capability downgrade → memory compression triggered |
| Corrupted vector index | ChromaDB index rebuild from embedding data in memory.db |
| Configuration corruption | Roll back to last-known-good configuration snapshot |

## Cross-references
- Consumed by: `skills/catlx-recovery/SKILL.md`.
- Depends on / delegates to: `catlx-workflow-engine` (checkpoint resume), `catlx-ai-provider` (failover), `catlx-docker` (container crash), `catlx-memory` (compression/downgrade), `catlx-security` (safe mode), `catlx-telemetry` (WAL/DUCKDB recovery).
- Full lifecycle: `knowledge/references/runtime-lifecycle.md` (§18.5).
