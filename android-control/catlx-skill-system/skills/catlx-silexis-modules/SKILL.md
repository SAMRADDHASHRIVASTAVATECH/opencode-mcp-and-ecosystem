---
name: catlx-silexis-modules
description: "Handles the SILEXIS module system in CATLX: module extraction, analysis, building, packaging, and the file-backed module registry (SQLite, REST on localhost:7700). Covers module manifests, capability declarations, dependency graphs, checksums, and usage across build artifacts. Use when the user asks about modules, the module registry, module lifecycle, manifest/API-contract validation, packaging, or how a capability becomes an independently versioned module."
metadata:
  catlx: subsystem
  category: architecture
  subsystem: SILEXIS_Module_System
  capability: module-lifecycle
  version: "1.0.0"
  source: "PART III §3.1-3.2"
  aliases: "modules, module system, module registry, module lifecycle, silexis, capability tokens, packaging"
  depends-on: "catlx-capability-routing"
---

# CATLX — SILEXIS Module System

This skill owns the **module lifecycle**: how any CATLX capability becomes a versioned, self-describing
Module — extracted, analyzed, built, packaged, and registered. SILEXIS is an OS-level design language
adopted as native CATLX subsystems (not bolted-on plugins).

> Canonical detail: `../../knowledge/references/silexis-and-routing.md` (§3.1–3.2), plus the manifest
> template `../examples` (see `../../templates/module-manifest.json`). Load on demand.

---

## Purpose

Every capability is encapsulated in a **Module**: a versioned, self-describing unit of logic with a
manifest, an API contract, and declared resource requirements. This skill covers the pipeline that takes a
candidate in `/modules/staging` and promotes it into `/modules/registry` and finally `/modules/installed`.

## When to activate

- User asks how CATLX organizes modules, or how a new capability becomes a module.
- Configuring the module registry, manifests, versioning, or dependency graphs.
- Debugging module extraction/analysis/build/packaging.
- Understanding capability tokens (e.g. `catlx.core.memory.episodic`).

## What this skill handles

1. **Module Extraction** — watch `/modules/staging`; on a valid `module.manifest.json`, run dependency
   analysis, interface-contract validation, API-surface extraction, and promotion to `/modules/registry`.
2. **Module Analysis** — multi-pass static analysis: declared vs actual dependencies, resource benchmarks
   under simulated T0/T1/T2, security-surface analysis (network, file, subprocess), capability-contract
   completeness.
3. **Module Building** — compile into a distributable artifact. On **Windows**: an Electron-compatible
   CommonJS bundle (+ native Node addon if native bindings required). Build uses **esbuild** (speed) +
   **Rollup** (final optimization).
4. **Module Packaging** — package contains: compiled bundle, manifest, capability declaration file,
   migration script, rollback script, API schema file (JSON Schema), optional Docker Compose fragment.
5. **Module Registry** — file-backed SQLite at `/data/registries/modules.db`; REST API on `localhost:7700`
   consumed by the Electron shell, CLI, and Plugin Marketplace. Fields: `module_id`, `version`,
   `capabilities`, `dependencies`, `runtime_state`, `install_path`, `checksum`, `compatibility_tier`.

## Registry schema (exact)

| Field | Description |
|---|---|
| `module_id` | `catlx.core.memory.episodic` |
| `version` | Semver `2.4.1` |
| `capabilities` | JSON array of capability tokens |
| `dependencies` | Directed dependency list with version constraints |
| `runtime_state` | `active \| suspended \| errored \| updating` |
| `install_path` | Relative: `/modules/installed/memory.episodic` |
| `checksum` | SHA-256 of package bundle at install time |
| `compatibility_tier` | Min tier: 0 \| 1 \| 2 \| 3 |

## Requirements / constraints

- **R4 (file-backed registries + WAL):** the registry is never held exclusively in memory; writes are
  transactional with a WAL.
- **R9 (modularity):** every subsystem is a replaceable, isolated module.
- Registry writes are crash-safe; on recovery the WAL replays before any read.

## Canonical knowledge it reads

`../../knowledge/references/silexis-and-routing.md` · `../../knowledge/references/folder-structure.md` ·
`../../knowledge/rules/architectural-rules.md` · `../../knowledge/references/data-registries.md`.

## Delegation

- **Where/when a module runs + fallback** → delegate to `catlx-capability-routing`
  (`skill({ name: "catlx-capability-routing" })`).
- **Docker-hosted modules/containers** → delegate to `catlx-docker`
  (`skill({ name: "catlx-docker" })`).
- **Plugin packaging/registry (distinct from modules)** → delegate to `catlx-plugin-ecosystem`
  (`skill({ name: "catlx-plugin-ecosystem" })`).
- **Module registry REST client usage** → note the registry is consumed by `catlx-electron-shell` and
  `catlx-capability-routing`.

## Edge cases & warnings

- A module with an invalid/unsigned package must not be promoted. The analyzer also rejects modules whose
  declared capabilities exceed their real implementation.
- Native Node addons must be built for the target Windows architecture; a mismatch breaks loading.
- Version constraints enforce the dependency graph; do not relax them silently.
- `runtime_state: errored` modules must be excluded from scheduling until re-validated.

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

- **Source:** PART III §3.1–3.2 (SILEXIS concept, extraction, analysis, building, packaging, registry).
- **Inferred/adapted:** Windows CommonJS + native-addon artifact (Linux/Docker OCI-layer description not
  applied to this Windows-only conversion). The registry schema is preserved exactly.
