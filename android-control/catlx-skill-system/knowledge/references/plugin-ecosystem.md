# Plugin Ecosystem — Canonical Reference

> Source: PART XIII — PLUGIN ECOSYSTEM. The single authoritative source for plugin architecture, runtime,
> security, SDK, marketplace readiness, hot reload, and version management / dependency resolution.

## 13.1 Plugin Architecture Philosophy
Plugins are how CATLX grows beyond its built-in capabilities. Every capability not core to the runtime can
be a plugin. Plugins are isolated, versioned, sandboxed, and replaceable. The architecture supports a
public marketplace while maintaining security and stability for the host runtime.

## 13.2 Plugin Runtime
Plugins run in the **Plugin Runtime** — an isolated execution environment separate from the core runtime.
On T0/T1, plugins run in Node.js worker threads with restricted access to the host API surface. On T2+,
plugins can optionally run in Docker containers for complete isolation. The runtime exposes a stable
**Plugin API (versioned semver)** that plugins call via a typed proxy interface. Internal CATLX module IDs
are never exposed to plugins.

## 13.3 Plugin Security
Every plugin package is **signed with the developer's private key**. The runtime verifies the signature
against the developer's public key registered in the Plugin Registry before loading. **Unsigned plugins are
rejected** unless the user explicitly enables developer mode (local development only). At install time the
user reviews the plugin's declared capabilities (file access, network hosts, credential names) and
approves or rejects each; approvals are stored in `plugins.db` and checked at every invocation.

## 13.4 Plugin SDK
The CATLX Plugin SDK is an npm package **`@catlx/plugin-sdk`** providing: TypeScript type definitions for
the entire Plugin API, a scaffolding CLI (`catlx plugin new my-plugin`), a test harness for local
development, mock implementations of all core services, and the build toolchain (esbuild + manifest
generator).

## 13.5 Marketplace Readiness
The **Plugin Marketplace** is an integrated panel in the Electron shell and a web portal
(marketplace.catlx.ai). Plugins are discoverable by category, capability, hardware-tier compatibility, and
rating. The in-app marketplace client handles: plugin search, one-click install, update notifications, and
uninstall. Plugin authors submit packages via the Developer Portal, which performs automated security
scanning (static analysis + capability audit) before listing.

## 13.6 Hot Reload
During development, plugins support hot reload: a file watcher monitors the plugin source directory; when a
source file changes, the runtime reloads the plugin module **without restarting CATLX**. In-flight calls
complete under the old version; new calls use the reloaded version. Hot reload is disabled for production
plugins (requires explicit opt-in in the plugin manifest).

## 13.7 Version Management & Dependency Resolution
Plugin dependencies are resolved by a deterministic resolver (analogous to yarn berry's PnP). Each plugin
carries its own vendored copy of third-party dependencies to avoid version conflicts with the host runtime
or other plugins. A **module alias map** ensures plugin imports resolve to their vendored copies. Breaking
Plugin API changes are handled via **API versioning**: plugins declare the API version they target; the
runtime provides a compatibility shim for older API versions up to **2 major versions back**.

## Cross-references
- Consumed by: `skills/catlx-plugin-ecosystem/SKILL.md`.
- Depends on / delegates to: `catlx-security` (signature, capability grant, sandbox), `catlx-silexis-modules` (packaging/registry), `catlx-electron-shell` (marketplace panel), `catlx-docker` (container sandbox), `catlx-hardware-adaptation` (plugin_sandbox tier).
- Plugin manifest template: `templates/plugin-manifest.json`.
- Source tree: `knowledge/references/folder-structure.md` (`plugins/`); registry `plugins.db`.
