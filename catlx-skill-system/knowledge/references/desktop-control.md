# Desktop Control Engine — Canonical Reference

> Source: PART V — DESKTOP CONTROL ENGINE (Windows-only adaptation). The single authoritative source for
> the mouse/keyboard controllers, window manager, file ops, browser automation, application automation,
> multi-monitor, HUD, and notifications.

## 5.1 Overview

The Desktop Control Engine (DCE) is CATLX's "hands." It lets the AI interact with any application as a
human would: moving the mouse, typing, reading the screen, navigating browser UIs, and managing files.
Implemented as a set of isolated modules exposing a unified **Desktop API** consumed by the Workflow
Engine.

## 5.2 Mouse Control
`MouseController`, backed by **robotjs** on Windows (with nut-js as a cross-platform alternative).
Operations: absolute move, relative move, smooth animated move, left/right/middle click, double-click,
drag, vertical and horizontal scroll. All coordinates are logical pixels normalized to the primary
display resolution. Multi-monitor coordinates are translated automatically.

## 5.3 Keyboard Control
`KeyboardController`. Supports raw key press/release events, text typing (configurable inter-keystroke
delay), hotkey combinations (Ctrl+C, Win+R, etc.), clipboard read/write, and **secure input mode**
(disables logging for password fields). On Windows it uses the **SendInput** API directly for maximum
compatibility.

## 5.4 Window Management
`WindowManager` enumerates open windows via the OS accessibility API (**UIAutomation** on Windows).
Can: list windows (title, process name, geometry), bring to front, move/resize, minimize/maximize/restore,
close, split to left/right halves, move across monitors. Window state is used to infer context (e.g.
"current window is VS Code → interpret code-related commands in that context").

## 5.5 OCR — Screen Understanding
`OCR` module converts screen regions to structured text. **T0:** Tesseract 5.x with `eng+osd` on CPU.
**T1:** adds a result cache to avoid re-OCR of static regions. **T2+:** EasyOCR or PaddleOCR with GPU for
near-instantaneous full-screen extraction. Beyond raw OCR, the **Screen Understanding layer** applies
post-processing: UI element classification (buttons, input fields, labels, links), spatial relationship
extraction, and element state detection (enabled/disabled, checked/unchecked, focused). This produces a
**ScreenModel** — a structured JSON representation of the screen's interactive surface — that the
Workflow Engine uses to make click decisions without hardcoded coordinates.
(Full detail: `knowledge/references/screen-understanding.md` if present, else section above.)

## 5.6 Browser Automation
Runs through **Playwright** (primary) with a **Puppeteer** fallback. Supports Chromium, Firefox, WebKit.
CATLX injects a companion browser extension exposing additional hooks for reading DOM state without OCR
overhead when the browser is a first-party target. Operations: navigate to URL, find/click elements by
CSS selector or accessibility name, fill forms, extract page content, take screenshots, handle
authentication flows, and manage multiple browser contexts (separate cookie/session stores per task).

## 5.7 Application Automation
Hybrid approach for non-browser apps: **UIAutomation** API for apps exposing accessibility trees
(most modern Windows apps); **OCR-based interaction** for legacy apps without accessibility support;
**native COM/WMI** for Microsoft Office (Word, Excel, Outlook) when programmatic access is faster and
more reliable than UI simulation.

## 5.8 File Operations
`FileOps` provides a safe, audited file API: read, write, copy, move, delete, rename, create/list
directory, search by name/content, compress/extract archives. All destructive operations (delete,
overwrite) are logged to the audit trail and optionally require voice confirmation. File operations
respect user-configured **safe zones** — directories from which automated deletion is blocked without an
explicit override.

## 5.9 Multi-Monitor Support
Enumerates all connected displays at boot and on hotplug. Each display has a logical index. All
coordinates are `(display_index, x, y)` tuples. `ScreenCapture` can capture the entire virtual desktop
(all monitors composited) or a single display. OCR and ScreenModel are computed per-display by default
and merged into a global ScreenModel on request.

## 5.10 Overlay HUD
A transparent, click-through Electron window at the highest z-order. Displays: current voice recognition
state, active workflow name and progress bar, pending memory writes, agent status indicators, and
notification toasts. On T0 the HUD is disabled to preserve CPU (status shown in the system tray
tooltip instead). HUD auto-hides in full-screen apps and re-appears on wake word detection.

## 5.11 Notification System
Integrates with the OS native notification system (**Windows Notification Center**). Time-critical
workflow events (completion, error, user input required) surface as native notifications. Focus-aware:
if the user is in a full-screen presentation, notifications are queued and delivered in batch on exit.

## 5.5 Screen Understanding (separate capability)
The `Screen Understanding` and `ScreenModel` logic is a distinct, tier-scaled capability documented in
the dedicated reference and skill `catlx-screen-understanding`. It is consumed by the DCE and the
Workflow Engine.

## Cross-references
- Consumed by: `skills/catlx-desktop-control/SKILL.md`, `skills/catlx-screen-understanding/SKILL.md`.
- Delegates to: `catlx-screen-understanding`, `catlx-electron-shell` (HUD), `catlx-security` (audit).
- Source tree: `knowledge/references/folder-structure.md` (`desktop-control/`).
