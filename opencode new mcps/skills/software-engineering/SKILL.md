---
name: software-engineering
description: Orchestrates a one-person software team workflow from request to verified delivery. Use when the user asks to build, maintain, debug, or ship any application, library, API, CLI, desktop, or service — and before writing code.
---

# Software engineering (one-person team)

Operate as a professional engineer, not a snippet generator.

## Always

1. Read `mcp-routing` mentally: **reuse specialist MCPs**.
2. Call `se_detect_environment` and `se_ecosystem` (or `se_route`) before scaffolding.
3. If a project path exists, `se_discover_project` before inventing a new stack.
4. Produce a short plan (`se_plan` or equivalent) the user can see.
5. Implement the smallest thing that satisfies the requirement.
6. Build and test on the **detected** toolchain. If a tool is missing, say so (`DEPENDENCY_MISSING`) — do not pretend.
7. `se_security_audit` (and specialist audits) before calling it done.
8. Document how to run it.

## Decision tree

```
Is it Android / APK / Compose / ADB?
  → android-development-mcp (+ this skill for general process)

Office document (docx/xlsx/pptx)?
  → office-documents-mcp

SQL database work?
  → database-sql-mcp

Windows printers/services/drivers?
  → windows-system-mcp

ASCII tree / folder layout / SDLC blueprint?
  → skill `structure-and-sdlc` + `se_ascii_tree` / `se_sdlc`

Otherwise software (cli, lib, api, web, desktop, native)?
  → software-engineering-mcp templates + this skill
```

## "Build this application" procedure

1. **Requirements** — skill `requirements-analysis`. Extract actors, must-haves, out-of-scope, constraints (OS, offline, license).
2. **Research / tech selection** — skill `technology-selection`. Prefer boring, installed toolchains.
3. **Architecture** — skill `architecture`. Modules, data, APIs, failure modes.
4. **Implement** — skill `implementation`. Match existing project style.
5. **Test** — skill `testing`. At least one automated test that would fail if the feature broke.
6. **Debug** — skill `debugging` if red.
7. **Secure** — skill `security`.
8. **Package / release** — skill `release-engineering`.
9. **Verify** — run the happy path; record commands that worked.

## Anti-patterns

- Defaulting every web app to MERN.
- Generating Android apps with `se_create_project` (wrong MCP).
- Unbounded shell.
- Silent skip of tests because "the code looks fine".
- Duplicating SQL/Office/Windows/Android tools here.

## Next files

- [../mcp-routing/SKILL.md](../mcp-routing/SKILL.md)
- [../technology-selection/SKILL.md](../technology-selection/SKILL.md)
