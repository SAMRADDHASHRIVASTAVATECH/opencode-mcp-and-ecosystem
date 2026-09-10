# Python API

## Open the engine

```python
from selfimprove.factory import open_engine
engine, config, store = open_engine()          # default workspace dir
# or: open_engine(state_dir="/tmp/mem")         # explicit directory
# or: set env SELFIMPROVE_STATE_DIR before import
```

## Core methods (`ExperienceEngine`)

| Method | Purpose |
|---|---|
| `record(action, outcome, error=None, fix=None, verdict=None, category=None, tags=None, derive_lesson=False)` | store an experience; optionally derive a lesson from a clear failure+fix or success+insight |
| `reflect_on(experience)` | convert a stored/loaded experience into a lesson |
| `reflect_session(session_label, what_worked=None, what_failed=None, fix=None, category=None, tags=None)` | end-of-session reflection (upserts `Do:`/`Avoid:` lessons) |
| `learn(statement, category=None, tags=None, source=None, confidence=None)` | explicit durable lesson |
| `retrieve(query, top_k=5, sources=None)` | ranked guidance block + matched lessons for a task |
| `list_lessons(status=None, category=None, tag=None)` | query lessons |
| `stats()` | counts by status/category |
| `consolidate(dry_run=False)` | daily cycle (merge dupes, confidence, obsolete, promote) |
| `promote(lesson_id)` | mark validated lesson strong |
| `mark_obsolete(lesson_id, reason)` | retire a lesson |
| `delete(lesson_id)` | archive (reversible), unless protected |
| `undo()` | revert last reversible lesson change (audited) |
| `get(lesson_id)` / `get_lesson` | fetch one lesson |
| `export(path=None)` / `import_(path)` | portable JSON snapshot |
| `.mode` (property) | current mode: `"cloud"` or `"local"` |
| `set_mode("local"|"cloud")` | switch improvement mode (audited, persistent) |
| `local_model()` / `set_local_model(model=…, base_model=…)` | select the local model being improved |

## Local improvement runner

```python
from selfimprove.factory import open_engine, improvement
eng, cfg, store = open_engine()
runner = improvement(eng, cfg)                 # binds to this engine+config

res = runner.run(dry_run=True)                 # preview dataset record count
res = runner.run()                             # build dataset (message gives the train cmd)
res = runner.run(invoke_trainer=True)          # fine-tune now via the Python trainer
```

`res` reports `records`, `dataset` path, `trainer` backend report, `trained`,
`output_dir`, `base_model`, and a human `message`. Runs are audit-logged
(`local.dataset`, `local.train`) and versioned under `<state>/local/checkpoints/`.
Requires mode `local`.

## Fine-tuning with the project's own Python trainer

```python
from selfimprove.trainer import run_fine_tune, backend_report
backend_report()                               # which ML modules are present
res = run_fine_tune(
    base_model="Qwen/Qwen2.5-Coder-7B-Instruct",
    dataset="<state>/local/run_<ts>.dataset.jsonl",
    output_dir="<state>/local/out", epochs=3, export_gguf=False)
```

`run_fine_tune` is pure Python (unsloth, or transformers+peft+trl fallback) and
writes a reversible LoRA adapter + merged model. LM Studio is never contacted.
Missing ML runtime raises a clean actionable error. See `docs/local-mode.md`.

Every create/update/promote/archive/undo is written through the audited store.

## Minimal example

```python
from selfimprove.factory import open_engine
e, cfg, store = open_engine()

e.learn("Keep MCP tool annotations constant; move arg spec to the description.",
        category="coding", tags=["python","mcp"])

e.record("registration", outcome="success", verdict="worked",
         what="constant annotations", category="coding", derive_lesson=True)

for _ in range(2):
    e.reflect_session("build-mcp", what_worked="constant annotations",
                      category="coding")   # → validated 3× total

report = e.consolidate(dry_run=True)        # preview promote/merge
e.consolidate()                             # promotes to strong (conf 0.8)

guidance = e.retrieve("make a python MCP tool")
store.close()                               # persist to memory.db
```

## Errors

`selfimprove.errors`: `EngineError`, `ProtectedLesson`, `NotFound`, `ValidationError`,
each exposing `.to_dict()`. Methods raise instead of silently mutating a protected lesson.
