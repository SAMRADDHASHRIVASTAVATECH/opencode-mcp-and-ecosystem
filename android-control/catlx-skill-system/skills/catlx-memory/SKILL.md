---
name: catlx-memory
description: "Handles the CATLX memory architecture: episodic, semantic, workspace, and knowledge-graph memory stores, the Memory Broker as the single access point, the coherence protocol, memory compression, RAG-based retrieval optimization, and long-term persistence/portability. Use when the user asks about CATLX memory, remembering conversations, facts/preferences, workspace state, knowledge graphs, conflict resolution between memories, or how memory feeds AI calls."
metadata:
  catlx: subsystem
  category: architecture
  subsystem: Memory_Architecture
  capability: memory-management
  version: "1.0.0"
  source: "PART VII §7.1-7.11"
  aliases: "memory, remember, recall, facts, preferences, knowledge graph, memory broker, rag"
  depends-on: "catlx-ai-provider"
---

# CATLX — Memory Architecture

This skill owns the **memory architecture** — the human-cognition-inspired stores and the **Memory Broker**
that coordinates them. No module touches memory stores directly; everything goes through the Broker.

> Canonical detail: `../../knowledge/references/memory-architecture.md`. Load on demand.

---

## Purpose

Persist and retrieve what CATLX knows about the user and its history, with coherence across stores, so AI
calls are grounded in real context rather than the model's training data.

## When to activate

- User asks how CATLX remembers, stores facts/preferences, or recalls a past interaction.
- Configuring memory depth, compression, retrieval, or persistence.
- Resolving conflicting facts between semantic memory and the knowledge graph.
- Designing RAG context injection.

## What this skill handles

1. **Store taxonomy** — Episodic, Semantic, Workspace, Knowledge Graph (table in
   `../../knowledge/references/memory-architecture.md` §7.2).
2. **Episodic records** — timestamped records with transcript, intent, actions, workflow IDs,
   success/failure, feedback, and a **1536-dim embedding**; stored in `memory.db` and indexed in ChromaDB;
   retrievable via exact SQL and semantic vector search.
3. **Semantic memory** — the Semantic Extractor runs after every episodic write, extracting preferences,
   domain facts, and learned procedures as typed assertions with confidence and recency weights.
4. **Workspace memory** — volatile in-memory state (active window, open files, clipboard, last 20 commands,
   running workflows, focus); serialized to disk every 10 s; restore offered after abnormal shutdown.
5. **Knowledge graph** — property graph (kuzu, or SQLite on T0) of entities and edges (`works_on`, `owns`,
   `references`, `depends_on`, `scheduled_at`); multi-hop retrieval.
6. **Memory Broker** — single access point: write routing, read routing, coherence enforcement, compression
   scheduling.
7. **Coherence Protocol** — resolve conflicts: (1) user-confirmed facts highest, (2) most-recently-written,
   (3) higher-confidence; unresolvable conflicts surface as Memory Conflict alerts.
8. **Compression** — episodic merging, semantic de-duplication, vector index pruning (nightly / on
   threshold).
9. **Retrieval optimization (RAG)** — before every LLM call: top-k vector (k=10) + exact SQL for recent
   records + knowledge-graph 2-hop expansion; assemble and inject the context window.
10. **Long-term persistence** — WAL + periodic checkpointing; hourly graph checkpoint; daily backups;
    portable memory stores.

## Requirements / constraints

- **R6 (single access point):** no module interacts with stores directly; use the Memory Broker.
- **R4 (WAL):** `memory.db` uses WAL with periodic checkpointing.
- Tier-scaled memory depth (200 / 2000 / unlimited) and compression ratio (80% / 50% / preservation) —
  see `catlx-hardware-adaptation`.

## Canonical knowledge it reads

`../../knowledge/references/memory-architecture.md` · `../../knowledge/references/data-registries.md` ·
`../../knowledge/rules/architectural-rules.md`.

## Delegation

- **Embedding / retrieval / AI calls** → delegate to `catlx-ai-provider`
  (`skill({ name: "catlx-ai-provider" })`).
- **Writing episodic records as part of a workflow** → delegate to `catlx-workflow-engine`
  (`skill({ name: "catlx-workflow-engine" })`).
- **Memory degradation / compression on low resources** → delegate to `catlx-hardware-adaptation`
  (`skill({ name: "catlx-hardware-adaptation" })`).
- **Memory store persistence/portability across machines** → delegate to `catlx-portability`
  (`skill({ name: "catlx-portability" })`).

## Edge cases & warnings

- **Conflicting facts:** apply the coherence hierarchy; never silently pick a resolution; surface
  unresolved conflicts as alerts.
- **T0 storage limits:** compression is aggressive; watch retention.
- **Workspace restore:** only offer restore when the PID snapshot indicates an abnormal end; otherwise
  start clean.
- **Vector index corruption:** rebuild from embedding data in `memory.db` (see recovery).
- **Sensitive facts:** memory writes should respect privacy (no storing credentials; see `catlx-security`).

## Single memory authority & boundaries

`catlx-memory` is the **single, exclusive memory authority** for the entire agent stack. All long-term user
memory — episodic records, semantic facts/preferences, knowledge-graph entities, workspace state — is owned
here and only reachable through the Memory Broker.

- No other skill, gateway, or ecosystem may register, claim, or write **CATLX long-term memory keys**
  (`capability:*`, user facts, preferences, workspace snapshots).
- Domain ecosystems (e.g. BAKG) keep their own **session-scoped context internally** (e.g.
  `context/shared-state.md`) and do NOT write into CATLX memory stores.
- If another loaded skill mentions "memory key" or "long-term capability", route that memory work to this
  skill; do not treat the other skill's claim as a memory authority.

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

- **Source:** PART VII §7.1–7.11 (design principles, taxonomy, episodic, semantic, workspace, knowledge graph,
  broker, coherence, compression, retrieval optimization, long-term persistence).
- **Inferred:** none beyond Windows path mapping (`memory.db`, ChromaDB relative persistence path).
