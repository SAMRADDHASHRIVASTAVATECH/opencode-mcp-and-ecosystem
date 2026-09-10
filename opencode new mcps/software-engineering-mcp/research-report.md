# Universal Software Engineering MCP — Research Report

**Date:** 2026-09-09  
**Status:** Research complete. Implementation follows.

---

## 1. What already exists in this ecosystem

| Specialist | Domain | Reuse, do not rebuild |
|------------|--------|------------------------|
| `office-documents-mcp` | DOCX/XLSX/PPTX | Document generation, inspect, convert |
| `database-sql-mcp` | SQLite/PG/MySQL/MSSQL/DuckDB | Schema, query, backup, SQL safety |
| `windows-system-mcp` | Windows admin, printers, CIM | OS/printer/driver ops |
| `android-development-mcp` | Android app lifecycle | Scaffold, Gradle, ADB, APK |

**Missing:** no skills (`SKILL.md`), no MCP config aggregating servers, no general software-engineering layer (web/CLI/desktop/backend/libraries), no technology-selection / architecture / test-debug-release playbooks.

This MCP is the **capability layer**: decide, scaffold non-specialist software, build/test/diagnose, and **route** specialist work to the four MCPs above.

---

## 2. What this MCP is not

- Not a MERN-only generator
- Not a duplicate of Android/Office/DB/Windows tools
- Not unbounded `run_shell`
- Not a replacement for GitHub/Playwright/cloud MCPs the user may add later

---

## 3. Host toolchain (this machine)

Present: Python 3.13, Node 20 / npm 10, gcc/g++, make, git, javac.  
Absent: Go, Rust/cargo, PHP, Ruby, .NET, Docker, Gradle.

The MCP must **detect** and generate anyway, returning `DEPENDENCY_MISSING` when a build cannot run.

---

## 4. Stacks to support (first-class templates)

Python CLI / library / FastAPI / Flask · Node CLI / Express / library · static HTML/CSS/JS · Java CLI · C + Makefile · Go CLI · Rust CLI · optional notes for Electron, Tauri, WinUI/.NET (route or generate stubs).

Desktop: Python tkinter (always available) or Electron if Node present. Native Windows GUI → recommend .NET if `dotnet` exists, else tkinter, and Windows *system* tasks go to `windows-system-mcp`.

Mobile: **always route to Android MCP** (and say iOS is out of scope here).

Data/docs: route to Database / Office MCPs.

---

## 5. Skill format

Agent Skills / Claude Skills: folder + `SKILL.md` with YAML `name` + `description` (third person, when-to-use), body < 500 lines, references one level deep.

Skills teach **decision procedures**, not encyclopedia pages.

---

## 6. Professional workflow to encode

```
request → classify domain → route specialist OR local stack
  → requirements → tech selection → architecture → plan
  → implement → build → test → diagnose → secure → package → verify
```
