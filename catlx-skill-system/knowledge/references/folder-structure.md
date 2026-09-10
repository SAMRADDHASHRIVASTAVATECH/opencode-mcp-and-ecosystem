# Complete Folder Structure — Canonical Reference

> Source: PART XVII §17.2 — COMPLETE FOLDER STRUCTURE (Windows-only). All paths are relative to
> `CATLX_ROOT`. This is the canonical directory layout for the CATLX runtime. Later in section B, the
> generated skill-system layout is also given.

## A. CATLX runtime folder structure

```
CATLX_ROOT/
├── launcher.exe                  # Windows entry point; detects CATLX_ROOT
├── catlx-core/                   # Core runtime (Node.js)
│   ├── index.js
│   ├── hardware-profiler/
│   ├── capability-router/
│   ├── event-bus/
│   └── adaptive-runtime/
├── voice/                        # Voice pipeline modules
│   ├── wake-word/
│   ├── stt/                      # Vosk, Whisper
│   ├── nlu/
│   ├── tts/                      # pyttsx3, Coqui, XTTS
│   └── disambiguation/
├── desktop-control/              # DCE modules
│   ├── mouse/
│   ├── keyboard/
│   ├── window-manager/
│   ├── ocr/
│   ├── screen-model/
│   ├── browser/
│   └── fileops/
├── memory/                       # Memory architecture
│   ├── broker/
│   ├── episodic/
│   ├── semantic/
│   ├── workspace/
│   ├── knowledge-graph/
│   └── compressor/
├── ai-providers/                 # AI provider adapters
│   ├── google-ai-studio/
│   ├── groq/
│   ├── huggingface/
│   └── local/                    # llama.cpp, vLLM
├── workflow-engine/              # WFE
│   ├── dag-executor/
│   ├── scheduler/
│   ├── checkpoint/
│   └── rollback/
├── security/
│   ├── credential-vault/
│   ├── permission-router/
│   ├── capability-firewall/
│   └── risk-detector/
├── telemetry/
│   ├── trace-collector/
│   ├── metrics/
│   └── profiler/
├── electron-shell/
│   ├── main/                     # Electron main process
│   ├── renderer/                 # React-based UI
│   ├── hud/
│   ├── command-palette/
│   └── tray/
├── plugins/
│   ├── runtime/
│   ├── sandbox/
│   ├── marketplace/
│   └── installed/                # User-installed plugins
├── modules/
│   ├── staging/                  # Modules awaiting extraction
│   ├── registry/                 # Validated, packaged modules
│   └── installed/                # Active modules
├── workflows/
│   ├── definitions/              # YAML workflow DSL files
│   └── templates/                # Pre-built workflow templates
├── docker/
│   ├── docker-compose.yml
│   ├── docker-compose.override.yml
│   ├── images/                   # Portable image tarballs
│   └── services/                 # Per-service Dockerfiles
├── data/                         # All persistent runtime data
│   ├── registries/               # SQLite databases
│   │   ├── modules.db
│   │   ├── workflows.db
│   │   ├── memory.db
│   │   ├── credentials.db
│   │   ├── plugins.db
│   ├── telemetry/
│   │   └── telemetry.duckdb
│   ├── audit/                    # Append-only audit logs
│   ├── snapshots/                # Workspace snapshots
│   ├── identity/                 # User keypair
│   ├── backups/                  # Daily backup exports
│   └── runtime/
│       └── catlx.pid             # Process lockfile
├── models/                       # Local AI model files
│   ├── vosk/
│   ├── whisper/
│   ├── wake-word/
│   └── llm/                      # GGUF files
├── node_modules/                 # Vendored npm dependencies
├── runtime/
│   └── node.exe / node           # Bundled Node.js binary
└── config/
    ├── capabilities.yaml         # Capability routing rules
    ├── providers.yaml            # AI provider routing policy
    ├── permissions.yaml          # Default permission grants
    └── hardware-profiles/        # Cached HW profile JSONs
```

## B. Generated skill-system layout (this repository)

```
catlx-skill-system/
├── README.md                # Plain product overview
├── SKILL.md                 # ROOT gateway skill (entry/routing/discovery)   -> skills/catlx/SKILL.md
├── INDEX.md                 # Global skill index
├── MANIFEST.md              # Machine-readable manifest
├── DEPENDENCY-GRAPH.md      # Dependency + relationship graph
├── SOURCE-MAP.md            # Source traceability
├── COVERAGE.md              # Coverage matrix
├── skills/
│   ├── catlx/SKILL.md                      (root gateway)
│   ├── catlx-hardware-adaptation/SKILL.md
│   ├── catlx-silexis-modules/SKILL.md
│   ├── catlx-capability-routing/SKILL.md
│   ├── catlx-voice-pipeline/SKILL.md
│   ├── catlx-desktop-control/SKILL.md
│   ├── catlx-screen-understanding/SKILL.md
│   ├── catlx-memory/SKILL.md
│   ├── catlx-ai-provider/SKILL.md
│   ├── catlx-workflow-engine/SKILL.md
│   ├── catlx-security/SKILL.md
│   ├── catlx-telemetry/SKILL.md
│   ├── catlx-electron-shell/SKILL.md
│   ├── catlx-plugin-ecosystem/SKILL.md
│   ├── catlx-docker/SKILL.md
│   ├── catlx-portability/SKILL.md
│   ├── catlx-recovery/SKILL.md
│   └── catlx-runtime-lifecycle/SKILL.md
├── knowledge/               # Canonical source-of-truth layer
│   ├── concepts/
│   ├── rules/
│   └── references/
├── workflows/               # Workflow YAML definitions/templates
├── examples/                # Source-derived examples
├── templates/               # Reusable templates (manifest, policy, DSL)
└── metadata/                # Machine-readable registry/graph data
```
