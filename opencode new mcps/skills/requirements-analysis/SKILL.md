---
name: requirements-analysis
description: Turns a vague "build this" request into testable requirements. Use before architecture or scaffolding whenever scope is unclear or the user named an application without constraints.
---

# Requirements analysis

Ask or infer, then write a short spec:

- **Problem** in one sentence
- **Users** and primary job-to-be-done
- **Must / should / won't**
- **Platforms** (Linux/macOS/Windows; browser; Android)
- **Data** (local files, SQL, none)
- **Integrations** (none unless stated)
- **Success check** (command or UI step that proves it works)
- **Non-goals** (especially "not a mobile app" vs Android)

If the user said "app" and means Android, route to Android MCP. If they mean a website, pick static-web or a backend template — do not assume React.

Stop and ask only when a wrong guess is expensive (native store release, paid APIs, destructive ops).
