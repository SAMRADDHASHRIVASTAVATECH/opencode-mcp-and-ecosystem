# CATLX — Non-Negotiable Architectural Rules

> Source: the cross-cutting constraints that appear throughout Parts I–XIX. A future change to any
> canonical rule must propagate here, not into dozens of skill copies. Skills **reference** these rules.

The following are the invariants the entire CATLX system obeys. If any implementation choice would
violate one of these, the rule wins.

## R1 — Single Edition
There is exactly **one** CATLX. No Lite, no stripped-down portable, no enterprise-only tier. The
runtime detects hardware at boot and configures every subsystem from a capability matrix. The feature
surface is identical everywhere; it degrades gracefully on constrained hardware and expands fully on
powerful hardware.

## R2 — Adaptive runtime, never hardcoded
Every subsystem reads its configuration from the **Capability Router** (the `CapabilityMap`), never
from hardcoded values or baked-in constants. When hardware state changes, the Adaptive Runtime Manager
emits a revised `CapabilityMap` in ≤ 500 ms. In-flight workflows continue under their old parameters
until their current step completes (zero data loss during resource contention).

## R3 — Relative path architecture
No CATLX code, config file, database, or registry entry contains a hardcoded absolute path. All paths
are relative to **`CATLX_ROOT`**, determined at startup from the launcher binary's own path. Moving the
CATLX directory to any location on any drive requires zero reconfiguration.

## R4 — File-backed registries with WAL
All persistent state that must survive crashes and relocations lives in **file-backed SQLite registries**
under `/data/registries/`. Registries are never held exclusively in memory. Every write is wrapped in a
transaction with a Write-Ahead Log (WAL). On recovery, the WAL is replayed before any subsystem reads
from the registry. This applies to `modules.db`, `workflows.db`, `memory.db`, `credentials.db`,
`plugins.db`.

## R5 — Least privilege / capability-gated access
Every module, plugin, and workflow requests **only** the capabilities it actually needs. Declarations
are checked by the Permission Router at load and at runtime. Undeclared capability or credential access
is blocked and logged as a security event. The Capability Firewall enforces this at the OS/process
level (AppContainer + Windows Filtering Platform on Windows).

## R6 — One access point per cross-cutting concern
- **Memory:** no module touches a memory store directly; everything goes through the **Memory Broker**.
- **AI inference:** no application code calls a provider directly; everything goes through the
  **Provider Abstraction Layer (PAL)**.
- **Capability decisions:** no subsystem decides its own capability; everything reads the
  **Capability Router**.

## R7 — Graceful degradation + deterministic recovery
Every subsystem is designed for graceful degradation and deterministic recovery from any failure mode
(crash, power loss, corrupted DB, failed provider, rogue plugin) without manual intervention beyond a
single voice command or button press. See `knowledge/references/recovery.md` and
`knowledge/references/runtime-lifecycle.md`.

## R8 — Replay safety
Every workflow can be checkpointed, replayed, and rolled back. The Workflow Engine persists state
journals so an interrupted run resumes from the last valid checkpoint rather than restarting.

## R9 — Modularity
Every subsystem is a replaceable, isolated module (SILEXIS). Modules are versioned, self-describing
(manifest + API contract + declared resource requirements), and registered in a file-backed registry.

## R10 — Local-first, offline-capable
Data, models, and processing prefer local resources. CATLX is fully functional without internet: remote
AI providers are disabled, local LLM servers serve all inference, the marketplace is browseable from
cached data, and memory/workflow operations continue normally. On network restoration CATLX auto-resumes
remote providers and syncs queued operations.

## R11 — Portability as a hard constraint
CATLX must run identically from the internal system drive or an external NVMe SSD on any Windows
machine without reinstallation. Portability is a core architectural constraint shaping the codebase.
(USB flash-drive scenarios are excluded from this conversion.)

## R12 — Machine-agnostic identity
User identity is a keypair in `/data/identity/`; the private key never leaves the CATLX directory.
Memory, workflow history, and preferences are bound to identity, not the host machine, so the whole
user state is portable across machines.

## R13 — Telemetry stays local
Full observability (tracing, metrics, lineage, profiling) is stored locally. It is never sent to a
remote telemetry endpoint without explicit user opt-in.

## R14 — Single source of truth
The canonical knowledge in this `knowledge/` layer is authoritative. Skills consume it by reference and
do not duplicate it. If a skill and a canonical file disagree, the canonical file wins.

## R15 — Windows-first
This conversion is Windows-only. All OS integration uses Windows mechanisms: DPAPI, Windows Credential
Manager, UIAutomation, SendInput, AppContainer, Windows Filtering Platform, Windows Notification Center,
Docker Desktop with WSL2. See `knowledge/rules/windows-rules.md`.

## R16 — Reuse-first / last-resort creation
The ecosystem never creates a new component as a default. For any missing capability, skill, dependency,
workflow, reference, helper, adapter, or template, it uses the ordered priority **reuse → install → adapt →
create** (see `knowledge/rules/component-lifecycle.md`). Creation is the final option, never the first.
Reusable components are persisted in the permanent ecosystem (not `/tmp`/scratch); registered; connected to
the dependency graph and capability index; given provenance; and reused by future requests. Already-generated
components are extended, not duplicated (`Skill X 2`/`new`/`temp`). No second competing knowledge source is
created — everything connects back to the canonical `knowledge/` layer and the shared graph. This applies to
the Universal Orchestrator and every individual skill, workflow, reference, helper, adapter, and template.
