# Portability Architecture — Canonical Reference

> Source: PART XV — PORTABILITY ARCHITECTURE (Windows-only adaptation; **USB flash-drive scenarios fully
> removed**). The single authoritative source for the portability mandate, relative path architecture,
> runtime portability, database portability, portable external SSD configuration, and cross-machine
> identity.

## 15.1 The Portability Mandate
CATLX must run identically from: the **internal system drive** of a Windows desktop, an **external NVMe
SSD** plugged into a laptop, or any other **Windows** machine — without reinstallation. Portability is a
core architectural constraint that shapes the entire codebase, not an afterthought. (USB flash-drive
examples are intentionally excluded from this conversion.)

## 15.2 Relative Path Architecture
No CATLX code, configuration file, database, or registry entry contains a hardcoded absolute path. All
paths are relative to **`CATLX_ROOT`** — the directory containing the CATLX launcher, determined at
startup from the launcher binary's own path. Moving the CATLX directory to any location on any drive
requires zero reconfiguration.

## 15.3 Runtime Portability
CATLX bundles its own **Node.js runtime** (the Node binary is included in the CATLX package). No global
Node.js installation is required. On Windows, CATLX uses a **portable Node.js distribution**. All npm
dependencies are vendored in `/node_modules/` within the CATLX directory. **No internet connection is
required to start CATLX.**

## 15.4 Database Portability
All SQLite databases use WAL mode with relative paths. The DuckDB telemetry database uses a path relative
to `CATLX_ROOT`. ChromaDB vector store uses a relative persistence path. There are no registry entries, no
OS-level service installations, and no drivers installed outside the CATLX directory (except GPU drivers,
expected to be present on the host OS).

## 15.5 Portable External SSD Configuration
When CATLX is installed on an external NVMe SSD, the installer runs in **portable mode**, which: sets
Windows drive-letter auto-assignment (assigns a consistent drive letter using the disk serial number via a
lightweight driver shim), writes a **portability manifest** to the drive root, and configures the Electron
shell to start in **tray-only mode** (no taskbar entry) to minimize footprint on guest machines. (USB flash
drive wording is removed.)

## 15.6 Cross-Machine Identity
CATLX uses a machine-agnostic identity model. User identity is established by a **keypair stored in
`/data/identity/`**. The private key never leaves the CATLX directory. All memory, workflow history, and
preferences are tied to this identity, not the host machine. When CATLX is plugged into a new machine, the
user's entire history and configuration is immediately available — the system is truly portable.

## 15.7 (Removed) USB Drive Performance Considerations
> This section is intentionally **omitted** from this Windows-only, USB-free conversion. There is no
> USB-performance-based tiering and no USB storage class detection. The tier is selected by the Hardware
> Profiler from the storage class (HDD / SATA SSD / NVMe) and sequential read speed; see
> `knowledge/references/hardware-adaptation.md`.

## Cross-references
- Consumed by: `skills/catlx-portability/SKILL.md`.
- Depends on / delegates to: `catlx-hardware-adaptation` (storage-tier detection), `catlx-docker` (relocatable volumes), `catlx-memory` (portable memory), `catlx-recovery` (relative-path WAL replay).
- Windows rules: `knowledge/rules/windows-rules.md`.
- Source tree: `knowledge/references/folder-structure.md` (`CATLX_ROOT/`).
