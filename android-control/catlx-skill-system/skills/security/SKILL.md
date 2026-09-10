---
name: security
description: Applies secure-by-default engineering checks. Use before release, when handling auth/secrets, or after se_security_audit findings.
---

# Security

- Run `se_security_audit` on the project.
- Android: also `android_security_audit`.
- SQL: never disable MCP write gates to "make the demo work".
- No hardcoded API keys. Use env vars.
- Allowlisted subprocess only (already true in these MCPs).
- Web: no innerHTML with user data; no eval.
- Dependencies: pin when shipping; `confirm=true` on install.
- Office macros: detect, never execute (Office MCP).
- Don't copy keystore passwords into README.
