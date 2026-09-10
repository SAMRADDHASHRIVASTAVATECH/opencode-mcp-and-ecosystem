# Workflow Engine — Canonical Reference

> Source: PART IX — WORKFLOW ENGINE. The single authoritative source for the DAG model, scheduling,
> checkpointing, replay, rollback, recovery/resilience, state machines, and the workflow definition DSL.

## 9.1 Overview
The Workflow Engine (WFE) is the execution core. Every CATLX action — from a simple file rename to a
multi-step research pipeline — is expressed as a **workflow**: a **Directed Acyclic Graph (DAG)** of
atomic steps. The WFE provides scheduling, parallel execution, checkpointing, replay, rollback, and
recovery as first-class features.

## 9.2 DAG Execution Model
A workflow DAG is a set of **Nodes** (steps) and directed **Edges** (dependencies). A node executes only
when all its parent nodes complete successfully. Nodes with no dependencies between them execute in
parallel up to the workflow-parallelism limit defined by the CapabilityMap. Each node is assigned: a
unique step ID, the module to invoke, input parameters (static or derived from parent outputs), a
timeout, and a retry policy.

## 9.3 Workflow Scheduling (four modes)

| Mode | Description | Example |
|---|---|---|
| **Immediate** | Execute now; synchronous response | Voice-triggered actions |
| **Deferred** | Execute at a specified time or cron expression | "summarize my emails every morning at 8 AM" |
| **Event-Driven** | Execute when a trigger fires (file created, clipboard changed) | — |
| **Background** | Execute at lowest priority, yielding CPU to interactive tasks | Memory compression, model downloads |

## 9.4 Checkpointing
Every workflow step writes a checkpoint to `workflows.db` on completion. A checkpoint records: step ID,
completion time, output data hash, and execution duration. If a workflow is interrupted (crash, power
loss, manual stop), the WFE resumes from the last successful checkpoint rather than restarting.
Checkpoint granularity is configurable per workflow; **high-cost operations (large file transfers, LLM
calls) always checkpoint regardless of setting.**

## 9.5 Replay
Any completed workflow can be replayed with identical inputs (debug/audit) or modified inputs
(iteration). During replay, CATLX can optionally use cached outputs from the original run for steps known
to be deterministic, dramatically reducing execution time. Replay is the primary debugging tool for
workflow authors.

## 9.6 Rollback
Steps that modify state (file operations, database writes, desktop actions) declare their **inverse
operation** at definition time. The WFE maintains a **rollback log** — an ordered list of inverse
operations for every completed step. If a step fails partway through, the WFE offers a full rollback:
executing all inverse operations in reverse order to restore the pre-workflow state. Offered automatically
on failure; triggerable manually from the dashboard.

## 9.7 Recovery & Resilience (multi-layer)

- **Step-Level Retry** — configurable exponential backoff per step (default 3 retries, 2s/4s/8s delays).
- **Provider Failover** — on AI provider error, retry with the next provider in the routing list.
- **Checkpoint Resume** — on crash recovery, incomplete workflows resume from last checkpoint on next startup.
- **Saga Pattern** — compensating transactions for distributed workflows across Docker services (eventual consistency).
- **Workflow Isolation** — workflows run in isolated execution contexts; a failure in one cannot corrupt another.

## 9.8 State Machines
Complex multi-step interactive workflows (multi-day research, iterative document drafting) are expressed
as **State Machines** rather than simple DAGs. A state machine workflow has: named states, transition
rules (including conditional transitions based on runtime data), entry/exit actions for each state, and a
terminal state. CATLX's voice interaction itself is a state machine: **Idle → Listening → Processing →
Executing → Feedback → Idle**.

## 9.9 Workflow Definition Format (YAML DSL)
Workflows are defined in a YAML-based DSL stored in `/workflows/definitions/`. Example:

```yaml
workflow:
  id: summarize-clipboard
  trigger: voice
  steps:
    - id: read-clipboard
      module: catlx.core.desktop.clipboard
      action: read
    - id: summarize
      module: catlx.core.ai.complete
      depends_on: [read-clipboard]
      input:
        prompt: 'Summarize this in 3 bullet points: {{read-clipboard.output}}'
    - id: speak-result
      module: catlx.core.tts
      depends_on: [summarize]
      input:
        text: '{{summarize.output}}'
```

## Cross-references
- Consumed by: `skills/catlx-workflow-engine/SKILL.md`.
- Depends on / delegates to: `catlx-capability-routing` (parallelism limit), `catlx-ai-provider`, `catlx-memory`, `catlx-security` (permission check per step), `catlx-telemetry`.
- DSL template: `templates/workflow-dsl.yaml`; example: `examples/workflow-summarize-clipboard.yaml`.
- Detailed lifecycle: `knowledge/references/runtime-lifecycle.md` (§18.3).
