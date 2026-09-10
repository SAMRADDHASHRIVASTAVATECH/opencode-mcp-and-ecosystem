# CATLX — What It Is, Core Mandates, Architectural Pillars

> Source: Part I — EXECUTIVE OVERVIEW (§1.1–1.3). This is the canonical identity of the system.

## 1.1 What CATLX Is

CATLX is a **voice-first, local-first, adaptive AI Operating System**. It is **not** a chatbot, **not**
an assistant wrapper, **not** a task-specific utility. It is the single intelligent runtime that lives
with the user — present on every machine, adapting to every hardware configuration, providing the same
complete feature set whether running on a dual-core netbook with 4 GB of RAM or a 64-core server with
multiple RTX GPUs.

It draws inspiration from Jarvis, Friday, Ghost, IRIS AI, and combines the capabilities of Open
Interpreter, OpenHands, and OpenClaw-style desktop automation into a single unified runtime, extended
with a full memory architecture, voice processing pipeline, workflow engine, telemetry subsystem, and
an Electron-based OS shell.

## 1.2 Core Design Mandates

| Mandate | Description | Implementation strategy |
|---|---|---|
| **Voice-First** | Every function accessible by voice command without keyboard interaction | Dedicated speech pipeline with local fallback |
| **Local-First** | Data, models, and processing prefer local resources | File-backed registries, local LLM support, offline mode |
| **Adaptive Runtime** | Automatically reconfigures from hardware capabilities | Hardware profiler at boot; capability matrix drives all decisions |
| **Portability** | Identical runtime from internal SSD or external (portable) drive | Relative path architecture; no hardcoded OS paths |
| **Modularity** | Every subsystem is a replaceable, isolated module | Plugin architecture with versioned APIs |
| **Replay Safety** | Every workflow can be checkpointed, replayed, and rolled back | DAG engine with persistent state journals |
| **Enterprise Ready** | Multi-user, multi-machine, auditable, secure | Credential vault, permission router, audit logs |
| **Single Edition** | No Lite version; one CATLX, runtime adapts | Hardware tier detection drives capability scaling |

> **Windows adaptation note:** CATLX targets **Windows 10 / Windows 11** as the primary platform in
> this conversion. Linux/macOS-specific mechanisms referenced in the source have been replaced with
> their Windows equivalents (see `knowledge/rules/windows-rules.md`). Portable operation means
> running identically from the internal system drive or an **external NVMe SSD** — USB flash-drive
> scenarios are intentionally excluded.

## 1.3 Architectural Pillars

- **Silexis-Derived Module Runtime** — module extraction, packaging, registry, adaptive capability routing
- **Voice Processing Pipeline** — wake word, transcription, NLU, intent planning, execution
- **Desktop Control Engine** — mouse, keyboard, OCR, window management, browser automation
- **Memory Architecture** — episodic, semantic, workspace, knowledge graph, with coherence protocol
- **Workflow DAG Engine** — scheduling, checkpointing, replay, rollback, recovery
- **AI Provider Router** — multi-provider abstraction with failover and local model support
- **Telemetry System** — distributed tracing, correlation, lineage, DuckDB metrics storage
- **Electron OS Shell** — command palette, HUD overlays, tray runtime, multi-window system
- **Plugin Ecosystem** — sandboxed plugins, hot reload, marketplace-ready SDK
- **Docker Architecture** — portable containers, relocatable volumes, offline mode
- **Security Layer** — credential vault, permission router, capability firewall, audit logs

These eleven pillars are what the skill ecosystem implements. Each pillar maps to one or more skills;
see `INDEX.md`.
