---
name: catlx-electron-shell
description: "Handles the CATLX Electron OS Shell: an OS-layer interface (not a normal app window), the multi-window window roles (main, HUD overlay, command palette, notification toasts, focus mode), the Ctrl+Space command palette with fuse.js fuzzy search, multi-window persistence, the always-on tray runtime, typed IPC security via contextBridge, and workspace persistence. Use when the user asks about the CATLX shell, windows, HUD, command palette, tray, IPC security, or workspace restoration."
metadata:
  catlx: subsystem
  category: interface
  subsystem: Electron_OS_Shell
  capability: os-shell
  version: "1.0.0"
  source: "PART XII §12.1-12.7"
  aliases: "shell, gui, electron, command palette, tray, hud, windows, workspace persistence"
  depends-on: "catlx-capability-routing, catlx-telemetry"
---

# CATLX — Electron OS Shell

This skill owns the **visual manifestation of the CATLX runtime**: an OS-layer interface that renders at
multiple z-levels and integrates with the OS at the tray, notification, and global-hotkey levels.

> Canonical detail: `../../knowledge/references/electron-shell.md`. Load on demand.

---

## Purpose

Provide the human-facing surface — windows, overlays, palette, tray, notifications — while keeping renderers
separated from Node.js via a secure typed IPC bridge, and persisting workspace state across restarts.

## When to activate

- User asks about the CATLX shell, windows/HUD/palette/tray, or how the GUI works.
- Configuring window roles, the command palette, or workspace persistence.
- Understanding IPC security or shell startup/restore.

## What this skill handles

1. **Desktop shell architecture** — Electron (Chromium + Node.js) with multiple browser windows in distinct
   roles: Main Window (dashboard, workflow manager, memory explorer, settings; resizable; closable to tray),
   HUD Overlay (topmost, transparent, click-through), Command Palette (modal), Notification Toasts
   (taskbar popups), Focus Mode Panel (auto-hiding sidebar).
2. **Command Palette** (Ctrl+Space) — centered search bar with real-time fuzzy search across all commands,
   installed workflows, recent voice commands, open files, settings toggles; powered by a **fuse.js** index
   rebuilt every 30 s.
3. **Multi-window system** — multiple simultaneous Electron windows for multi-monitor productivity; each can
   show a module panel, workflow trace, or memory explorer; persisted across restarts.
4. **Tray runtime** — the last-resort interface; tray process stays active with all windows closed; menu:
   quick commands, subsystem status, open main/palette, emergency controls (stop all workflows, enter safe
   mode, quit).
5. **IPC security** — typed IPC bridge (`contextBridge`); renderers cannot call Node.js APIs directly; only
   validated, main-process-dispatched typed IPC methods; prevents injected renderer JS (e.g. from browser
   automation) from reaching Node.js.
6. **Workspace persistence** — Workspace Serializer runs every 60 s and on shutdown; serializes window layout,
   panels, filters/search, pinned workflows, preferences, and in-progress manual workflows; restores within
   500 ms of first render.

## Requirements / constraints

- **GUI mode by tier** (`cli` / `minimal_hud` / `full_electron`) from the CapabilityMap.
- **R6 (single access point) and R5 (least privilege):** IPC bridge is typed and validated; renderers are
  sandboxed from Node.js.
- Windows Notification Center + tray integration; HUD on T0 is disabled (tray tooltip instead).

## Canonical knowledge it reads

`../../knowledge/references/electron-shell.md` · `../../knowledge/rules/windows-rules.md` ·
`../../knowledge/references/data-registries.md` · `../../knowledge/references/hardware-adaptation.md`.

## Delegation

- **GUI mode / HUD tier** → delegate to `catlx-hardware-adaptation`
  (`skill({ name: "catlx-hardware-adaptation" })`).
- **Observability dashboard panel** → delegate to `catlx-telemetry`
  (`skill({ name: "catlx-telemetry" })`).
- **Memory explorer panel** → delegate to `catlx-memory` (`skill({ name: "catlx-memory" })`).
- **Live GUI events via WebSocket bus** → delegate to `catlx-capability-routing`
  (`skill({ name: "catlx-capability-routing" })`).
- **HUD overlay behavior for desktop control** → delegate to `catlx-desktop-control`
  (`skill({ name: "catlx-desktop-control" })`).

## Edge cases & warnings

- **T0:** GUI dashboard/HUD replaced by CLI/tray tooltip; do not start the full Electron GUI.
- **Full-screen apps:** HUD auto-hides; notifications batch.
- **IPC safety:** never expose arbitrary Node.js APIs through the bridge; inject only validated typed methods.
- **Workspace restore:** use the serializer snapshot; if a snapshot from an abnormal shutdown exists, offer
  restore (see recovery).

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

- **Source:** PART XII §12.1–12.7 (shell as OS-layer interface, desktop shell architecture, command palette,
  multi-window, tray runtime, IPC security, workspace persistence).
- **Inferred/adapted:** Windows tray/notification integration; HUD is Electron (Windows-compatible).
