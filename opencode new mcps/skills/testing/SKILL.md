---
name: testing
description: Plans and runs tests for software in this ecosystem. Use when adding features, fixing bugs, or before declaring work done.
---

# Testing

Minimum bar: **one automated test that fails if the change is broken**.

| Kind | Tool |
|------|------|
| Python | `se_test` → pytest |
| Node | `npm test` / node:test |
| C/Make | `make` / `make test` |
| Android | `android_run_tests` |
| SQL | `db_query` against fixtures, not production drops |

- Prefer tests of domain behavior over snapshot spam.
- Don't mock the thing you're trying to prove.
- If the toolchain is missing, report it; don't skip quietly.
- Record the command that was run and its exit code.
