# Architecture

This document explains how the add-on package is organized so that a receiver
can reason about it without reading every file.

## Layer model

The package is an **extension layer** that sits on top of an existing JARVIS.
It contributes three kinds of things:

1. **Declarative definitions** (skills, policies, agents, MCPs, tools, events,
   schemas, contracts, capability areas). These are data a host can discover,
   validate and register.
2. **Contracts** that describe behavior without depending on a host
   implementation (e.g. the GUI interaction contract, the memory store contract,
   the universal result contract).
3. **A tiny runtime library** (`src/jarvis_addon`) implementing the portable
   logic: state machines, the policy engine, the universal result, recovery
   selection, and package self-audit/discovery.

Nothing in the package is host code, and no host is required to exist.

## Capability area = composition root

Each of the 20 areas is a directory with a `capability.yaml` that is the
"bill of materials" for that area:

```yaml
capability_id: universal-digital-agency
skills:   [capability-composition, tool-selection, tool-routing, planning, verification]
policies: [agency-policy]
agents:   [orchestrator]
schemas:  [goal, result, context]
contracts:[agency-contract, result-contract]
events:   [GOAL_CREATED, TASK_COMPLETED]
authorization: {auth_level: AUTHORIZED_AUTONOMOUS}
```

Leaf definitions reference each other by id, so the whole package is a graph
you can walk from any entry point. `registry.discover_capabilities()` and the
`registries/*.yaml` files make this graph inspectable.

## Cross-cutting contracts (§17–§22)

These contracts are defined once under `contracts/` and mirrored by JSON
Schemas under `schemas/` so both humans and machines share the same contract:

| Contract | File | Schema |
|----------|------|--------|
| Universal result (§17)      | `contracts/result-contract.yaml`  | `schemas/result.schema.json` |
| Verification (§18)          | `contracts/verification-contract.yaml` | `schemas/verification.schema.json` |
| Recovery (§19)              | `contracts/recovery-contract.yaml` | `schemas/recovery.schema.json` |
| Events (§20)                | `events/*.yaml` + `event.schema.json` | `schemas/event.schema.json` |
| Memory (§21)                | `contracts/memory-contract.yaml` | `schemas/memory.schema.json` |
| World model (§22)           | `contracts/world-model-contract.yaml` | `schemas/worldmodel.schema.json` |
| Skill (§8)                  | `contracts/skill-contract.yaml` | `schemas/skill.schema.json` |
| Tool (§16)                  | `contracts/tool-contract.yaml` | `schemas/tool.schema.json` |

## Lifecycle state machines

Explicit, validated transitions live in `src/jarvis_addon/lifecycle.py` and are
the authoritative source:

* **Capability** (§24): `DISCOVERED → DESIGNED → EXPERIMENTAL → TESTING →
  VALIDATED → ENABLED` … `DEGRADED / DISABLED / DEPRECATED`
* **Maintenance** (§25): `HEALTHY → DEGRADED → DIAGNOSTIC → REPAIRING →
  TESTING → VERIFIED → HEALTHY`
* **Generation** (§26): `MISSING → DESIGNED → GENERATED → SANDBOXED → TESTED →
  VALIDATED → REGISTERED → ENABLED`

## Authorization & policy model (§9–§12)

* **Authorization ladder (§11):** `OBSERVE → RECOMMEND → SAFE_EXECUTE →
  AUTHORIZED_AUTONOMOUS → EXPLICIT_APPROVAL → DENIED`.
* **Policy actions (§10):** `ALLOW, ALLOW_WITH_CONDITIONS, REQUIRE_APPROVAL,
  DENY, ESCALATE`.
* The decision engine returns the **most-restrictive** applicable policy and
  honors `host_deny` / `host_min_auth` as strict overrides — it can only tighten,
  never loosen.

## Additive import semantics (§28)

`import-metadata.yaml` declares `import_type: TYPE_EXTENSION`,
`mode: ADDITIVE`, permitted operations `DETECT/COMPARE/REUSE/MAP/EXTEND`, and
prohibits `REPLACE/DELETE/OVERWRITE/MODIFY_EXISTING`. Every addition is
reversible per `rollback-metadata.yaml`.

## Host adapters are contracts, not dependencies

Where physical implementation requires a host (OS automation, STT/TTS, screen
capture, vector memory, code execution), this package ships only the *contract*
of that interface — for example the GUI interaction contract and the memory
store contract — so a compatible host can bind its own implementation without
the package depending on any specific host.
