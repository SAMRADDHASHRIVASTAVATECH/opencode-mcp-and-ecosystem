---
name: performance
description: Investigates slowness with measurement first. Use when the user reports performance problems or asks to optimize.
---

# Performance

Measure before changing algorithms.

- Python: time the function; don't rewrite to Rust unprompted.
- SQL: `db_explain` on the Database MCP.
- Android: `android_profile` (meminfo/gfxinfo).
- Web: fewer assets; don't add a bundler for three files.
- Avoid N+1 I/O; batch when evidence shows it matters.

If it's fast enough for the stated load, stop.
