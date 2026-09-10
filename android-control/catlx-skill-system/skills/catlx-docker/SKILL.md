---
name: catlx-docker
description: "Handles the CATLX Docker architecture: the container strategy, core service containers, Docker Compose configuration with overrides, portable/relocatable volumes relative to CATLX_ROOT, offline mode, Docker Swarm/Kubernetes for enterprise, and Docker recovery or service degradation. Use when the user asks about CATLX Docker/containers, the Compose file, GPU containers, offline containers, relocatable volumes, Swarm/Kubernetes, or container health/restart."
metadata:
  catlx: subsystem
  category: infrastructure
  subsystem: Docker_Layer
  capability: container-deployment
  version: "1.0.0"
  source: "PART XIV §14.1-14.7"
  aliases: "docker, containers, compose, containerized, gpu containers, swarm, kubernetes"
  depends-on: "catlx-hardware-adaptation"
---

# CATLX — Docker Architecture

This skill owns the **container isolation and deployment layer** for heavy ML workloads, enterprise
multi-service deployments, and portable runtime packages. On Windows this is **Docker Desktop with a WSL2
backend**. Docker is **not required** for T0/T1 operation — all capabilities are available without it there.

> Canonical detail: `../../knowledge/references/docker.md`. Fragment template:
> `../../templates/docker-compose.fragment.yml`. Load on demand.

---

## Purpose

Isolate heavy workloads (LLM, Whisper, TTS, OCR, ChromaDB, browser, telemetry) and deploy CATLX services
portably with relocatable volumes and GPU passthrough.

## When to activate

- User asks how CATLX uses containers, or which services run in containers.
- Writing/reading the Compose file, debugging a container crash/degradation, or offline mode.
- Enterprise deployment (Swarm/Kubernetes).

## What this skill handles

1. **Container strategy** — Docker for heavy ML/enterprise/portable packages; optional for T0/T1; preferred
   on T2+ (or when Docker Desktop is present) for isolation.
2. **Core service containers** — `catlx-core`, `catlx-llm-server`, `catlx-whisper`, `catlx-tts`,
   `catlx-chromadb`, `catlx-browser`, `catlx-ocr`, `catlx-telemetry` (GPU passthrough where relevant).
3. **Docker Compose configuration** — `/docker/docker-compose.yml` defines services, build contexts, volume
   mounts, network config, GPU assignments, health checks, restart policies; `docker-compose.override.yml` for
   per-machine customization.
4. **Portable containers & relocatable volumes** — all volume mount points relative to `CATLX_ROOT`; resolves
   when moved to a new machine (internal → external NVMe SSD); image builder embeds a portable image registry
   so images load without internet.
5. **Offline mode** — triggered automatically on network-health-check failure; remote providers disabled, local
   LLM servers serve all inference, marketplace browseable from cache, memory/workflow continue; on
   reconnection auto-resume + sync queued ops.
6. **Enterprise (Docker Swarm & Kubernetes)** — distribute services across nodes (LLM/OCR on GPU nodes, core/
   telemetry on CPU nodes); Helm chart with Kubernetes-native health checks, HPA for inference, PVCs for data.
7. **Docker recovery** — `restart: unless-stopped`; container health monitoring; failure to become healthy →
   mark capability degraded, route to fallbacks, surface 'Service Degraded'; full stack restart via dashboard
   or voice "Restart CATLX services."

## Requirements / constraints

- **R10 (local-first/offline):** must run fully functional without internet.
- **R5:** containers are the strictest plugin/agent sandbox tier (T2+).
- Windows: Docker Desktop + WSL2 backend; GPU passthrough for CUDA workloads (see `../../knowledge/rules/windows-rules.md`).
- Volumes relative to `CATLX_ROOT` (portability, R3/R11).

## Canonical knowledge it reads

`../../knowledge/references/docker.md` · `../../knowledge/rules/windows-rules.md` ·
`../../knowledge/references/portability.md` · `../../knowledge/references/data-registries.md`.

## Delegation

- **Which tier / container or fallback** → delegate to `catlx-capability-routing`
  (`skill({ name: "catlx-capability-routing" })`).
- **Container crash recovery** → delegate to `catlx-recovery`
  (`skill({ name: "catlx-recovery" })`).
- **Relocatable volume paths / portable registry** → delegate to `catlx-portability`
  (`skill({ name: "catlx-portability" })`).
- **Container sandbox security** → delegate to `catlx-security`
  (`skill({ name: "catlx-security" })`).
- **Containerized modules (SILEXIS packaging)** → delegate to `catlx-silexis-modules`
  (`skill({ name: "catlx-silexis-modules" })`).

## Edge cases & warnings

- **Not required on T0/T1** — do not assume Docker is present; fall back to local process/subprocess.
- **GPU passthrough** — only on GPU-capable hosts; otherwise drop to CPU.
- **Offline** — never depend on remote provider/container registry when offline; use the portable registry +
  local servers.
- **Container health** — a container that never becomes healthy marks the capability degraded and routes to
  fallbacks; surface the alert.

## Component lifecycle policy (reuse → install → adapt → create)

**NEVER create a new component as the default.** Before building/creating anything (a sub-skill, dependency,
reference, workflow, helper, adapter, or template), check, in order:
1. **Reuse** an existing local component (resolve aliases/equivalent capabilities first) — reuse, don't rebuild.
2. **Use** an already-registered component from the registry.
3. **Install** a suitable existing, trusted, supported component → validate → register → connect to the graph → use.
4. **Adapt** an existing compatible component via a small persistent adapter/wrapper instead of re-creating it.
5. **Create only as last resort** — then make it permanent immediately: stable id, canonical location, register,
   add to the capability index + dependency graph, add provenance, use, and allow future reuse.
6. Never reorganise/recreate already-generated components (no `Skill X 2` / `new` / `temp` variants); extend the
   existing one. Never create a second competing knowledge source; connect back to the canonical `knowledge/` layer.
   Promote any reusable artifact out of `/tmp`/scratch into the permanent ecosystem.

> Full policy: `../../knowledge/rules/component-lifecycle.md`.

## Source / provenance

- **Source:** PART XIV §14.1–14.7 (container strategy, core service containers, Compose config, portable
  containers & relocatable volumes, offline mode, Swarm/Kubernetes, Docker recovery).
- **Inferred/adapted:** Windows Docker Desktop + WSL2 backend; USB-drive wording removed from relocatable
  volume/portable-registry discussion (external NVMe SSD only).
