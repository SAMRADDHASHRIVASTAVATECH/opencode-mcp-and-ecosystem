# Docker Architecture — Canonical Reference

> Source: PART XIV — DOCKER ARCHITECTURE (Windows-only adaptation: Docker Desktop with WSL2 backend).
> The single authoritative source for container strategy, core service containers, Compose configuration,
> portable/relocatable volumes, offline mode, enterprise orchestration, and Docker recovery.

## 14.1 Container Strategy
CATLX uses Docker as the isolation and deployment layer for heavy ML workloads, enterprise multi-service
deployments, and portable runtime packages. **Docker is not required for T0/T1 operation** — all capabilities
are available without Docker on those tiers. On T2+ hardware (or when Docker Desktop is installed on any
tier), Docker-backed services are automatically preferred for their isolation benefits.

## 14.2 Core Service Containers

| Container name | Description |
|---|---|
| `catlx-core` | Main Node.js runtime process; Electron shell on desktop |
| `catlx-llm-server` | llama.cpp or vLLM inference server; GPU passthrough |
| `catlx-whisper` | Whisper large-v3 STT inference; CUDA-accelerated |
| `catlx-tts` | Coqui TTS / XTTS-v2 synthesis server |
| `catlx-chromadb` | ChromaDB vector store; persistent volume mounted |
| `catlx-browser` | Playwright-controlled browser instance; isolated profile |
| `catlx-ocr` | EasyOCR / PaddleOCR server; GPU passthrough |
| `catlx-telemetry` | DuckDB telemetry aggregator service |

## 14.3 Docker Compose Configuration
Primary deployment config is a Docker Compose file at `/docker/docker-compose.yml`. It defines all service
containers: build contexts, volume mounts, network configuration, GPU resource assignments, health checks,
and restart policies. A companion `docker-compose.override.yml` allows per-machine customization without
modifying the primary configuration.

## 14.4 Portable Containers & Relocatable Volumes
CATLX Docker volumes are designed for portability. All volume mount points use paths relative to the
`CATLX_ROOT` environment variable. When CATLX is moved to a new machine (internal SSD → **external NVMe
SSD**), volume paths resolve correctly. Container images are built with the CATLX image builder, which
embeds a portable image registry; on a machine without internet access CATLX can load its container images
from the portable registry bundled on the external drive. (USB drive wording is removed.)

## 14.5 Offline Mode
CATLX is fully functional without internet. Offline mode triggers automatically when the network health
check fails. In offline mode: remote AI providers are disabled, local LLM servers serve all inference, the
Plugin Marketplace is browseable from cached data only, and all memory and workflow operations continue
normally. When connectivity returns, CATLX auto-resumes remote providers and syncs queued operations.

## 14.6 Enterprise: Docker Swarm & Kubernetes
For T3 enterprise deployments CATLX supports Docker Swarm and Kubernetes. The Swarm manifest distributes
services across nodes — LLM inference and OCR on GPU nodes, core runtime and telemetry on CPU nodes. The
Kubernetes Helm chart provides equivalent functionality with Kubernetes-native health checks, horizontal
pod autoscaling for inference services, and persistent volume claims for data stores.

## 14.7 Docker Recovery
If a container crashes, Docker's restart policy (`restart: unless-stopped`) auto-restarts it. CATLX monitors
container health via the Docker healthcheck API. If a container fails to become healthy within its startup
timeout, CATLX Core marks the associated capability as degraded, routes requests to fallbacks, and surfaces
a **'Service Degraded'** alert. The user can trigger a full container-stack restart from the dashboard or by
voice: "Restart CATLX services."

## Cross-references
- Consumed by: `skills/catlx-docker/SKILL.md`.
- Depends on / delegates to: `catlx-capability-routing` (LOCAL_CONTAINER env + fallback), `catlx-recovery` (Docker crash), `catlx-portability` (relocatable volumes via CATLX_ROOT), `catlx-security` (container sandbox).
- Compose templates: `templates/docker-compose.fragment.yml`.
- Source tree: `knowledge/references/folder-structure.md` (`docker/`).
