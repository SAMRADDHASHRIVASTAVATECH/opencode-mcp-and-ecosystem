---
name: implementation
description: How to change and create code professionally in this ecosystem. Use when writing or editing application source after a plan exists.
---

# Implementation

- Change the smallest set of files.
- Match naming, formatter, and test style already in the tree.
- No drive-by refactors.
- New projects: `se_create_project` then edit — don't hand-author packaging files unless the template is wrong.
- After edits: `se_build` / `se_test` (or Android/Office equivalents).
- Dependencies: `se_deps` with `confirm=true`; do not silently npm-install the internet.
- Comments only where intent is non-obvious.
- Do not commit secrets. Do not log passwords (sibling MCPs redact).

If the task is "add a Word export", call Office MCP tools rather than generating XML by hand.
