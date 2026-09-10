# SILEXIS Integration & Capability Routing — Canonical Reference

> Source: PART III — SILEXIS INTEGRATION (§3.1–3.7). The single authoritative source for the module
> lifecycle, module registry, environment routing, capability fallback chains, file-backed registries,
> adaptive runtime evolution, and live GUI synchronization.

## 3.1 SILEXIS Concept

SILEXIS is an OS-level design language defining how intelligent software modules are extracted,
analyzed, built, packaged, registered, routed, and evolved. CATLX adopts the strongest SILEXIS concepts
as **native subsystems**, not bolted-on plugins.

## 3.2 Module Lifecycle — Extraction Through Registry

### 3.2.1 Module Extraction
Every capability is encapsulated in a **Module** — a versioned, self-describing unit of logic with a
manifest, an API contract, and declared resource requirements. The Module Extractor watches
`/modules/staging`. When a new directory appears with a valid `module.manifest.json`, it triggers the
extraction pipeline: **dependency analysis → interface contract validation → API surface extraction →
promotion to `/modules/registry`**.

### 3.2.2 Module Analysis
Before acceptance, the Module Analyzer performs multi-pass static analysis: declared vs actual
dependencies, resource consumption benchmarks under simulated T0/T1/T2 profiles, security surface
analysis (network calls, file access, subprocess invocations), and capability contract completeness.

### 3.2.3 Module Building
The Module Builder compiles each module into a distributable artifact. On **Windows** this produces an
**Electron-compatible CommonJS bundle** plus a native Node addon if native bindings are required. The
build system uses **esbuild** for speed with **Rollup** for final artifact optimization. (On
Linux/Docker the source specifies an OCI-compatible layer — not applicable to this Windows-only build.)

### 3.2.4 Module Packaging
Each module package contains: the compiled bundle, the manifest, a capability declaration file, a
migration script (version upgrades), a rollback script (downgrades), an API schema file (JSON Schema),
and an optional Docker Compose fragment for containerized deployment.

### 3.2.5 Module Registry
File-backed SQLite DB at `/data/registries/modules.db`. Records every installed module, version history,
declared capabilities, runtime state, and dependency graph. Exposes a REST API on **`localhost:7700`**
consumed by the Electron shell, the CLI, and the Plugin Marketplace.

| Registry field | Description |
|---|---|
| `module_id` | Unique namespaced identifier, e.g. `catlx.core.memory.episodic` |
| `version` | Semver string, e.g. `2.4.1` |
| `capabilities` | JSON array of declared capability tokens |
| `dependencies` | Directed dependency list with version constraints |
| `runtime_state` | `active \| suspended \| errored \| updating` |
| `install_path` | Relative path from CATLX root: `/modules/installed/memory.episodic` |
| `checksum` | SHA-256 of package bundle at install time |
| `compatibility_tier` | Minimum hardware tier required: 0 \| 1 \| 2 \| 3 |

## 3.3 Environment Routing

Determines where a module's work executes. Four environments, selected by hardware tier and
module-declared preferences.

| Environment | Description | Trigger | Example modules |
|---|---|---|---|
| `LOCAL_PROCESS` | Node.js worker thread in main process | T0; all tiers for fast, lightweight modules | Intent Parser, Memory Broker |
| `LOCAL_SUBPROCESS` | Isolated OS subprocess with IPC pipe | T1+; native bindings or CPU load | OCR Engine, STT Transcriber |
| `LOCAL_CONTAINER` | Docker container managed by Compose | T2+; heavy ML workloads, GPU access | Whisper STT, Coqui TTS, LLM Server |
| `REMOTE_API` | HTTP call to external AI provider | All tiers; when local model unavailable | Google AI Studio, Groq, HuggingFace |

## 3.4 Runtime Adaptation & Capability Routing

Capability Routing guarantees every request is handled by the best available capability for current
hardware. On a request (e.g. `'transcribe audio'`) the Capability Router queries the CapabilityMap for
the STT strategy, then routes to the appropriate module. If that is unavailable (e.g. Whisper large
needs a GPU that is busy), it falls back to the next-best option transparently.

### 3.4.1 Fallback Chain Example — Speech-to-Text
| Priority | Engine |
|---|---|
| 1 (Best) | Whisper large-v3 on GPU |
| 2 | Whisper medium on CPU |
| 3 | Vosk large model |
| 4 | Vosk small model |
| 5 (Last resort) | Remote API (Google Speech / Groq Whisper) |

## 3.5 File-Backed Registries

All persistent state that must survive crashes and relocations is a SQLite DB in `/data/registries/`.
Registries are never held exclusively in memory. Every write is wrapped in a transaction with a **WAL**
to ensure crash safety. On recovery the WAL is replayed before any subsystem reads. Databases:
`modules.db`, `workflows.db`, `memory.db`, `credentials.db`, `plugins.db`, plus the
DuckDB telemetry store `telemetry.duckdb` (see telemetry reference).

## 3.6 Adaptive Runtime Evolution

CATLX collects performance data on every module invocation. The Adaptive Runtime Evolver analyzes this
nightly (or on demand) and produces configuration recommendations: modules to hot-swap, memory depth
parameters to adjust, workflow parallelism limits to revise. Recommendations appear in the dashboard and
can be applied with a single command or automatically on a schedule.

## 3.7 Live GUI Synchronization

Every runtime-state change is broadcast over a local **WebSocket bus on port `7701`**. The Electron
shell subscribes and updates the GUI in real time — no polling, no full-page refreshes. Each module
state change, memory update, workflow progress step, telemetry event, and voice recognition result
arrives as a typed event and renders within one animation frame (< 16 ms).

## Cross-references
- Consumed by: `skills/catlx-silexis-modules/SKILL.md`, `skills/catlx-capability-routing/SKILL.md`.
- Registry schema template: `templates/module-manifest.json`.
