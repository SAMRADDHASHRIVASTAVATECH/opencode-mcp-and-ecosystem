# Hardware Adaptation — Canonical Reference

> Source: PART II — HARDWARE ADAPTATION MODEL (Windows-only adaptation). The single authoritative source
> for tiers, the capability matrix, the boot scan, the Capability Router, and runtime re-adaptation.

## 2.1 Philosophy of One

There is exactly one CATLX. The runtime profile engine detects available hardware at boot and
automatically configures every subsystem according to a capability matrix derived from that detection.
The experience degrades gracefully on constrained hardware and expands fully on powerful hardware —
but the feature surface stays the same.

## 2.2 Hardware Tier Definitions (Windows)

| Parameter | Ultra Low-End (T0) | Mid-Range (T1) | High-End (T2) |
|---|---|---|---|
| CPU example | AMD E2-9000 / Intel Celeron | Ryzen 5 / Core i5 | Ryzen 9 / Core i9 |
| Cores / Threads | 2C / 2T | 6C / 12T | 16C / 32T |
| RAM | 4–8 GB | 16 GB | 32–64 GB |
| Storage | HDD / slow SSD | SATA or NVMe SSD | NVMe SSD |
| GPU | Integrated / None | Integrated or dGPU | RTX Series |
| GPU VRAM | — | 0–4 GB | 8–24+ GB |
| Network | 100 Mbps NIC | Gigabit / Wi-Fi 5 | Gigabit / Wi-Fi 6 |
| OS Target | Windows 10 | Windows 10/11 | Windows 11 |

**Enterprise Tier (T3):** multi-core servers, GPU clusters, Docker Swarm / Kubernetes.

## 2.3 Capability Matrix — Runtime Auto-Configuration

At boot the Hardware Profiler runs a ≤ 50 ms scan, returns a `HardwareProfile`, and the Capability
Router consumes it. Every subsystem reads its configuration from the Capability Router, never from
hardcoded values.

| Capability dimension | T0 | T1 | T2 / T3 |
|---|---|---|---|
| Agent count (concurrent) | 1 agent | 3–5 agents | 10–50+ agents |
| Memory depth (episodic) | Last 200 turns | Last 2,000 turns | Unlimited (vector + graph) |
| Workflow parallelism | Sequential only | 4-way parallel | Full DAG parallel |
| Telemetry sampling | 5% | 25% | 100% full trace |
| Dashboard rendering | Text CLI only | Minimal HUD | Full Electron GUI + HUD |
| OCR engine | Tesseract (CPU only) | Tesseract + cache | Tesseract + GPU / EasyOCR |
| Vector search (HNSW) | In-memory small index | Persistent ChromaDB | Multi-instance ChromaDB cluster |
| Reasoning depth | 1-step direct reply | 3-step chain-of-thought | Multi-agent multi-step |
| TTS engine | pyttsx3 (offline) | pyttsx3 + Coqui TTS | Coqui TTS + XTTS-v2 GPU |
| STT engine | Vosk (tiny model) | Vosk (large model) | Whisper large-v3 / GPU |
| LLM inference | Remote API only | Remote API + small local | Remote + full local LLM |
| Plugin sandboxing | Process isolation | Process + memory quotas | Full Docker container sandbox |
| Memory compression | Aggressive (80% ratio) | Balanced (50% ratio) | Minimal (preservation mode) |

## 2.4 Hardware Profiler Implementation

### 2.4.1 Boot Scan Procedure (Windows)

1. **CPU** — read core count, thread count, base clock, architecture (x86, ARM).
2. **RAM** — total installed, available at boot, swap availability.
3. **GPU** — enumerate via DirectX / CUDA device query (Windows Device Manager / DXGI); record VRAM.
4. **Storage** — detect storage device class (HDD / SATA SSD / NVMe); measure sequential read speed.
5. **Network** — probe interface speed; detect proxy / airgap conditions.
6. **OS** — detect Windows version; check virtualization (Docker / WSL2 / bare metal).
7. **Build `HardwareProfile` JSON**; write to runtime config cache (`config/hardware-profiles/`).

### 2.4.2 Capability Routing Decision Tree

The Capability Router is a deterministic state machine. It consumes the `HardwareProfile` and emits a
`CapabilityMap` — a set of named capability flags and integer parameters consumed by each subsystem at
init time:

```jsonc
{
  "tier": 0 | 1 | 2 | 3,
  "max_concurrent_agents": 1 | 3 | 10,
  "memory_depth_turns": 200 | 2000 | null,       // null = unlimited
  "workflow_parallelism": "sequential" | "limited" | "full",
  "telemetry_sample_rate": 0.05 | 0.25 | 1.0,
  "ocr_backend": "tesseract_cpu" | "tesseract_gpu" | "easyocr",
  "vector_backend": "inmemory" | "chromadb_local" | "chromadb_cluster",
  "llm_strategy": "remote_only" | "remote_primary" | "local_primary",
  "tts_engine": "pyttsx3" | "coqui" | "xtts2",
  "stt_engine": "vosk_tiny" | "vosk_large" | "whisper_large",
  "gui_mode": "cli" | "minimal_hud" | "full_electron",
  "plugin_sandbox": "process" | "quota" | "docker"
}
```

## 2.5 Runtime Re-Adaptation

CATLX monitors hardware continuously. If RAM drops below **15% available** or CPU usage exceeds **90%
for more than 10 seconds**, the Adaptive Runtime Manager fires a re-adaptation event. All subsystems
receive a revised `CapabilityMap` within **500 ms**. In-flight workflows are **not** cancelled — they
continue under old parameters until their current step completes, then adopt the new profile. This
guarantees zero data loss during resource contention.

## Cross-references

- Consumed by: `skills/catlx-hardware-adaptation/SKILL.md`, `skills/catlx-capability-routing/SKILL.md`.
- `CATLX_ROOT`-relative paths: `config/hardware-profiles/`, `/data/registries/modules.db`.
