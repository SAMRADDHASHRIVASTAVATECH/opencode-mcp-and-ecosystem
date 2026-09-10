---
name: architecture
description: Chooses module boundaries, data flow, and failure handling for new or existing software. Use after requirements and tech selection, before large implementation.
---

# Architecture

Keep it smaller than the ego.

- **CLI:** parse → domain function → print/exit codes. Tests call domain, not stdout only.
- **Library:** public API in `__init__` or `index.js`; no hidden I/O in core functions.
- **API:** HTTP adapter over domain; health endpoint; explicit errors; no business logic in the framework file only if it grows.
- **Web static:** HTML structure, CSS, JS unobtrusive.
- **Desktop:** UI thread vs work; don't block on network without feedback.
- **Multi-service:** don't. One process until proven otherwise.

Document: entrypoint, data stores, env vars, what happens when a dependency is down.

For Android, follow Android MCP architecture (modules, ViewModel), not this file's web advice.

Existing repo: `se_discover_project` and **match** its shape. Do not rewrite Django as FastAPI "for cleanliness" unless asked.
