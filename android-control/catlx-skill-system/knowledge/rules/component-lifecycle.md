# CATLX Skill Ecosystem — Component Lifecycle Policy

> **Reuse-First / Install-First / Last-Resort Creation.** This is the canonical policy for how this ecosystem
> obtains any missing capability, skill, dependency, tool, workflow, reference, helper, adapter, or template.
> It applies **uniformly** to the Universal Orchestrator, every individual skill, dependencies, workflows,
> references, helpers, adapters, templates, and supporting resources.
>
> Status: canonical rule. Reference it; do not duplicate it.

## The priority order (never inverted)

```text
1. REUSE EXISTING LOCAL COMPONENT
2. USE AN ALREADY REGISTERED COMPONENT
3. FIND / INSTALL AN EXISTING AVAILABLE COMPONENT
4. ADAPT AN EXISTING COMPATIBLE COMPONENT IF APPROPRIATE
5. CREATE A NEW COMPONENT ONLY AS THE LAST RESORT
```

Creation is the **final** option, never the default.

## Decision tree (check before create)

```text
REQUIRED CAPABILITY
      ↓
CHECK LOCAL SKILL SYSTEM            -> reuse
      ↓
CHECK REGISTERED COMPONENTS          -> use
      ↓
CHECK AVAILABLE / INSTALLABLE         -> install -> validate -> register -> use
      ↓
CHECK FOR COMPATIBLE EXISTING         -> adapt -> validate -> register -> use
      ↓
ONLY IF NOTHING SUITABLE EXISTS
      ↓
CREATE NEW COMPONENT -> validate -> register -> connect -> use -> persist
```

**Never skip directly to generation.** The five checks are mandatory and ordered.

## Where to look first (deterministically)

1. **Local skills** — `skills/` (and the registry `metadata/skills-registry.json`).
2. **Registered components** — `metadata/skills-registry.json`, `metadata/dependency-graph.json`,
   `metadata/capability-index.json`.
3. **Capability/intent lookup** — `metadata/capability-index.json` (`capability_to_skill`, `intent_to_skills`).
4. **Canonical knowledge** — `knowledge/` (concepts, rules, references) — reuse this rather than re-deriving.
5. **Installable** — a supported, trusted source compatible with the target runtime. Do **not** install
   arbitrary or untrusted components merely because their names look relevant. Only legitimate, compatible
   sources are allowed.
6. **Adaptable** — an existing component/skill that is close but not a perfect interface match; prefer a
   small **persistent adapter/wrapper** over re-creating the underlying capability.

## Reuse rules

- If a suitable component exists, **use it**. Do not recreate it, and do not create a second implementation
  merely because another name or path could be used.
- **Resolve aliases, equivalent names, and semantically equivalent capabilities** before concluding a
  component is missing. The capability index (aliases per skill) supports this.
- **Do not recreate installed components.** Once registered, future requests discover and reuse it.

## Install rules

- Prefer installing a suitable existing implementation over creating a new one.
- Use **only legitimate, compatible, trusted sources** supported by the target environment.
- After install: confirm/assign identity → register in the registry → describe capabilities → record
  dependencies → connect to the dependency graph → make discoverable in the capability index → use.
- **Validate** what you reasonably can before relying on it: compatibility, expected capability, skill
  format, dependencies, runtime compatibility, source/provenance, basic integrity. Do not blindly trust an
  incompatible or untrusted component.

## Adapt rules

- Prefer a small persistent **adapter/wrapper** over recreating the whole capability.
- Register the adapter and reuse it. Model it as: `Existing Component → Persistent Adapter → Skill Ecosystem`.

## Create rules (last resort)

Create a new component only when **all** of the following hold:
- no suitable local component exists, **AND**
- no suitable installable existing component exists, **AND**
- no suitable existing component can be reasonably adapted.

Then create the **smallest correct reusable** component that satisfies the requirement. Do not overbuild.
Do not create speculative capabilities that are not required.

A newly created reusable component must immediately become part of the permanent ecosystem:

```text
CREATE → VALIDATE → ASSIGN STABLE ID → PLACE IN PERMANENT LOCATION → REGISTER → ADD TO CAPABILITY INDEX
      → ADD TO DEPENDENCY GRAPH → ADD TO ROUTING → ADD SOURCE/PROVENANCE → USE → REUSE
```

Do not leave it as an unregistered file.

## Persistence rules (never temporary by default)

- A component that is likely to be useful beyond the current subtask must be created directly in the
  **permanent** skill ecosystem (its canonical location).
- Examples: reusable skill, sub-skill, workflow, reference, shared knowledge module, helper utility, adapter,
  template, routing component.
- **Avoid** `/tmp`, `temporary/`, `scratch/`, `session-only/` for components that are intended to survive.
- Temporary files are only for genuinely ephemeral work: intermediate parsing, temporary extraction, build
  artifacts, one-time transformation data, validation output, scratch calculations.
- **A temporary implementation must not secretly become a permanent dependency.** If an artifact is found to
  be reusable, **promote** it into the permanent ecosystem.

## Reusability check (before creating a temporary solution)

Ask: *"Will this capability reasonably be needed again?"* Consider:
- Is it a reusable capability? Is it a dependency of another skill? Is it useful outside the current request?
- Does it represent a stable concept? Could a future task need it?
- Does the source document define it as a reusable capability?

If substantially yes → **create/install/register it permanently.** Do not create a disposable copy.

## One source of truth

Installing or creating a component must **not** create a second competing knowledge source. It must connect
back to the canonical knowledge, canonical source, skill registry, and dependency graph. If an installed
component contains overlapping knowledge, decide whether it should be **referenced**, **adapted**,
**wrapped**, **superseded**, or remain an external implementation. Never silently create conflicting
authoritative copies.

## Final lifecycle (every missing capability)

```text
DISCOVER → REUSE? → USE
        → INSTALLABLE? → INSTALL → REGISTER → USE
        → ADAPTABLE?   → ADAPT  → REGISTER → USE
        → CREATE → VALIDATE → REGISTER → CONNECT → USE → PERSIST → REUSE FOREVER (unless intentionally updated)
```

The goal: a **persistent, growing ecosystem**, not a collection of temporary one-off implementations.
