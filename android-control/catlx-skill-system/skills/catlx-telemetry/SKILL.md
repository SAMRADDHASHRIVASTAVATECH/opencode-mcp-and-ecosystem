---
name: catlx-telemetry
description: "Handles CATLX telemetry and observability: distributed tracing with a root Trace ID and spans, cross-subsystem correlation, causal lineage, the metrics collector, DuckDB storage, profiling, and the observability dashboard (or the catlx telemetry report CLI on T0). Use when the user asks about CATLX logging, tracing, metrics, profiling, observability, the dashboard, 'why did CATLX do X', or how CATLX reconstructs an execution tree."
metadata:
  catlx: subsystem
  category: observability
  subsystem: Telemetry_System
  capability: telemetry-observability
  version: "1.0.0"
  source: "PART XI §11.1-11.7"
  aliases: "telemetry, tracing, metrics, observability, logging, profiling, monitoring, dashboard"
  depends-on: ""
---

# CATLX — Telemetry & Observability

This skill owns the **observability** of an autonomous system. Every action must be traceable to debug,
optimize, and audit it. All telemetry is stored **locally** and only sent externally with explicit opt-in.

> Canonical detail: `../../knowledge/references/telemetry.md`. Load on demand.

---

## Purpose

Give CATLX full, local, queryable visibility into what it did and why — distributed tracing, structured
metrics, causal lineage, and profiling.

## When to activate

- User asks how to trace CATLX activity, view metrics, profile, or see the observability dashboard.
- Debugging "what did CATLX do in response to X" or "why did CATLX decide Y".
- Configuring sampling rate, storage, or the CLI report.

## What this skill handles

1. **Distributed tracing & correlation** — every voice command/workflow/background task gets a root
   **Trace ID (UUID v4)**; each sub-operation creates a **Span** with a parent Span ID. A Span records start
   time, end time, module name, operation type, input-parameters hash, output hash, and status
   (OK/ERROR/TIMEOUT). The **Correlation Engine** links traces across subsystems so the whole chain
   (Workflow → Memory Broker → Vector Store → AI Provider) shares one root Trace ID.
2. **Causal lineage** — for every AI-generated output, record which prompt was sent, which provider responded,
   which memory context was injected, and which user command initiated the chain; stored as a directed graph.
3. **Metrics** — at configurable sample rates (5% T0; 100% T2+): voice pipeline stage latencies, workflow step
   durations/retries, memory op latency, AI provider latency/tokens/cost, system resource usage (CPU/RAM/GPU)
   per module, error rates by module and workflow type.
4. **DuckDB storage** — columnar, zero-dependency, time-series-capable at `/data/telemetry/telemetry.duckdb`;
   writes in append batches of 100; partitioned by month.
5. **Profiling** — instrument hot paths with microsecond timing (Node.js Performance Hooks + V8 sampling
   profiler); auto-profile the slowest 1% of operations; store reports in `/data/telemetry/profiles/`.
6. **Observability dashboard** — Electron shell view (Ctrl+Shift+T or tray): trace waterfall (last 10 ops),
   metrics time-series, causal lineage graph viewer (Sigma.js), structured log viewer with full-text search.
   On T0, replaced by CLI: `catlx telemetry report`.

## Requirements / constraints

- **R13 (telemetry stays local):** never sent to a remote endpoint without explicit opt-in.
- Sampling rate and dashboard mode come from the CapabilityMap (`telemetry_sample_rate`, `gui_mode`).
- All tracing goes through correlation IDs shared across the PAL and Workflow Engine.

## Canonical knowledge it reads

`../../knowledge/references/telemetry.md` · `../../knowledge/references/data-registries.md` ·
`../../knowledge/references/hardware-adaptation.md` · `../../knowledge/rules/architectural-rules.md`.

## Delegation

- **Dashboard / GUI rendering** → delegate to `catlx-electron-shell`
  (`skill({ name: "catlx-electron-shell" })`).
- **Failover correlation** → delegate to `catlx-ai-provider`
  (`skill({ name: "catlx-ai-provider" })`).
- **Workflow run tracing** → delegate to `catlx-workflow-engine`
  (`skill({ name: "catlx-workflow-engine" })`).
- **Profiling/sampling tier** → delegate to `catlx-hardware-adaptation`
  (`skill({ name: "catlx-hardware-adaptation" })`).

## Edge cases & warnings

- **T0:** dashboard unavailable → use the `catlx telemetry report` CLI.
- **Write amplification:** batch telemetry writes (100 records) to minimize amplification.
- **Corruption:** DuckDB/vector stores must be recoverable (see recovery); never silently drop traces.
- **Privacy:** respect opt-in; a metric that could leak sensitive state should be flagged.

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

- **Source:** PART XI §11.1–11.7 (philosophy, tracing & correlation, causal lineage, metrics, DuckDB storage,
  profiling, observability dashboard).
- **Inferred:** none; endpooints/paths mapped to Windows-relative paths.
