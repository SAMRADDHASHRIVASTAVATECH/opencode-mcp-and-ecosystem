---
name: catlx-hardware-adaptation
description: "Handles CATLX hardware adaptation: hardware tier detection (T0/T1/T2/T3), the capability matrix, the boot-time hardware scan, the Capability Router state machine that emits the CapabilityMap, and runtime re-adaptation when resources change. Use when the user asks about hardware tiers, capability scaling, the 50ms boot scan, CapabilityMap fields, adaptive reconfiguration, or how CATLX picks OCR/STT/TTS/LLM backends per hardware."
metadata:
  catlx: subsystem
  category: architecture
  subsystem: Core_Runtime
  capability: hardware-adaptation
  version: "1.0.0"
  source: "PART II §2.1-2.5"
  aliases: "hardware, hardware adaptation, tier detection, capability matrix, hardware profile, boot scan, adaptive runtime, capability map"
  depends-on: ""
---

# CATLX — Hardware Adaptation

This skill owns the **hardware adaptation** capability: how CATLX detects hardware at boot and derives the
`CapabilityMap` that drives every subsystem. It is the "one CATLX adapts to any machine" behavior.

> Canonical detail lives in `../../knowledge/references/hardware-adaptation.md` and `../../knowledge/references/hardware-adaptation.md`,
> `../../knowledge/references/component-tree.md`, and `../../knowledge/references/folder-structure.md`.
> Load those on demand. This SKILL.md is the operational interface.

---

## Purpose

There is exactly **one** CATLX. The runtime profile engine detects available hardware at boot and
configures every subsystem from a capability matrix derived from that detection. The feature surface is
identical everywhere; capability scales with hardware.

## When to activate

- User references hardware tiers, capability limits, or "runs on any machine."
- User asks how CATLX picks OCR / STT / TTS / LLM / vector / GUI / sandbox backends.
- Configuring or debugging the boot hardware scan or a `CapabilityMap`.
- Runtime re-adaptation when RAM/CPU pressure occurs.

## What this skill handles

1. **Tier classification** (T0/T1/T2/T3) from CPU, cores/threads, RAM, storage class, GPU/VRAM, network.
2. **Capability matrix** — per-tier values for agent count, memory depth, workflow parallelism, telemetry
   sampling, dashboard rendering, OCR, vector search, reasoning depth, TTS, STT, LLM, sandboxing,
   compression. (Full table in `../../knowledge/references/hardware-adaptation.md` §2.3.)
3. **Boot scan procedure** — the ≤ 50 ms scan of CPU, RAM, GPU (DXGI/CUDA), storage (class + sequential
   read speed), network, OS/virtualization; then build a `HardwareProfile` JSON.
4. **Capability Routing Decision Tree** — the deterministic state machine that consumes `HardwareProfile`
   and emits a `CapabilityMap`. Fields: `tier`, `max_concurrent_agents`, `memory_depth_turns`,
   `workflow_parallelism`, `telemetry_sample_rate`, `ocr_backend`, `vector_backend`, `llm_strategy`,
   `tts_engine`, `stt_engine`, `gui_mode`, `plugin_sandbox`. See `../../examples/capability-map.json`.
5. **Runtime re-adaptation** — if RAM < 15% available or CPU > 90% for > 10 s, fire a re-adaptation event;
   all subsystems get a revised `CapabilityMap` within 500 ms; in-flight workflows keep old parameters
   until the current step completes (zero data loss).

## Requirements / constraints

- **R2 (adaptive, never hardcoded):** every subsystem must read config from the Capability Router, not
  from baked-in constants.
- **Windows-only:** GPU enumeration via DirectX/CUDA; storage class detection; WSL2/Docker detection.
  See `../../knowledge/rules/windows-rules.md`.
- The decision logic is **deterministic** — a given `HardwareProfile` always yields the same `CapabilityMap`.

## Canonical knowledge it reads

`../../knowledge/references/hardware-adaptation.md` · `../../knowledge/rules/architectural-rules.md` ·
`../../knowledge/references/component-tree.md` · `../../knowledge/references/folder-structure.md`.

## Delegation (automatic skill invocation)

Follow the root delegation protocol (`catlx` → `skill({ name: "catlx" })` ) when you need a capability you do
not own:

- **Select a specific backend engine / where it runs / fallback chain** → delegate to `catlx-capability-routing`
  (`skill({ name: "catlx-capability-routing" })`). The router decides `LOCAL_PROCESS/SUBPROCESS/CONTAINER/REMOTE`
  and the transparent fallback order.
- **A specific subsystem behavior** (voice STT/TTS tier choices, OCR tier choices, vector/dashboard mode)
  → delegate to the owning subsystem skill (e.g. `catlx-voice-pipeline`, `catlx-screen-understanding`,
  `catlx-telemetry`, `catlx-electron-shell`, `catlx-security`).
- **The component tree or folder layout** → read `../../knowledge/references/component-tree.md`.

## Edge cases & warnings

- T0 with no GPU forces CPU-only OCR/STT/TTS and CLI-only GUI; do not assume a GPU backend is available.
- T3 enterprise: capability map values exceed the T2 table (cluster-scale agent counts, full DAG parallel).
- On re-adaptation, never cancel in-flight workflows; let the current step finish under the old profile.
- Do not fabricate a tier; classify strictly from the scan. If the scan is ambiguous, record the
  uncertainty rather than inventing a tier.

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

- **Source:** PART II §2.1–2.5 (tiers, capability matrix, profiler implementation, decision tree, re-adaptation).
- **Inferred/adapted:** Windows-only GPU enumeration and OS/virtualization detection; the OS-target rows
  restricted to Windows 10/11. No domain content is invented.
