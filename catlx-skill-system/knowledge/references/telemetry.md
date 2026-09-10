# Telemetry & Observability — Canonical Reference

> Source: PART XI — TELEMETRY & OBSERVABILITY. The single authoritative source for distributed tracing &
> correlation, causal lineage, metrics, DuckDB storage, profiling, and the observability dashboard.

## 11.1 Observability Philosophy
CATLX is an AI system making autonomous decisions. To debug, optimize, and audit it, every action must be
traceable. CATLX implements full observability: distributed tracing, structured metrics, causal lineage,
and profiling — all stored locally, never sent to a remote telemetry endpoint without explicit user
opt-in.

## 11.2 Distributed Tracing & Correlation
Every voice command, workflow execution, and background task is assigned a **root Trace ID (UUID v4)**.
Every sub-operation creates a **Span** with a parent Span ID, allowing the full execution tree to be
reconstructed. Spans record: start time, end time, module name, operation type, input-parameters hash,
output hash, and status (OK / ERROR / TIMEOUT). The **Correlation Engine** links traces across subsystem
boundaries — when the Workflow Engine calls the Memory Broker, which calls the Vector Store, which calls
the AI Provider, the whole chain shares one root Trace ID.

## 11.3 Causal Lineage
For every AI-generated output (text completion, workflow plan, memory extraction) CATLX records causal
lineage: which prompt was sent, which provider responded, which memory context was injected, and which
user command initiated the chain. Stored as a directed graph in the telemetry database to answer "why did
CATLX decide to do X?"

## 11.4 Metrics
The Metrics Collector records quantitative performance data at configurable sample rates (5% on T0; 100%
on T2+):

- Voice pipeline latency per stage (wake word detection, STT, NLU, planning, execution)
- Workflow step durations and retry counts
- Memory operation latency (read, write, embedding, retrieval)
- AI provider latency, tokens used, estimated cost
- System resource usage (CPU, RAM, GPU) per module
- Error rates by module and by workflow type

## 11.5 DuckDB Storage
All telemetry data is stored in a DuckDB database at `/data/telemetry/telemetry.duckdb`. DuckDB is chosen
for: columnar storage (fast analytical queries), zero-dependency deployment (no server process), high
write throughput, and first-class time-series analytical support. Telemetry is written in append batches
of **100 records** to minimize write amplification. The database is **partitioned by month** for easy
archival.

## 11.6 Profiling
The Profiler instruments hot-path code with microsecond-resolution timing using Node.js Performance Hooks
and the V8 sampling profiler. Profiling runs automatically on the **slowest 1% of operations** (sampled
by duration percentile). Reports stored in `/data/telemetry/profiles/` and rendered in the dashboard's
performance view.

## 11.7 Observability Dashboard
The Electron shell includes a built-in observability dashboard (Ctrl+Shift+T or tray menu) rendering: a
live trace waterfall for the last 10 operations, a metrics time-series chart, a causal lineage graph
viewer (Sigma.js force-directed graph), and a structured log viewer with full-text search. On T0 the
dashboard is replaced by a CLI command: `catlx telemetry report`.

## Cross-references
- Consumed by: `skills/catlx-telemetry/SKILL.md`.
- Depends on / delegates to: `catlx-electron-shell` (dashboard), `catlx-ai-provider` (correlation on failover), `catlx-workflow-engine`.
- Data store: `telemetry.duckdb`; see `knowledge/references/data-registries.md`.
- Source tree: `knowledge/references/folder-structure.md` (`telemetry/`).
