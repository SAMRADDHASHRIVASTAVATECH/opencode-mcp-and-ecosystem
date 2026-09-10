---
name: mcp-routing
description: Chooses which existing specialist MCP and which software-engineering tools to use. Use at the start of any engineering task and whenever work crosses documents, SQL, Windows, Android, or general code.
---

# MCP routing

This ecosystem already has specialists. Routing is part of engineering.

| User intent | MCP | Do not |
|-------------|-----|--------|
| Word/Excel/PowerPoint files | `office-documents-mcp` | Hand-build OOXML |
| Query/schema/backup SQL | `database-sql-mcp` | Raw sqlite3 with no policy |
| Printers, spooler, Windows services | `windows-system-mcp` | Generic PowerShell |
| Android app/APK/emulator | `android-development-mcp` | Fake Gradle in SE MCP |
| CLI, library, API, web, desktop, C/Go/Rust/Java | `software-engineering-mcp` | Force Node+React |

Call `se_route` with the user's words. Honor `specialist` when `score > 0`.

If both apply (e.g. "Android app with SQLite"): **Android MCP for the app**, Database MCP for on-device/file SQL analysis if needed. Do not merge servers.

Skills live in `skills/*/SKILL.md`. Load only what the current phase needs.
