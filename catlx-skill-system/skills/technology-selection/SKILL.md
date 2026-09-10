---
name: technology-selection
description: Selects language, framework, and build system from host capabilities and requirements. Use before se_create_project or adding dependencies. Avoids MERN-default and fashion-driven stacks.
---

# Technology selection

## Rules

1. Prefer what `se_detect_environment` shows is **installed**.
2. Prefer stdlib and boring libraries.
3. One language per small project unless there is a hard reason.
4. Web UI: static HTML first; add a framework only for real SPA complexity.
5. API: Python FastAPI or Flask, or Node Express — pick the language the rest of the repo uses.
6. CLI: Python argparse or Node bin, or C/Go/Rust if the user asked native.
7. Desktop: tkinter if Python; do not invent Electron unless requested.
8. Android: **Android MCP**, Kotlin Compose default there.
9. Data: Database MCP for SQL; do not embed a new ORM "because".
10. Windows printers/OS: Windows MCP.

## Template map (`se_create_project`)

| Need | Template |
|------|----------|
| CLI | `python-cli`, `node-cli`, `c-cli`, `go-cli`, `rust-cli`, `java-cli` |
| Library | `python-lib`, `node-library` |
| HTTP API | `python-fastapi`, `python-flask`, `node-express` |
| Website | `static-web` |
| Desktop | `python-desktop` |

If Go/Rust missing, you may still scaffold, but `se_build` will fail honestly.
