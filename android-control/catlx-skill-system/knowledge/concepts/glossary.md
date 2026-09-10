# CATLX — Canonical Glossary

> Authoritative terminology. One definition per concept. Every skill and reference in this system
> uses these terms exactly as defined here. Do not invent alternative meanings.

## Core system

- **CATLX** — the single voice-first, local-first, adaptive AI Operating System. Not a chatbot, not a
  assistant wrapper, not a task utility. One intelligent runtime present on every machine.
- **CATLX_ROOT** — the directory containing the CATLX launcher. Determined at startup from the
  launcher binary's own path. **No absolute OS paths are ever hardcoded**; all paths are relative to
  `CATLX_ROOT`.
- **Single Edition** — there is exactly one CATLX (no Lite / portable / enterprise tiers). The runtime
  adapts to hardware via capability detection. The feature surface is identical on every machine.

## Hardware & capability

- **HardwareProfile** — the JSON object emitted by the Hardware Profiler after the boot scan.
  Contains CPU, RAM, GPU/VRAM, storage class + sequential read speed, network, OS, and
  virtualization facts. Cached to `config/hardware-profiles/`.
- **CapabilityMap** — the set of named capability flags and integer parameters emitted by the
  Capability Router, consumed by every subsystem at init time. Example fields: `tier`,
  `max_concurrent_agents`, `memory_depth_turns`, `workflow_parallelism`, `telemetry_sample_rate`,
  `ocr_backend`, `vector_backend`, `llm_strategy`, `tts_engine`, `stt_engine`, `gui_mode`,
  `plugin_sandbox`.
- **Hardware Tier** — `T0` (Ultra Low-End), `T1` (Mid-Range), `T2` (High-End), `T3` (Enterprise).
  Determines capability scaling. T0 ≈ 2C/2T, 4–8 GB RAM, no GPU; T1 ≈ 6C/12T, 16 GB, integrated or
  dGPU; T2 ≈ 16C/32T, 32–64 GB, RTX GPU; T3 = multi-core servers, GPU clusters, Swarm/K8s.
- **Adaptive Runtime Manager** — monitors hardware continuously and fires a **re-adaptation event**
  when RAM < 15% available or CPU > 90% for > 10 s. All subsystems receive a revised CapabilityMap
  within 500 ms. In-flight workflows keep their old parameters until the current step completes.

## SILEXIS module system

- **Module** — a versioned, self-describing unit of logic with a manifest, an API contract, and
  declared resource requirements. The unit of CATLX capability encapsulation.
- **Module Extraction** — the process that watches `/modules/staging`, and when a valid
  `module.manifest.json` appears, runs dependency analysis, interface-contract validation, API-surface
  extraction, and promotion to `/modules/registry`.
- **Module Registry** — a file-backed SQLite DB at `/data/registries/modules.db`. Records each
  installed module, its version history, declared capabilities, runtime state, and dependency graph.
  Exposes a REST API on `localhost:7700`.
- **Capability token** — a string like `catlx.core.memory.episodic` identifying a declarable capability.

## Execution environments

- **LOCAL_PROCESS** — Node.js worker thread in the main process (T0; all tiers for fast/light modules).
- **LOCAL_SUBPROCESS** — isolated OS subprocess with an IPC pipe (T1+; native bindings or CPU load).
- **LOCAL_CONTAINER** — Docker container managed by Compose (T2+; heavy ML/GPU workloads).
- **REMOTE_API** — HTTP call to an external AI provider (all tiers; when local model unavailable).
- **Capability Routing** — the mechanism that ensures every request is served by the best available
  capability for the current hardware state, falling back transparently down a priority chain when the
  best module is unavailable.

## Voice pipeline

- **Wake Word** — the always-on trigger (default `Hey CATLX`), OpenWakeWord/Porcupine, 1–3% CPU on T0.
- **IntentObject** — structured result from NLU: `{action_type, entities, confidence, ambiguity_flags,
  suggested_plan}`.
- **ExecutionPlan** — a DAG of atomic steps converted from a confirmed IntentObject, with resource
  requirements, estimated duration, and fallback paths.
- **Conversational Context Window** — the persistent last-N-turns context injected into every NLU call.
- **VAD** — Voice Activity Detector; end-of-utterance silence default 800 ms.

## Memory

- **Episodic Record** — timestamped record of an interaction: timestamp, voice transcript, intent
  resolved, actions, workflow IDs, success/failure, feedback signal, and a 1536-dim embedding vector.
- **Memory Broker** — the single access point for all memory operations. Handles write routing, read
  routing, coherence enforcement, and compression scheduling. No module touches stores directly.
- **Coherence Protocol** — conflict-resolution hierarchy: (1) user-confirmed facts highest, then
  (2) most-recently-written supersede older, then (3) higher-confidence supersede lower. Unresolvable
  conflicts surface as Memory Conflict alerts.
- **RAG** — Retrieval Augmented Generation. Before every LLM call the Broker does a fast retrieval
  pass (top-k vector search k=10 + exact SQL for recent records + knowledge-graph 2-hop expansion).

## AI providers

- **Provider Abstraction Layer (PAL)** — a uniform interface normalizing requests/responses across
  providers. Exposes `ProviderClient` methods: `complete()`, `streamComplete()`, `embed()`,
  `transcribe()`, `synthesize()`. Callers never know which provider serves a request.
- **Provider Router / Failover** — picks the best provider per request type and latency requirement;
  on timeout/error marks the provider degraded (30 s cooldown) and moves to the next in the priority
  list, then to the best local model (T1+), then queues with user notification (T0).
- **Cost Optimization Router** — for non-latency-critical tasks, selects the cheapest provider tier
  meeting quality. Fast models (e.g. Groq Llama 3 8B) for classification/extraction; large models
  (Gemini Pro) for complex reasoning/code/multi-step planning.

## Workflow

- **Workflow Engine (WFE)** — the execution core. Every action is a **Direct Acyclic Graph (DAG)** of
  atomic steps. Provides scheduling, parallel execution, checkpointing, replay, rollback, recovery.
- **Checkpoint** — a record of a completed step (step ID, completion time, output hash, duration) in
  `workflows.db`. Enables resume.
- **Rollback log** — ordered list of inverse operations for completed steps. Executed in reverse on
  failure to restore pre-workflow state.
- **Saga pattern** — compensating transactions for distributed workflows across Docker services.
- **State machine workflow** — named states, transition rules, entry/exit actions, terminal state
  (e.g. voice state machine: Idle → Listening → Processing → Executing → Feedback → Idle).

## Security

- **Credential Vault** — encrypted credential store. On Windows uses DPAPI (tied to the Windows login
  credential). Verifies capability-gated API access. Never plaintext files / env vars in production.
- **Permission Router** — runtime enforcement of the capability model. Verifies each module's declared
  capabilities against a user-approved grant in `permissions.db` at load and at runtime.
- **Capability Firewall** — process-level enforcement below the Permission Router. On Windows uses
  **AppContainer** and **Windows Filtering Platform** rules; ensures a compromised binary cannot exceed
  its declared permissions.
- **Audit log** — append-only, tamper-evident (HMAC-signed) record of every action in `/data/audit/`.
- **Safe Mode** — core runtime only; no plugins, no user workflows, no AI provider calls.
- **Recovery Mode** — last-known-good configuration; errored/crash-causing plugins disabled; health
  check run before resuming.

## Telemetry

- **Trace ID** — UUID v4 root per voice command / workflow / background task. Every sub-operation
  creates a **Span** with a parent Span ID so the execution tree reconstructs.
- **Causal lineage** — directed graph recording prompt → provider → injected memory context → initiating
  user command, to answer "why did CATLX decide X?".
- **DuckDB** — columnar, zero-dependency, time-series-capable telemetry store at
  `/data/telemetry/telemetry.duckdb`, written in append batches of 100, partitioned by month.

## Shell / plugins / Docker / portability

- **Electron OS Shell** — the OS-layer interface; not a normal app window. Renders at multiple
  z-levels and integrates at the tray, notification, and global-hotkey levels.
- **IPC bridge (contextBridge)** — typed IPC; renderers cannot call Node.js APIs directly.
- **Plugin** — an isolated, versioned, sandboxed, replaceable extension. Signed with the developer's
  private key and verified before load.
- **Docker Compose** — primary deployment config at `/docker/docker-compose.yml`, with a machine-local
  override file. Volume mounts resolve via `CATLX_ROOT` (portable).
- **Portable mode** — installer mode for external SSD/portable drives: writes a portability manifest,
  starts the shell tray-only, bundles its own Node runtime and vendored dependencies.
- **Machine-agnostic identity** — a keypair in `/data/identity/`; private key never leaves CATLX.
  Memory, workflows, and preferences are bound to identity, not the host machine.

## Provenance terms

- **Canonical knowledge** — the authoritative single-source content in `knowledge/`. Skills consume it
  by reference; they do not duplicate it.
- **Skill** — a normal OpenCode-style capability directory containing `SKILL.md`. Independently
  callable and interconnected.
