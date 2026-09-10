# Memory Architecture — Canonical Reference

> Source: PART VII — MEMORY ARCHITECTURE. The single authoritative source for the memory store taxonomy,
> the Memory Broker, the coherence protocol, compression, retrieval optimization, and long-term
> persistence.

## 7.1 Design Principles
Memory is modeled after human cognitive memory. Multiple distinct stores serve different retrieval
patterns and retention requirements. All stores are coordinated by the **Memory Broker**, which ensures
coherence, resolves conflicts, and routes retrieval requests to the optimal store.

## 7.2 Memory Store Taxonomy

| Memory type | Description |
|---|---|
| **Episodic Memory** | Timestamped records of events (what happened, when, who, result). Analogous to human autobiographical memory. |
| **Semantic Memory** | Factual knowledge extracted from interactions: user preferences, domain facts, learned procedures. Analogous to general knowledge. |
| **Workspace Memory** | Short-lived working context: current task state, open files, active workflows, clipboard. Expires when the session ends. |
| **Knowledge Graph Memory** | Relationship graph between entities (person → project → deadline → file). Enables complex multi-hop queries. |

## 7.3 Episodic Memory
Every interaction is recorded as an **EpisodicRecord**: timestamp, voice transcript, intent resolved,
actions taken, workflow IDs, success/failure status, user feedback signal, and a **1536-dim embedding
vector**. Stored in `memory.db` (SQLite) and indexed in ChromaDB (vector store). Retrieval supports exact
SQL queries ("show me all file operations from last Tuesday") and semantic vector search ("what did I ask
you about the project budget?").

## 7.4 Semantic Memory
Stores user-specific and domain-specific knowledge extracted from episodic interactions. The **Semantic
Extractor** runs after every episodic write, scanning for extractable facts: user preferences (e.g.
"prefers dark mode"), domain knowledge (project codenames, key contacts, file naming conventions), and
learned procedures ("when asked to submit a report, always CC the manager"). Stored as typed assertions
with confidence scores and recency weights.

## 7.5 Workspace Memory
A volatile in-memory store tracking the current desktop state: active window, open file paths, recent
clipboard content, the last 20 voice commands, the state of any running workflows, and the current focus
context. Serialized to disk every **10 seconds** as a workspace snapshot for crash recovery. On startup,
if a snapshot exists from a session that ended abnormally (crash detected via PID file), CATLX offers to
restore the previous workspace state.

## 7.6 Knowledge Graph Memory
A property graph database (kuzu, or a SQLite-based lightweight alternative on T0). Nodes = entities
(people, projects, files, applications, domains). Edges = relationships (`works_on`, `owns`, `references`,
`depends_on`, `scheduled_at`). Every significant interaction referencing multiple entities creates or
reinforces edges. Enables multi-hop retrieval: "Find all files related to the project that Alice
mentioned last month."

## 7.7 Memory Broker
The single access point for all memory operations. No module interacts with memory stores directly. It
handles: **write routing** (which stores for a record type), **read routing** (which stores for a
retrieval request), **coherence enforcement** (no conflicting facts across stores), and **compression
scheduling**.

## 7.8 Memory Coherence Protocol
When a fact exists in both Semantic Memory and the Knowledge Graph with conflicting values, the
Coherence Protocol resolves via prioritization: (1) **user-confirmed facts** highest, (2) **most-recently
-written** supersede older, (3) **higher-confidence** supersede lower. Conflicts that cannot be
auto-resolved surface as **Memory Conflict alerts** in the dashboard.

## 7.9 Memory Compression
On T0, memory depth is limited by storage and retrieval speed. The Memory Compressor runs nightly (or
when size exceeds a threshold) and applies: **episodic merging** (merge multiple low-significance
episodes from a session into one summary record), **semantic de-duplication** (merge semantically
equivalent facts), and **vector index pruning** (drop embeddings older than a configurable retention
window).

## 7.10 Retrieval Optimization (RAG)
Before every LLM call the Memory Broker performs a fast retrieval pass: **top-k semantic vector search
(k=10)** + **exact SQL match** for recent episode records + **Knowledge Graph 2-hop neighborhood
expansion** around mentioned entities. The resulting context window is assembled and injected into the
LLM prompt, giving the model access to relevant historical context without relying on its training data.

## 7.11 Long-Term Persistence
Designed for indefinite retention. SQLite uses WAL mode with periodic checkpointing. Vector indexes
persist to disk after every write batch. Knowledge Graph is checkpointed hourly. Full memory backups
export to a user-configured backup location (local or network share) on a daily schedule. Memory stores
are portable — transferable to a new machine and fully restored, giving continuity across hardware
upgrades.

## Cross-references
- Consumed by: `skills/catlx-memory/SKILL.md`.
- Delegates to: `catlx-ai-provider` (embedding via PAL), `catlx-workflow-engine`, `catlx-security`.
- Data registry: `memory.db`; vector store ChromaDB; graph kuzu. See `knowledge/references/data-registries.md`.
- Source tree: `knowledge/references/folder-structure.md` (`memory/`).
