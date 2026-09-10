# Contract & Section Map

This file maps the original design's numbered sections to where each is
implemented in this package, so a reviewer can verify nothing is missing.

| § | Concern | Where implemented |
|---|---------|-------------------|
| §5  | Capability creation pipeline | `src/jarvis_addon/generator.py`, capability area `capability-creation`, `capability-creation-policy` |
| §8  | Universal skill schema | `schemas/skill.schema.json`, `contracts/skill-contract.yaml`, `skills/*.yaml` |
| §9  | Policy actions | `src/jarvis_addon/policy.py` (ALLOW…ESCALATE) |
| §10 | Policy actions list | `contracts/authorization-contract.yaml`, `policies/*.yaml` |
| §11 | Authorization ladder | `src/jarvis_addon/policy.py`, `contracts/authorization-contract.yaml` |
| §12 | Non-override rule | enforced in `policy.evaluate` + `policies/*.yaml` (`non_override: true`) |
| §13 | Agent roles | `agents/*.yaml` (21), `schemas/agent.schema.json` |
| §14 | Real MCP definitions | `mcps/*.yaml` (10), `schemas/mcp.schema.json` |
| §15 | MCP management | skills under `capability-creation` + `self-maintenance` (mcp-discovery/creation/validation/registration/health), `mcp-health`, `mcp-list` tools |
| §16 | Tool contract | `schemas/tool.schema.json`, `contracts/tool-contract.yaml`, `tools/*.yaml` (44) |
| §17 | Universal result | `contracts/result-contract.yaml`, `schemas/result.schema.json`, `src/jarvis_addon/result.py` |
| §18 | Verification contract | `contracts/verification-contract.yaml`, `schemas/verification.schema.json` |
| §19 | Recovery contract | `contracts/recovery-contract.yaml`, `schemas/recovery.schema.json`, `src/jarvis_addon/recovery.py` |
| §20 | Events | `events/*.yaml` (30), `schemas/event.schema.json` |
| §21 | Memory | `contracts/memory-contract.yaml`, `schemas/memory.schema.json`, `memory/*` |
| §22 | World model | `contracts/world-model-contract.yaml`, `schemas/worldmodel.schema.json`, `world-model/*` |
| §24 | Capability lifecycle | `src/jarvis_addon/lifecycle.py` |
| §25 | Self-maintenance lifecycle | `src/jarvis_addon/lifecycle.py`, `maintenance-lifecycle` policy |
| §26 | Generation lifecycle | `src/jarvis_addon/lifecycle.py` + `generator.py` |
| §28 | Import metadata | `import-metadata.yaml` (TYPE_EXTENSION / MODE_ADDITIVE, no replace/delete/overwrite) |
| §31 | Rollback metadata | `rollback-metadata.yaml` |
| §32 | Tests | verification via `src/jarvis_addon/{audit,registry}.py` (dedicated test suite removed by operator decision) |
| §33 | Docs | `docs/` |
| §35 | No placeholders | enforced by `audit.scan_placeholders` |
| §40 | Acceptance audit | `docs/ACCEPTANCE.md`, `src/jarvis_addon/audit.py`, `registry.py` |

## Other contract files

| File | Purpose |
|------|---------|
| `contracts/context-contract.yaml` | assembled/prioritized/compressed context packets |
| `contracts/observation-contract.yaml` | unified multimodal observation envelope |
| `contracts/goal-contract.yaml` | persistent authorized goals |
| `contracts/prediction-contract.yaml` | bounded, labelled predictions |
| `contracts/coordination-contract.yaml` | multi-agent leases/locks/merging |
| `contracts/conversation-contract.yaml` | real-time conversation primitives |
| `schemas/decision.schema.json` | decision-support structure |
| `schemas/observation.schema.json` | multimodal observation |
| `schemas/context.schema.json` | context packet |
| `schemas/prediction.schema.json` | prediction |
| `schemas/goal.schema.json` | persistent goal |
| `schemas/memory.schema.json` | memory item |
| `schemas/worldmodel.schema.json` | world model |
| `schemas/definitions.json` | shared auth/action/permissions enums |
