---
name: catlx-jarvis-bridge
description: "Bridge between CATLX and JARVIS systems — routes requests between the two orchestrators based on intent classification, capability availability, and authorization laddens. Ensures additive compatibility and never weakens existing policies."
metadata:
  catlx: bridge
  category: integration
  subsystem: CATLX_JARVIS_BRIDGE
  capability: cross-system-routing
  version: "1.0.0"
  source: "Integrated JARVIS capability package (C:\Users\HP\.config\opencode\jarvis-addon)"
  aliases: "jarvis-bridge, cross-system, catlx-jarvis, jarvis-catlx"
---
# CATLX ⇄ JARVIS Bridge

This skill bridges the **CATLX Universal AI Operating System** and the **JARVIS Add-On capability package**. It ensures the two systems can cooperate without conflict, respecting each other's additive policies and authorization ladders.

## When to activate

- User requests involve capabilities from **both** CATLX and JARVIS domains
- A CATLX request maps to a JARVIS-defined capability area (or vice versa)
- The user asks "Can JARVIS do X?" or "Use CATLX for Y"
- Ambiguous requests that could be handled by either system

## Two-mode routing

### MODE A — CATLX-first (default)
1. Classify the user's intent using CATLX's capability-index.json routing table
2. If the intent maps to a **JARVIS-defined area** (see bridging table below), delegate to JARVIS via `skill({ name: "jarvis" })` with the JARVIS operating model
3. JARVIS executes the task using its 10-step cycle (goal → compose → plan → execute → verify → record → recover → evaluate → learn)
4. Return the JARVIS result to the user, optionally weaving in CATLX context
5. If JARVIS cannot complete, CATLX fallback runs its own workflow

### MODE B — JARVIS-first
1. Classify the user's intent using JARVIS's capability routing (the 20 capability areas in `skills/jarvis/SKILL.md`)
2. If the intent maps to a **CATLX-defined area** (see bridging table below), delegate to CATLX via `skill({ name: "catlx-orchestrator" })`
3. CATLX executes using its skill ecosystem
4. Return the CATLX result, optionally weaving in JARVIS context
5. If CATLX cannot complete, JARVIS fallback runs its own cycle

## Bridging table — intent mapping

| CATLX intent area | JARVIS equivalent area | Bridge condition |
|---|---|---|
| `capability-creation` | `capability-creation` | Route to JARVIS `capability-composition` skill |
| `decision-support` | `proactive-assistance` | Route to JARVIS if decision needs evidence-based evaluation |
| `digital-world-model` | `world-state-management` | Route to JARVIS for state management |
| `failure-recovery` | `recovery` | JARVIS recovery cycle is default; CATLX fallback if needed |
| `general-reasoning` | `self-evaluation` | Route to JARVIS self-evaluation |
| `high-reliability` | `high-reliability` | JARVIS health-monitoring + prediction |
| `knowledge-updating` | `memory-management` | Route to JARVIS memory store |
| `long-horizon-autonomy` | `goal-management` | JARVIS goal-management is primary |
| `multi-agent-coordination` | `agent-coordination` | JARVIS agent-coordination |
| `multimodal-fusion` | `screen-understanding` | Route to JARVIS for screen UI analysis |
| `persistent-goals` | `goal-management` | Same area — JARVIS persistence wins for goal storage |
| `predictive-assistance` | `prediction` | Route to JARVIS prediction |
| `project-management` | `project-management` | Route to JARVIS project-management |
| `real-time-conversation` | `multimodal-context` | Route to JARVIS for conversation context |
| `skill-creation` | `skill-creation` | JARVIS skill-creation pipeline |
| `tool-routing` | `tool-routing` | JARVIS tool-routing |
| `verification` | `verification` | JARVIS verification-first contract |
| `workflow-optimization` | `workflow-optimization` | JARVIS workflow optimization |
| `world-state-management` | `digital-world-model` | Route to JARVIS world-model |

**Reverse bridging** (JARVIS → CATLX) uses the same table in reverse — if a JARVIS request maps to a CATLX area, delegate to `catlx-orchestrator`.

## Bridging procedure

1. **Classify intent** using the bridging table above
2. **Check authorization**: both systems have `non_override: true` additive policies. The most restrictive auth level wins. If CATLX requires `EXPLICIT_APPROVAL` and JARVIS requires `AUTHORIZED_AUTONOMOUS`, the more restrictive (`EXPLICIT_APPROVAL`) governs.
3. **Delegate**: invoke the target system's gateway skill:
   - CATLX → JARVIS: `skill({ name: "jarvis" })` with intent description
   - JARVIS → CATLX: `skill({ name: "catlx-orchestrator" })` with intent description
4. **Receive and synthesize**: the originating system receives the result and presents it to the user, noting which subsystem handled which part
5. **Cycle protection**: maintain an active-chain marker (`catlx↔jarvis`). If the same cross-system round is detected, skip redundant re-invocation and reuse the existing result

## Policy compatibility

Both CATLX and JARVIS adhere to **additive-only** policies (`non_override: true`):

- **CATLX**: `policies/antigravity-delegation.md` rule 6b (explicit user model requests override everything, highest priority)
- **JARVIS**: `policies/antigravity-delegation.md` rule 6b (same clause, synced)
- **Combined**: When both systems are active, the **user's explicit model request** (rule 6b HIGHEST PRIORITY) governs model selection. Model fallback stays within Gemini only; Claude/GPT are permanently prohibited as automatic fallbacks for both systems.
- **Verification-first**: Both require observed evidence for success (never fabricate)
- **Rollback**: Both use additive-reversible schemes (default `UNREGISTER`)
- **Placeholders**: `audit.scan_placeholders` must find 0 TODO/TBD/FIXME markers in any generated content for either system

## Integration with AGENTS.md

The combined routing table appears in the **JARVIS Operating Capability System** section of AGENTS.md (already added additively). Cross-system routing references:

- `skill({ name: "catlx-orchestrator" })` — invoke CATLX orchestrator from JARVIS context
- `skill({ name: "jarvis" })` — invoke JARVIS operating model from CATLX context
- `skill({ name: "catlx-jarvis-bridge" })` — explicit bridge invocation (rare; usually auto-routed)

**Never** create competing duplicate skills. If a capability exists in both systems, **reuse** the existing component and register the mapping in the bridging table. **Never** create a second knowledge source — connect back to the canonical layers.

## Source / provenance

- **CATLX side:** `C:\Users\HP\.config\opencode\catlx-skill-system\`, `C:\Users\HP\.config\opencode\skills\catlx\`
- **JARVIS side:** `C:\Users\HP\.config\opencode\jarvis-addon\`, `C:\Users\HP\.config\opencode\skills\jarvis\`
- **Bridge:** This skill, `C:\Users\HP\.config\opencode\catlx-skill-system\skills\catlx-jarvis-bridge\`
- **Cross-references:** AGENTS.md JARVIS section, CATLX orchestrator SKILL.md routing table