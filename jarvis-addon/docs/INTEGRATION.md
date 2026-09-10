# Integration Guide (for a compatible JARVIS host)

This package is **self-contained and inert until imported**. It never requires,
assumes, installs or modifies any existing JARVIS/OpenCode/Claude host. A
compatible host reads this package and registers its contents additively.

## The import contract (summary of `import-metadata.yaml`)

For every component you receive, apply exactly this sequence:

1. **DETECT** — does an identifier already exist in the host?
2. **COMPARE** — are they identical?
3. **REUSE** — if identical, reuse the host's existing component. Do **not**
   register a duplicate.
4. **MAP** — if different, map this package's id to a namespaced extended id
   (prefix `jarvis_addon.`). 
5. **EXTEND** — register only under the new id; never touch the host's version.

Prohibited for every component: **REPLACE, DELETE, OVERWRITE, MODIFY_EXISTING.**

## What you receive (discoverable)

The package can tell you exactly what it ships. As a host, either:

* read the registries: `registries/{skill,agent,mcp,tool,event,policy,
  schema,contract,capability}-registry.yaml` and `manifest.yaml`, or
* call the runtime helper:

```python
import sys; sys.path.insert(0, "/path/to/jarvis-addon/src")
from jarvis_addon import registry, audit
inv = registry.inventory("/path/to/jarvis-addon")
caps = registry.discover_capabilities("/path/to/jarvis-addon")
print(inv)            # counts per kind
print(list(caps))     # the 20 capability areas
# integrity checks
print(audit.scan_placeholders("/path/to/jarvis-addon"))   # [] == no placeholders
```

## How to register additively

For each capability area (or each kind), follow the capability's authorization
level. Do not enable anything above the authorization the capability declares
until the operator grants it. Skills reference the tools/operations they rely
on; MCPs list the tools/resources they provide; policies carry `non_override:
true` and may only tighten existing host policy.

Recommended order (each step optional & reversible):

1. Validate every YAML/JSON against the bundled schemas
   (`src/jarvis_addon/schemautil.py`).
2. Register schemas, then contracts.
3. Register skills, tools, events.
4. Register MCP definitions and bind their tools/resources.
5. Register agents and their allowed-skills.
6. Register policies (as strict-override additions only).
7. Compose capability areas from the registered parts.
8. Enable capabilities only at or below their declared authorization, and only
   with operator consent where policy requires it.

## Rollback

Every addition is individually removable using `rollback-metadata.yaml`. The
default inverse for each kind is **UNREGISTER** of only that component, leaving
all unrelated JARVIS components untouched. No add-on component is ever required
by the host, so removal never breaks pre-existing functionality.

## Real-world note on host adapters

Where the package needs real physical capability it cannot (and must not)
provide on its own — OS/GUI automation, speech, screen capture, a memory
backend, code execution — it ships the **contract** of that adapter rather than
an implementation. A compatible host binds its own adapter to that contract.
This is why the package has no dependency on any specific host.
