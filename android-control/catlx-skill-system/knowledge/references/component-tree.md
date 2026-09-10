# Complete Component Tree — Canonical Reference

> Source: PART XVII §17.1 — COMPLETE COMPONENT TREE. The authoritative module-level hierarchy of CATLX.
> Two rows unify into the tree below. This is a structural reference; for behavior see the relevant part
> reference and skill.

```
CATLX RUNTIME
├── Core Runtime
│   ├── Hardware Profiler
│   ├── Capability Router
│   ├── Adaptive Runtime Manager
│   └── Event Bus (WebSocket :7701)
├── Voice Pipeline
│   ├── Wake Word Detector
│   ├── Audio Capture
│   ├── STT Transcriber (Vosk / Whisper)
│   ├── Context Injector
│   ├── NLU Intent Parser
│   ├── Disambiguation Engine
│   ├── Workflow Planner
│   └── TTS Synthesizer (pyttsx3 / Coqui)
├── Desktop Control Engine
│   ├── MouseController
│   ├── KeyboardController
│   ├── WindowManager
│   ├── OCR Engine (Tesseract / EasyOCR)
│   ├── Screen Understanding Layer
│   ├── Browser Automation (Playwright)
│   ├── App Automation (UIAutomation)
│   ├── FileOps Module
│   ├── Multi-Monitor Manager
│   └── Overlay HUD
├── Memory Architecture
│   ├── Memory Broker
│   ├── Episodic Memory Store (SQLite + ChromaDB)
│   ├── Semantic Memory Store
│   ├── Workspace Memory (volatile)
│   ├── Knowledge Graph (kuzu)
│   ├── Memory Compressor
│   └── Coherence Protocol
├── AI Provider Layer
│   ├── Provider Abstraction Layer (PAL)
│   ├── Provider Router
│   ├── Google AI Studio Adapter
│   ├── Groq Adapter
│   ├── Hugging Face Adapter
│   └── Local Model Manager (llama.cpp / vLLM)
├── Workflow Engine
│   ├── DAG Executor
│   ├── Scheduler (immediate / deferred / event / background)
│   ├── Checkpoint Manager
│   ├── Rollback Manager
│   └── State Machine Runner
├── Security Layer
│   ├── Credential Vault
│   ├── Permission Router
│   ├── Capability Firewall
│   ├── Risk Detector
│   └── Audit Log Writer
├── Telemetry System
│   ├── Trace Collector
│   ├── Metrics Collector
│   ├── Causal Lineage Recorder
│   ├── Profiler
│   └── DuckDB Store
├── Electron OS Shell
│   ├── Main Window
│   ├── HUD Overlay
│   ├── Command Palette
│   ├── Tray Runtime
│   ├── IPC Bridge
│   └── Workspace Serializer
├── Plugin Runtime
│   ├── Plugin Loader
│   ├── Plugin Sandbox
│   ├── Plugin API Proxy
│   ├── Marketplace Client
│   └── Hot Reload Watcher
├── SILEXIS Module System
│   ├── Module Extractor
│   ├── Module Analyzer
│   ├── Module Builder
│   ├── Module Packager
│   └── Module Registry (SQLite :7700)
└── Docker Layer (T2+)
    ├── Docker Compose Orchestrator
    ├── Container Health Monitor
    ├── Portable Image Registry
    └── Volume Path Resolver
```

## Skill → component mapping (for routing)

| Subsystem | Primary skill(s) |
|---|---|
| Core Runtime / hardware | `catlx-hardware-adaptation`, `catlx-capability-routing` |
| Voice Pipeline | `catlx-voice-pipeline` |
| Desktop Control Engine | `catlx-desktop-control`, `catlx-screen-understanding` |
| Memory Architecture | `catlx-memory` |
| AI Provider Layer | `catlx-ai-provider` |
| Workflow Engine | `catlx-workflow-engine` |
| Security Layer | `catlx-security` |
| Telemetry System | `catlx-telemetry` |
| Electron OS Shell | `catlx-electron-shell` |
| Plugin Runtime | `catlx-plugin-ecosystem` |
| SILEXIS Module System | `catlx-silexis-modules` |
| Docker Layer | `catlx-docker` |
| Cross-cutting | `catlx-portability`, `catlx-recovery`, `catlx-runtime-lifecycle` |
