---
name: catlx-portability
description: "Handles CATLX portability: the portability mandate, the CATLX_ROOT relative-path architecture, bundled Node runtime, database portability, portable external NVMe SSD configuration (portable mode), and machine-agnostic identity. USB flash-drive scenarios are excluded. Use when the user asks how CATLX runs identically from an internal drive or external SSD, how paths stay relative, how it's portable across machines, or about cross-machine identity."
metadata:
  catlx: subsystem
  category: architecture
  subsystem: Portability
  capability: portability
  version: "1.0.0"
  source: "PART XV §15.1-15.6 (USB removed)"
  aliases: "portability, portable, portable mode, relative paths, cross-machine, identity"
  depends-on: "catlx-hardware-adaptation"
---

# CATLX — Portability Architecture

This skill owns the **portability constraint**: the same runtime runs identically from the internal system
drive or an external NVMe SSD on any Windows machine, with **zero reconfiguration**. Portability is a core
architectural constraint, not an afterthought. **USB flash-drive scenarios are excluded.**

> Canonical detail: `../../knowledge/references/portability.md`. Load on demand.

---

## Purpose

Ensure moving the CATLX directory to any location on any drive requires no reconfiguration and preserves the
full user state (memory, workflows, preferences) via machine-agnostic identity.

## When to activate

- User asks how CATLX is portable, how paths work, or how it moves between machines.
- Configuring portable mode on an external SSD.
- Troubleshooting a hardcoded/absolute path or a move that broke a registry path.

## What this skill handles

1. **The portability mandate** — identical runtime from the internal drive or an external NVMe SSD on any
   Windows machine, no reinstallation.
2. **Relative path architecture** — no hardcoded absolute OS paths anywhere. All paths relative to
   **`CATLX_ROOT`** (the dir containing the launcher, determined at startup from the launcher's own path).
   Moving the directory requires zero reconfiguration.
3. **Runtime portability** — bundles its own **portable Node.js** binary; no global Node install; all npm deps
   vendored in `node_modules/`; no internet needed to start.
4. **Database portability** — SQLite in WAL mode with relative paths; DuckDB relative to `CATLX_ROOT`;
   ChromaDB relative persistence path; no registry entries, OS service installs, or drivers outside the CATLX
   dir (except GPU drivers expected on the host).
5. **Portable external SSD configuration** — portable-mode installer: consistent drive-letter auto-assignment
   via disk-serial-number driver shim; writes a portability manifest to the drive root; Electron shell starts
   **tray-only** (no taskbar entry) to minimize footprint on guest machines. (USB flash-drive wording removed.)
6. **Cross-machine identity** — identity is a keypair in `/data/identity/`; the private key never leaves CATLX;
   memory, workflows, preferences are tied to identity, not the host machine; plugged into any machine the full
   state is immediately available.

## Requirements / constraints

- **R3 (relative paths)** and **R11 (portability as a hard constraint)**.
- **R12 (machine-agnostic identity).**
- Windows `CATLX_ROOT` detection from `launcher.exe`; portable Node distribution.

## Canonical knowledge it reads

`../../knowledge/references/portability.md` · `../../knowledge/references/folder-structure.md` ·
`../../knowledge/rules/windows-rules.md` · `../../knowledge/rules/architectural-rules.md`.

## Delegation

- **Storage-class tier detection** → delegate to `catlx-hardware-adaptation`
  (`skill({ name: "catlx-hardware-adaptation" })`).
- **Relocatable volumes / portable image registry** → delegate to `catlx-docker`
  (`skill({ name: "catlx-docker" })`).
- **Portable memory stores across machines** → delegate to `catlx-memory`
  (`skill({ name: "catlx-memory" })`).
- **Config/path resolution for registries** → delegate to `catlx-capability-routing`
  (`skill({ name: "catlx-capability-routing" })`).

## Edge cases & warnings

- **No hardcoded paths** — reject any path not relative to `CATLX_ROOT`.
- **Drive-letter changes** — portable mode's serial-number shim keeps a consistent letter on external drives.
- **Missing GPU drivers on a new host** — expected host-side; do not attempt to bundle them.
- **Identity key** — the private key must never leave `/data/identity/`; it is the source of cross-machine
  continuity.
- **USB flash drives** — excluded; portable storage means external NVMe SSD.

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

- **Source:** PART XV §15.1–15.6 (portability mandate, relative path architecture, runtime portability,
  database portability, portable external SSD configuration, cross-machine identity).
- **Deviations (explicit):** §15.7 **USB Drive Performance Considerations is removed**; portable-mode wording
  changed from "external SSD or USB drive" to "external NVMe SSD"; USB drive-letter/flash references removed.
  These are noted as deviations, not silent changes.
