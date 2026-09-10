# Architecture

## Layers

| Module | Responsibility |
|---|---|
| `model.py` | `Lesson` + `Experience` dataclasses, statuses (active/strong/obsolete/archived), sources, protected flag |
| `store.py` | SQLite persistence in workspace files; versioned head; **audit/undo log**; JSON export/import |
| `engine.py` | the learning loop: record → reflect → learn → retrieve → consolidate → promote |
| `mode.py` | improvement mode (cloud/local), persistent local-model config |
| `improve.py` | Local-mode mechanism: deterministic fine-tune dataset build + improvement-run registry |
| `trainer.py` | the project's own Python fine-tuner (unsloth / transformers+peft+trl), no external server |
| `factory.py` | open engine + portable snapshot helpers + `improvement()` runner |
| `main.py` | CLI |

## Two modes (cloud vs local)

`mode.py` stores the active mode in the memory DB. **Cloud mode** uses only the
memory learning loop below. **Local mode** adds, at each completed task/learning
cycle, an `ImprovementRun` (`improve.py`) that turns verified memory into a
fine-tuning dataset and hands it to the project's own Python trainer
(`trainer.py`) — which performs the LoRA/full fine-tune and produces a versioned
checkpoint. The separate local model you opt in to improving is the only
fine-tune target; no external server (LM Studio) is part of training. Deterministic
memory behaviour is identical in both modes; see [local-mode.md](local-mode.md).

## The learning loop (`ExperienceEngine`)

* **record** — store a raw `Experience` (action, outcome, error/fix/verdict, category,
  tags). Optionally auto-derive a lesson.
* **reflect_on** — one experience → lesson (`Do:` for success with an insight,
  `Avoid: ...` for a failure + its fix).
* **reflect_session** — end-of-session reflection from what worked / what failed; upserts
  (deduplicates) lessons by normalized statement.
* **learn** — explicit durable lesson (e.g. from a user correction or discovery).
* **retrieve** — rank relevant active/strong lessons for a new task by token overlap +
  tag match + confidence (+ strong bonus), with a fuzzy fallback, returning a human
  guidance block.
* **consolidate** (daily) — merge duplicate identities (summing counters), recompute
  confidence from the validation ratio, **promote** lessons validated ≥3× to `strong`,
  and archive/remove as configured. Dry-run supported.
* **promote** — repeatedly validated lessons become `strong` long-term knowledge.

## Dedup & identity

A lesson's identity is its normalized statement. Re-recording the same insight increments
`times_seen` / `times_validated` instead of creating a duplicate. `consolidate` merges any
stragglers.

## Confidence

`confidence = 0.3 + 0.7 * validated / (seen + 2)`; strong lessons floor at 0.8. This is a
deterministic measure of how often a lesson has been verified — not fabricated.

## Versioning, reversibility, audit

Every mutating write:
* increments the lesson `version`,
* appends an audit row (`action`, `entity`, before/after JSON),
* the store keeps a head version counter.

`undo` walks the audit log (scanning past non-lesson rows) and restores the previous state
for the most recent reversible lesson change. `export` writes a portable JSON snapshot to
the workspace. `import` loads one back.

## Protection

Lessons may be marked `protected`. Protected lessons are skipped by consolidation,
duplicate-merge, obsolete-marking and delete — enforcing the "do not blindly modify
safeguards / critical knowledge" guardrail. (Protection itself is set intentionally, e.g.
for security guardrail lessons.)
