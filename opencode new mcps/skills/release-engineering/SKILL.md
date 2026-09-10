---
name: release-engineering
description: Packages, versions, and verifies software for delivery. Use when the user asks to ship, release, produce artifacts, or write install instructions.
---

# Release engineering

1. Version bump in the project manifest.
2. `se_test` / specialist tests green.
3. `se_security_audit`.
4. `se_package` or Android `assembleRelease` / `bundleRelease` (Android MCP).
5. `se_document` if README is missing.
6. State artifacts paths and how a stranger runs them.
7. Do not publish to npm/PyPI/Play unless explicitly asked (and then still confirm).

Android signing: Android MCP, user keystore, never invent a production password.
