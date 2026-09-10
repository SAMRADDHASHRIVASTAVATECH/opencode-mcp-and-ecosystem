---
name: catlx-plugin-ecosystem
description: "Handles the CATLX plugin ecosystem: the plugin runtime (worker threads / Docker), signed plugin security with capability grants, the @catlx/plugin-sdk, the Plugin Marketplace, hot reload, and version management with deterministic dependency resolution (PnP-style) and API compatibility shims. Use when the user asks about CATLX plugins, writing/installing a plugin, the Plugin SDK, marketplace, hot reload, plugin signing/security, or plugin dependency resolution."
metadata:
  catlx: subsystem
  category: architecture
  subsystem: Plugin_Runtime
  capability: plugin-ecosystem
  version: "1.0.0"
  source: "PART XIII §13.1-13.7"
  aliases: "plugins, plugin, plugin sdk, marketplace, extensions, hot reload"
  depends-on: "catlx-silexis-modules, catlx-security, catlx-electron-shell, catlx-docker"
---

# CATLX — Plugin Ecosystem

This skill owns how CATLX **grows beyond its built-in capabilities**: isolated, versioned, sandboxed,
replaceable plugins, with a marketplace-ready SDK and security guarantees.

> Canonical detail: `../../knowledge/references/plugin-ecosystem.md`. Manifest template:
> `../../templates/plugin-manifest.json`. Load on demand.

---

## Purpose

Let third-party developers extend CATLX safely, with signature verification, capability grants, sandboxing,
and deterministic dependency resolution — without exposing internal CATLX module IDs or risking the host
runtime.

## When to activate

- User asks how to write/install/update/uninstall a CATLX plugin.
- Configuring plugin signing, capability grants, or the marketplace.
- Debugging plugin sandboxing, hot reload, or dependency conflicts.

## What this skill handles

1. **Plugin architecture philosophy** — every non-core capability can be a plugin; plugins are isolated,
   versioned, sandboxed, replaceable; support a public marketplace while maintaining host security.
2. **Plugin Runtime** — isolated execution environment separate from core; worker threads (T0/T1) or Docker
   containers (T2+); versioned Plugin API via a typed proxy; internal module IDs never exposed.
3. **Plugin security** — every package signed with the developer's private key; runtime verifies against the
   registered public key; **unsigned plugins rejected** unless developer mode is enabled. At install the user
   reviews declared capabilities (file access, network hosts, credential names) and approves/rejects each;
   approvals stored in `plugins.db` and checked at every invocation.
4. **Plugin SDK** — `@catlx/plugin-sdk` npm package: TypeScript types for the full Plugin API, scaffolding
   CLI (`catlx plugin new my-plugin`), test harness, mock core-CATLX services, build toolchain
   (esbuild + manifest generator).
5. **Marketplace readiness** — integrated panel in the Electron shell + web portal (marketplace.catlx.ai);
   discover by category, capability, hardware-tier compatibility, rating; in-app client handles search, one-click
   install, update notifications, uninstall; authors submit via the Developer Portal which auto-scans
   (static analysis + capability audit) before listing.
6. **Hot reload** — during development, a file watcher reloads a plugin module without restarting CATLX;
   in-flight calls finish under the old version; disabled for production unless explicitly opted in.
7. **Version management & dependency resolution** — deterministic resolver (analogous to yarn berry PnP);
   each plugin vendors its own third-party deps; a module alias map resolves imports; breaking API changes via
   API versioning with a compatibility shim up to **2 major versions back**.

## Requirements / constraints

- **R5 (least privilege):** capability grants reviewed and stored in `plugins.db`; enforced per invocation.
- **R9 (modularity):** plugins are isolated/replaceable.
- Sandbox tier from CapabilityMap (`plugin_sandbox` = process / quota / docker).

## Canonical knowledge it reads

`../../knowledge/references/plugin-ecosystem.md` · `../../knowledge/references/security.md` ·
`../../knowledge/references/folder-structure.md` · `../../knowledge/references/data-registries.md`.

## Delegation

- **Signing/capability grant/sandbox enforcement** → delegate to `catlx-security`
  (`skill({ name: "catlx-security" })`).
- **Plugin packaging/artifact** → delegate to `catlx-silexis-modules`
  (`skill({ name: "catlx-silexis-modules" })`).
- **Marketplace panel in the shell** → delegate to `catlx-electron-shell`
  (`skill({ name: "catlx-electron-shell" })`).
- **Docker-container plugin sandbox** → delegate to `catlx-docker`
  (`skill({ name: "catlx-docker" })`).
- **Registering plugin capabilities with the router** → delegate to `catlx-capability-routing`
  (`skill({ name: "catlx-capability-routing" })`).

## Edge cases & warnings

- **Unsigned plugin:** reject unless explicit developer mode (local development only).
- **Capability grant:** the user approves each capability; un-granted access is blocked and logged.
- **Dependency conflicts:** vendored copies + module alias map prevent host/plugin conflicts.
- **Hot reload:** only for development; production plugins are loaded immutably.
- **Destroying sandbox on uninstall:** call `cleanup()`, deregister capabilities, remove files.

## Component lifecycle policy (reuse → install → adapt → create)

**NEVER create a new component as the default.** Before building/creating anything (a sub-skill, dependency,
reference, workflow, helper, adapter, or template), check, in order:
1. **Reuse** an existing local component (resolve aliases/equivalent capabilities first) — reuse, don't rebuild.
2. **Use** an already-registered component from the registry.
3. **Install** a suitable existing, trusted, supported component → validate → register → connect to the graph → use.
4. **Adapt** an existing compatible component via a small persistent adapter/wrapper instead of re-creating it.
5. **Create only as last resort** — then make it permanent immediately: stable id, canonical location, register,
   add to the capability index + dependency graph, add provenance, use, and allow future reuse.
6. Never reorganise/recreate already-generated components (no `Skill X 2` / `new` / `temp` variants); extend the
   existing one. Never create a second competing knowledge source; connect back to the canonical `knowledge/` layer.
   Promote any reusable artifact out of `/tmp`/scratch into the permanent ecosystem.

> Full policy: `../../knowledge/rules/component-lifecycle.md`.

## Source / provenance

- **Source:** PART XIII §13.1–13.7 (philosophy, runtime, security, SDK, marketplace readiness, hot reload,
  version management & dependency resolution).
- **Inferred:** none; plugin/Publisher/Portal naming preserved; marketplace coordinates (`marketplace.catlx.ai`)
  preserved as source facts, not endorsements.
