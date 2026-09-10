---
name: catlx-desktop-control
description: "Handles the CATLX Desktop Control Engine: mouse control, keyboard synthesis, window management, file operations, browser automation (Playwright/Puppeteer), application automation (UIAutomation/COM-WMI/OCR), multi-monitor support, the overlay HUD, and native notifications. Use when the user asks how CATLX moves the mouse, types, reads windows, manages files, automates browsers or apps, handles multiple monitors, or shows HUD/notifications."
metadata:
  catlx: subsystem
  category: interface
  subsystem: Desktop_Control_Engine
  capability: desktop-automation
  version: "1.0.0"
  source: "PART V §5.1-5.4, 5.6-5.11"
  aliases: "desktop control, mouse, keyboard, window management, file ops, browser automation, app automation, automate"
  depends-on: "catlx-electron-shell, catlx-security"
---

# CATLX — Desktop Control Engine

This skill owns the **"hands"** of CATLX: the ability to interact with any Windows application as a human
would — moving the mouse, typing, reading the screen, navigating browser UIs, and managing files. Modules
expose a unified **Desktop API** consumed by the Workflow Engine.

> Canonical detail: `../../knowledge/references/desktop-control.md` (screen/OCR detail lives in
> `catlx-screen-understanding`). Load on demand.

---

## Purpose

Give the AI the mechanics to act on the desktop. This skill coordinates the isolated modules that implement
that interaction and enforces the safety/audit constraints around destructive actions.

## When to activate

- User asks how CATLX controls the mouse, keyboard, windows, files, browsers, or apps.
- Designing an automation that involves clicking/typing/reading UI.
- Debugging window manipulation, coordinates, or safe-zone file operations.

## What this skill handles

1. **Mouse control** (`MouseController`, robotjs) — absolute/relative/smooth move, left/right/middle click,
   double-click, drag, vertical/horizontal scroll. Coordinates are logical pixels normalized to the primary
   display; multi-monitor coordinates auto-translated.
2. **Keyboard control** (`KeyboardController`) — raw key press/release, text typing (configurable
   inter-keystroke delay), hotkeys (Ctrl+C, Win+R), clipboard read/write, **secure input mode** (no logging
   for password fields). Uses **SendInput** on Windows.
3. **Window management** (`WindowManager`) — enumerate windows via **UIAutomation**; list (title, process,
   geometry), bring to front, move/resize, minimize/maximize/restore, close, split to halves, move across
   monitors; use window state as interaction context.
4. **File operations** (`FileOps`) — read/write/copy/move/delete/rename, create/list dir, search by
   name/content, compress/extract. Destructive ops are audit-logged and optionally require voice
   confirmation; file ops respect **safe zones** (deletion blocked without override).
5. **Browser automation** — **Playwright** (primary) with **Puppeteer** fallback; Chromium/Firefox/WebKit;
   injects a companion extension for DOM reads (no OCR overhead); navigate, click by CSS/accessibility name,
   fill forms, extract content, screenshot, handle auth, multiple contexts.
6. **Application automation** — hybrid: **UIAutomation** (modern Windows apps with accessibility trees),
   **OCR-based interaction** (legacy apps), **native COM/WMI** (Microsoft Office).
7. **Multi-monitor** — enumerate displays at boot/hotplug; coordinates as `(display_index, x, y)`; capture
   full virtual desktop or a single display; ScreenModels merged.
8. **Overlay HUD** — transparent, click-through, topmost Electron window; shows voice state, workflow
   progress, pending memory writes, agent status, toasts; disabled on T0 (tray tooltip instead); auto-hides
   in full-screen, re-appears on wake word.
9. **Notifications** — Windows Notification Center integration; focus-aware batching (queue in full-screen;
   deliver on exit).

## Requirements / constraints

- **R5 (least privilege):** destructive ops audit-logged; input synthesis explicitly approved and
   audit-logged; safe zones honored.
- **Windows-only:** UIAutomation, SendInput, Windows Notification Center. See `../../knowledge/rules/windows-rules.md`.
- Coordinates are logical pixels; translate multi-monitor.

## Canonical knowledge it reads

`../../knowledge/references/desktop-control.md` · `../../knowledge/references/screen-understanding.md` ·
`../../knowledge/rules/windows-rules.md` · `../../knowledge/references/security.md`.

## Delegation

- **OCR / Screen Understanding / ScreenModel** → delegate to `catlx-screen-understanding`
  (`skill({ name: "catlx-screen-understanding" })`).
- **Permission/audit for destructive ops** → delegate to `catlx-security`
  (`skill({ name: "catlx-security" })`).
- **HUD window shell, command palette, tray** → delegate to `catlx-electron-shell`
  (`skill({ name: "catlx-electron-shell" })`).
- **Executing actions as a workflow** → delegate to `catlx-workflow-engine`
  (`skill({ name: "catlx-workflow-engine" })`).
- **Where a DCE module runs (process/subprocess/container)** → delegate to `catlx-capability-routing`
  (`skill({ name: "catlx-capability-routing" })`).

## Edge cases & warnings

- **Legacy apps without accessibility trees** — use OCR-based interaction, not UIAutomation.
- **Full-screen presentation** — batch notifications; auto-switch HUD focus.
- **Safe zones** — refuse automated deletion outside approved zones unless an explicit override occurs.
- **Secure input** — never log keystrokes in password fields.
- **Multi-monitor** — always use `(display_index, x, y)`; never assume primary only.

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

- **Source:** PART V §5.1–5.4, 5.6–5.11 (overview, mouse, keyboard, window, browser, app automation, file
  ops, multi-monitor, HUD, notifications). §5.5 (OCR/Screen Understanding) is in `catlx-screen-understanding`.
- **Inferred/adapted:** Windows equivalents (UIAutomation, SendInput, Notification Center); Linux text paths
  (AT-SPI2, uinput, XTest) and libnotify dropped.
