# Workflow & State

The engine runs in **two improvement modes** sharing one memory store:

* **Cloud mode** (default): memory-based self-improvement (the cycle below).
* **Local mode**: same cycle **plus** a local-model fine-tuning improvement run at
  the end of each completed task/learning cycle — turn it on with
  `selfimprove mode local`, select your local model with
  `selfimprove local model …`, and close each loop with `selfimprove improve`.

Deterministic memory recording is identical in both modes. See
[local-mode.md](local-mode.md) for the Local-mode mechanism.

## Quick cycle

```text
[Before a task]  retrieve "…"            → guidance block from past lessons
[During]         record … --derive       → experience (+ auto lesson if clear)
[After session]  reflect --worked/…      → upsert a lesson (Do: / Avoid:)
                 (repeatedly validated)  → bump times_validated
[Daily]          consolidate             → merge dupes, confidence, promote to strong
                 (use --dry-run first)
[Oversight]      stats · list --status strong · audit · export · undo
```

## Where memory lives (workspace files)

By default the engine uses a directory under your **shared workspace** so memory
persists and travels with the project:

```
~/.selfimprove/
├── memory.db               # SQLite: lessons, experiences, audit log
└── memory-snapshot.json    # portable JSON snapshot (from `selfimprove export`)
```

Override the location with the `SELFIMPROVE_STATE_DIR` environment variable or the
`--state-dir` option — handy for tests and for keeping a given memory store per project.
Run everything against a throwaway dir to experiment without polluting real memory:

```bash
SELFIMPROVE_STATE_DIR=/tmp/mem-demo selfimprove record … # etc.
```

## Lifecycle of a lesson

```
            written            validated 3×          needs review
 active  ──────────────►  strong  ──────────────►  obsolete ──► archived(delete)
   ▲          ▲                │   confidence↓
   └──────────┴────────────────┘   (re-validated ⇒ back to active)
```

* `active`  — currently useful guidance.
* `strong`  — validated repeatedly; high-confidence long-term knowledge.
* `obsolete`— no longer true / superseded; excluded from retrieval by default.
* `archived`(via `delete`) — removed from live view but kept for audit/reversibility.
* `protected` — set explicitly; excluded from auto consolidation, merge, obsolete, delete.
