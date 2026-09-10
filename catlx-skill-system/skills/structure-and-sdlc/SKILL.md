---
name: structure-and-sdlc
description: Turns ASCII file trees and the 21-phase SDLC catalog into real project layouts. Use when the user pastes a tree, wants boilerplate folders, or asks for an SDLC blueprint by audience and project type.
---

# Structure and SDLC

Operational tools live on the software-engineering MCP. This skill is how to choose among them.

## When

- User pastes or asks to generate an **ASCII directory tree**.
- User wants **interconnected stubs** (Python/JS/Java/C/Go/Rust/…).
- User names an **audience** (kids, startups, clinicians, …) and a **project type**.
- User wants a **21-phase SDLC** outline at LOW / MEDIUM / HIGH depth.

## Tools

1. `se_ascii_tree` — `parse` / `preview` / `scan` / `create` (`create` needs `confirm=true`).
2. `se_sdlc` — `catalog` / `search` / `generate` / `export` (`export` needs `confirm=true`).
3. `se_launch_gui` — `ascii_tree` or `sdlc` for the desktop apps (needs a display).
4. After files exist: `se_discover_project`, `se_create_project` only if a stack template fits better than a raw tree.

## Decision

```
Have an ASCII tree (or a folder to scan)?
  → se_ascii_tree parse/preview, then create with confirm

Need a taxonomy / SDLC plan first?
  → se_sdlc catalog or search
  → se_sdlc generate (audience × category × type)
  → if they asked to write it: se_sdlc export with confirm
  → honor route_hint (android / office / sql / windows / se)

Android / Office / SQL / Windows domain work?
  → specialist MCP, do not fake it here
```

## Anti-patterns

- Dumping unbounded shell (`mkdir -p` loops) instead of `se_ascii_tree create`.
- Treating SDLC export as a finished product — it is a skeleton, not implementation.
- Ignoring `route_hint` on Android/Office/SQL/Windows types.
- Launching GUIs in headless CI.

## Next files

- [../software-engineering/SKILL.md](../software-engineering/SKILL.md)
- [../mcp-routing/SKILL.md](../mcp-routing/SKILL.md)
