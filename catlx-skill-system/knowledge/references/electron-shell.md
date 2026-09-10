# Electron OS Shell — Canonical Reference

> Source: PART XII — ELECTRON OS SHELL (Windows-only adaptation). The single authoritative source for the
> OS-layer shell, window roles, command palette, multi-window system, tray runtime, IPC security, and
> workspace persistence.

## 12.1 The Shell as an OS-Layer Interface
The CATLX Electron Shell is not a traditional application window. It is an OS-layer interface: a
persistent process that renders components at multiple z-levels (normal windows, always-on-top panels,
transparent overlays) and integrates with the OS at the system tray, notification, and global-hotkey
levels. It is the visual manifestation of the CATLX runtime.

## 12.2 Desktop Shell Architecture
Built on Electron (Chromium + Node.js), structured as multiple browser windows with distinct roles:

| Window type | Description |
|---|---|
| **Main Window** | Full application frame: module dashboard, workflow manager, memory explorer, settings. Resizable; closable to tray. |
| **HUD Overlay** | Always-on-top, transparent, click-through overlay for real-time status indicators. |
| **Command Palette** | Modal overlay triggered by global hotkey (Ctrl+Space); keyboard access to all functions. |
| **Notification Toasts** | Non-interactive popups near the taskbar for completion events. |
| **Focus Mode Panel** | Slim auto-hiding sidebar; shows active task and quick controls. |

## 12.3 Command Palette
Ctrl+Space keyboard-first alternative to voice. Renders as a centered search bar with real-time fuzzy
search across: all CATLX commands, installed workflows, recent voice commands, open files, and settings
toggles. Typing triggers instant filtering; keyboard navigation selects and executes. Powered by a
**fuse.js** fuzzy search index rebuilt every 30 seconds.

## 12.4 Multi-Window System
Supports multiple simultaneous Electron windows for multi-monitor productivity. Each window can display a
different module panel, a live workflow execution trace, or a memory explorer for a specific time range.
Windows are **persisted across restarts**: on shutdown the Workspace Serializer
records open windows, positions, sizes, and displayed content; on startup they are restored to the last
state.

## 12.5 Tray Runtime
The system tray icon is the last-resort interface. Even when all windows are closed, the tray process
remains active, maintaining all runtime services. The tray menu provides: quick access to common commands,
status indicators for all subsystems, the option to open the main window or command palette, and
emergency controls (stop all workflows, enter safe mode, quit completely).

## 12.6 IPC Security
All inter-process communication between Electron renderer processes and the main process uses a **typed
IPC bridge (contextBridge)**. Renderer processes cannot call Node.js APIs directly; they invoke typed IPC
methods validated and dispatched by the main process. This prevents renderer-side JavaScript (including
content injected via browser automation) from accessing the Node.js runtime.

## 12.7 Workspace Persistence
The Workspace Serializer runs every **60 seconds** and on shutdown. It serializes: open window layout,
currently displayed module panels, active filters/search terms, pinned workflows, user preferences, and
the state of any in-progress manual workflow construction. On startup the workspace is restored from this
snapshot within 500 ms of first render.

## Cross-references
- Consumed by: `skills/catlx-electron-shell/SKILL.md`.
- Depends on / delegates to: `catlx-capability-routing` (GUI mode / HUD tier), `catlx-telemetry` (dashboard), `catlx-memory` (memory explorer).
- Windows rules: `knowledge/rules/windows-rules.md` (Windows Notification Center, tray).
- Source tree: `knowledge/references/folder-structure.md` (`electron-shell/`).
