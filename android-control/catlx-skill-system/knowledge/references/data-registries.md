# Data Registries & Endpoints — Canonical Reference

> Source: PART III §3.5 (File-Backed Registries), parts VII–XIV, and endpoints across the spec. The
> authoritative list of persistent stores, their formats, their WAL safety, and the local ports/endpoints.
> All paths are relative to `CATLX_ROOT`.

## File-backed registries (`/data/registries/`)

Rule (from `knowledge/rules/architectural-rules.md` R4): registries are SQLite, never held exclusively in
memory, every write in a transaction with a **Write-Ahead Log (WAL)**; the WAL is replayed before any
subsystem reads on recovery.

| Database | Purpose (source section) | Backing store |
|---|---|---|
| `modules.db` | Installed modules, versions, states, capability graph (§3.2.5) | SQLite |
| `workflows.db` | Workflow definitions, DAG structures, run history, checkpoints, rollback log (§9.1–9.9) | SQLite |
| `memory.db` | Episodic and semantic memory entries (§7.3–7.4) | SQLite |
| `credentials.db` | Encrypted credential store (DPAPI on Windows) (§10.2) | SQLite (encrypted) |
| `plugins.db` | Installed plugins, marketplace metadata, capability grants (§13.3) | SQLite |
| `telemetry.duckdb` | DuckDB-format metrics, traces, lineage (§11.5) | DuckDB |
| `permissions.db` | User-approved capability grants (§10.4) | SQLite |
| `workspace-latest.json` | Workspace snapshot for crash recovery (§12.7, §16.2) | JSON in `/data/snapshots/` |

## Local ports & services

| Port / service | Scheme | Consumed by | Source |
|---|---|---|---|
| `localhost:7700` | REST API | Module Registry — Electron shell, CLI, Plugin Marketplace | §3.2.5 |
| `localhost:7701` | WebSocket bus | Live GUI sync — every runtime-state change as a typed event (< 16 ms) | §3.7, §17.1 |
| localhost OpenAI-compatible API | HTTP | Local Model Manager (llama.cpp / vLLM) — drop-in for any remote provider | §8.5 |
| LAN (encrypted) | HTTP + WebSocket | CATLX Mobile companion API (mDNS-discovered; AES-256-GCM) | §6.2 |

## Audit store
`/data/audit/` — append-only audit log, HMAC-signed per installation, 90-day retention (§10.7).

## Identity
`/data/identity/` — user keypair; private key never leaves the CATLX directory (§15.6).

## Runtime state
`/data/runtime/catlx.pid` — process lockfile; used for crash detection (§16.2).

## Model files
`/models/{vosk,whisper,wake-word,llm}` — local AI model files; `llm/` holds GGUF files (§8.5).

## Config (relative, no hardcoded paths)
`/config/capabilities.yaml` (routing rules), `/config/providers.yaml` (AI routing policy),
`/config/permissions.yaml` (default grants), `/config/hardware-profiles/` (cached HW profile JSONs).

## Cross-references
- Consumed by: `skills/catlx-silexis-modules/SKILL.md`, `skills/catlx-capability-routing/SKILL.md`, `skills/catlx-telemetry/SKILL.md`, `skills/catlx-security/SKILL.md`, `skills/catlx-recovery/SKILL.md`, `skills/catlx-portability/SKILL.md`.
