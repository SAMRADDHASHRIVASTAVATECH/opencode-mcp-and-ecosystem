---
name: desktop-applications
description: Builds local desktop UIs. Use for tkinter or when the user wants a desktop app. Native Windows admin is a different MCP.
---

# Desktop applications

- Default: `python-desktop` (tkinter, stdlib).
- Electron only if requested and Node is available.
- WinUI/.NET only if `dotnet` is installed; otherwise say so.
- Printers/services/drivers: **windows-system-mcp**, not a GUI wrapper.
