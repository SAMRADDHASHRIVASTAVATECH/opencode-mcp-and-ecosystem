# Security Architecture — Canonical Reference

> Source: PART X — SECURITY ARCHITECTURE (Windows-only adaptation). The single authoritative source for
> the security model, credential vault, Windows Credential Manager integration, permission router,
> capability firewall, runtime sandbox, audit logs, risk detection, and safe/recovery modes.

## 10.1 Security Model Philosophy
CATLX operates with significant privileges (mouse/keyboard control, screen read, code execution, file
transfer). This requires a rigorous model built on **least privilege**: every module, plugin, and
workflow requests only the capabilities it actually needs, and those requests are logged and auditable.

## 10.2 Credential Vault
All sensitive credentials (API keys, passwords, OAuth tokens) are stored in the CATLX Credential Vault.
On **Windows it uses DPAPI** (Windows Data Protection API), which ties encryption to the user's Windows
login credential. Credentials are never stored in plaintext files, environment variables (in production),
or the module registry. The vault exposes a **capability-gated API**: a module requesting a credential
must declare the credential identifier in its manifest; the Permission Router checks the declaration at
load and at runtime; undeclared access is blocked and logged as a security event.

## 10.3 Windows Credential Manager Integration
On Windows, CATLX integrates with **Windows Credential Manager** as a secondary store for credentials
shared with other Windows applications (e.g., Outlook passwords, Azure credentials). CATLX reads from it
with explicit user consent and can write to it for cross-application sharing.

## 10.4 Permission Router
The runtime enforcement layer of the capability model. Every module declares required capabilities in its
manifest. At load time the Permission Router verifies declarations against a **user-approved capability
grant** stored in `permissions.db`. At runtime every capability exercise is checked against the grant;
un-guaranteed exercises are blocked and surfaced as permission-violation events.

| Capability category | Examples | Grant level required |
|---|---|---|
| File Read | Read any file; read within safe zone only | Per-directory grants |
| File Write / Delete | Write/delete any file; restricted zones | Explicit per-directory approval |
| Process Execution | Run system commands, scripts | Explicit approval per module |
| Network Access | HTTP calls to external hosts | Per-domain allowlist |
| Screen Read (OCR) | Capture and read screen contents | Global toggle, per-app exclusions |
| Input Synthesis | Keyboard/mouse control | Explicit approval; audit-logged |
| Credential Access | Read vault entries | Per-credential declaration in manifest |
| Plugin API | Cross-plugin communication | Namespaced plugin tokens |

## 10.5 Capability Firewall
A process-level enforcement layer below the Permission Router. Uses OS-level mechanisms
(**AppContainer** on Windows; **Windows Filtering Platform** network rules) to enforce capability
restrictions at the kernel level, ensuring that even a compromised module binary cannot exceed its
declared permissions. Plugin processes run in the most restrictive sandbox tier compatible with their
declared capabilities.

## 10.6 Runtime Sandbox
Plugins execute in isolated Node.js worker threads (T0/T1) or Docker containers (T2+). Each sandbox has:
a memory quota, a CPU time budget per call, a restricted filesystem view (only declared paths accessible
via path mapping), a network policy enforced by a Windows Filtering Platform rule, and a hard-kill
timeout that terminates the sandbox if it exceeds its wall-clock budget.

## 10.7 Audit Logs
Every action is recorded in an append-only audit log in `/data/audit/`. Each entry records: timestamp,
actor (module/workflow/plugin), action type, target (file path, window handle, URL, etc.), parameters,
and outcome. Entries are **signed with a per-installation HMAC key** so tampering can be detected.
Retained 90 days by default and exported with every daily backup.

## 10.8 Risk Detection
Analyzes workflow execution patterns in real time and flags: workflows that access files outside their
declared scope, modules requesting credentials not used in 30 days, unusual network egress patterns, and
inputs matching prompt-injection patterns. Flagged events are surfaced in the dashboard and **optionally
halt the workflow pending user review**.

## 10.9 Recovery Mode & Safe Mode
- **Safe Mode** — only the core runtime active; no plugins, no user-defined workflows, no AI provider
  calls. Used for troubleshooting startup failures and inspecting state after a security event.
- **Recovery Mode** — starts with the last-known-good configuration snapshot; plugins flagged as errored
  or that caused the last crash are disabled; runs a configuration health check and presents results
  before resuming normal operation.

## Cross-references
- Consumed by: `skills/catlx-security/SKILL.md`.
- Depends on / delegates to: `catlx-hardware-adaptation` (plugin_sandbox tier), `catlx-recovery` (safe/recovery mode), `catlx-telemetry` (audit and risk events), `catlx-docker` (container sandbox).
- Permission policy template: `templates/permissions.yaml`; vault: `credentials.db`.
- Source tree: `knowledge/references/folder-structure.md` (`security/`, `data/audit/`, `data/identity/`).
