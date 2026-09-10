---
name: catlx-workflow-engine
description: "Handles the CATLX Workflow Engine: the DAG execution model, the four scheduling modes (immediate/deferred/event/background), checkpointing, replay, rollback, multi-layer recovery and resilience, state machines, and the YAML workflow definition DSL. Use when the user asks about CATLX workflows, running tasks in steps, scheduling, checkpoint/resume, replaying/rolling back a run, or defining a workflow in YAML."
metadata:
  catlx: subsystem
  category: architecture
  subsystem: Workflow_Engine
  capability: workflow-execution
  version: "1.0.0"
  source: "PART IX §9.1-9.9"
  aliases: "workflow, dag, scheduling, task runner, pipeline, checkpoints, replay, rollback, automation"
  depends-on: "catlx-capability-routing, catlx-ai-provider, catlx-memory, catlx-security"
---

# CATLX — Workflow Engine

This skill owns the **execution core** of CATLX. Every action — from a file rename to a multi-step research
pipeline — is a workflow: a **Directed Acyclic Graph (DAG)** of atomic steps. The WFE provides scheduling,
parallel execution, checkpointing, replay, rollback, and recovery as first-class features.

> Canonical detail: `../../knowledge/references/workflow-engine.md`. DSL example:
> `../../workflows/summarize-clipboard.yaml` and `../../workflows/summarize-clipboard.yaml`. Load on demand.

---

## Purpose

Model and run any task as a schedulable, resumable, replayable, and safely undoable DAG of steps.

## When to activate

- User asks how CATLX plans/runs a multi-step task, or asks to schedule/define a workflow.
- Designing step dependencies, retries, timeouts, or rollback.
- Debugging a failed/interrupted run or resuming from a checkpoint.
- Defining a workflow in the YAML DSL.

## What this skill handles

1. **DAG execution model** — Nodes (steps) + directed Edges (dependencies). A node runs only when all parents
   succeed; independent nodes run in parallel up to the workflow-parallelism limit. Each node has a step ID,
   module to invoke, input (static or derived from parent outputs), timeout, retry policy.
2. **Scheduling (four modes)** — Immediate (now, synchronous), Deferred (time/cron), Event-Driven (trigger
   fires), Background (lowest priority, yields CPU).
3. **Checkpointing** — each step writes a checkpoint to `workflows.db` (step ID, completion time, output hash,
   duration). Resume from last checkpoint after interruption; high-cost ops always checkpoint.
4. **Replay** — with identical or modified inputs; optionally reuse cached deterministic outputs; primary
   debugging tool.
5. **Rollback** — steps declare inverse operations; the rollback log applies inverses in reverse order to
   restore pre-workflow state; offered on failure, manual from dashboard.
6. **Recovery & resilience** — step-level retry (default 3 retries, 2s/4s/8s backoff), provider failover,
   checkpoint resume, Saga pattern (compensating transactions for distributed workflows), workflow isolation.
7. **State machines** — for complex interactive workflows: named states, transition rules, entry/exit actions,
   terminal state. (Voice: Idle → Listening → Processing → Executing → Feedback → Idle.)
8. **Workflow definition format** — YAML DSL in `/workflows/definitions/`; see `../../workflows/summarize-clipboard.yaml`.

## Requirements / constraints

- **R8 (replay safety):** every workflow checkpointed, replayable, rollbackable.
- **R2:** parallelism limit from the CapabilityMap.
- **R5:** ExecutionPlan validated by the Permission Router (capability check per step) before execution.
- No cycles in a DAG; all dependencies present; all modules available (validate before run).

## Canonical knowledge it reads

`../../knowledge/references/workflow-engine.md` · `../../knowledge/references/runtime-lifecycle.md` ·
`../../knowledge/references/data-registries.md` · `../../knowledge/rules/architectural-rules.md`.

## Delegation

- **Parallelism limit / scheduling by tier** → delegate to `catlx-capability-routing`
  (`skill({ name: "catlx-capability-routing" })`).
- **Steps that call AI** → delegate to `catlx-ai-provider` (`skill({ name: "catlx-ai-provider" })`).
- **Steps that read/write memory** → delegate to `catlx-memory` (`skill({ name: "catlx-memory" })`).
- **Steps that act on the desktop / file ops** → delegate to `catlx-desktop-control`
  (`skill({ name: "catlx-desktop-control" })`).
- **Step permission validation** → delegate to `catlx-security` (`skill({ name: "catlx-security" })`).
- **Container-hosted steps (Saga / distributed)** → delegate to `catlx-docker`
  (`skill({ name: "catlx-docker" })`).
- **Crash resume / checkpoint restore** → delegate to `catlx-recovery`
  (`skill({ name: "catlx-recovery" })`).
- **Telemetry of runs** → delegate to `catlx-telemetry` (`skill({ name: "catlx-telemetry" })`).

## Edge cases & warnings

- **Cycles:** a DAG must have no cycles; validate before executing.
- **Failure partway:** offer rollback; if accepted, apply inverses in reverse order.
- **Distributed (Docker) workflows:** use Saga compensating transactions for eventual consistency.
- **Deterministic replay:** only reuse cached output for steps proven deterministic.
- **Workflow isolation:** a failure in one workflow must not corrupt another.

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

- **Source:** PART IX §9.1–9.9 (overview, DAG model, scheduling, checkpointing, replay, rollback, recovery &
  resilience, state machines, workflow definition format/DSL example).
- **Inferred:** none; DSL example preserved exactly in `../../workflows/summarize-clipboard.yaml`.
