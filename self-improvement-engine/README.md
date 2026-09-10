# Self-Improvement Engine

A **deterministic, auditable self-improvement system** with **two improvement
modes**, depending on which AI model is doing your work:

```
Experience → Reflection → Learning → Memory → Retrieval → Better Performance → New Experience
```

| Mode | What it does | When |
|---|---|---|
| **Cloud** (default) | Memory-based learning: records experiences, lessons, sessions into persistent memory and uses them to avoid repeating mistakes in future tasks. | Using a cloud model. |
| **Local LLM** | **Everything Cloud does, plus** a local-model self-improvement / fine-tuning mechanism. Each completed task or learning cycle accumulates *verified* learning and runs an improvement step that progressively fine-tunes the local model you load in **LM Studio**, making it more specialised and capable over time. | You explicitly tell the system you're using a local model via LM Studio. |

Both modes share the same persistent, audited memory store. Improvement happens
through validated knowledge only — the engine/assistant model and its safeguards
are never modified. In Local mode the improvement target is the **separate local
model you opt in to improving**, and every fine-tune is versioned and audited.

---

## Install

```bash
cd self-improvement-engine
python -m pip install -e .
selfimprove --help
```

Memory lives in workspace files (`~/.selfimprove/`, overridable via
`SELFIMPROVE_STATE_DIR` or `--state-dir`), so it persists across sessions.

## Cloud Mode (default) — CLI quick tour

```bash
# BEFORE a task: retrieve relevant past experience as guidance
selfimprove retrieve "building an MCP server with python"

# DURING/AFTER: record an experience (optionally auto-derive a lesson)
selfimprove record "mcp tool registration" --outcome failure \
    --error "NameError: local var in annotation" \
    --fix "keep annotations constant; put arg spec in the description" \
    --tag python --category coding --derive

# AFTER a session: reflection pass
selfimprove reflect --label "build-mcp" \
    --worked "Use constant annotations for MCP tool params" --category coding

# Explicit lessons / user corrections
selfimprove learn "Remove tests/ from the final deliverable after verifying" \
    --category workflow --tag deliverable

# Maintain
selfimprove stats && selfimprove consolidate && selfimprove export && selfimprove audit
```

## Local LLM Mode — when you're using a local model in LM Studio

Activate it and tell the system which local model does your tasks:

```bash
selfimprove mode local              # switch on Local mode (persists)
selfimprove local model qwen2.5-coder-7b \
    --base "Qwen/Qwen2.5-Coder-7B-Instruct"   # select the model you use
selfimprove local                   # status: mode, model, server, trainer
```

In Local mode, at the **end of every completed task or learning cycle**, the agent
hands the data it collected to this project's **own Python fine-tuner**:

```bash
selfimprove improve                 # build the fine-tuning dataset
selfimprove improve --dry-run       # preview record count & paths
selfimprove improve --train         # fine-tune now with this project's Python code
```

`selfimprove improve`:
1. **Builds a verified fine-tuning dataset** (`~/.selfimprove/local/run_*.dataset.jsonl`)
   from accumulated **verified** lessons + experiences (chat `messages` JSONL).
2. **Hands it to the Python trainer** (`selfimprove.trainer`), which runs the real
   LoRA/full fine-tune producing a versioned checkpoint under
   `~/.selfimprove/local/checkpoints/<run>/`.

The fine-tune is done **entirely by Python code in this project** — LM Studio is
never part of training and is never contacted. You only **load** the finished
adapter/merged model into LM Studio afterwards. Fine-tuning is reversible:
checkpoints are versioned, prior runs are kept, and the active model target is
stored so you can point back at an earlier checkpoint at any time.

To fine-tune a specific dataset directly (the "call this code with the data it
did" path), run the Python trainer yourself:

```bash
selfimprove train --data run_<ts>.dataset.jsonl \
    --model "Qwen/Qwen2.5-Coder-7B-Instruct" --output ~/.selfimprove/local/out \
    [--gguf]        # --gguf also exports an LM Studio/llama.cpp GGUF
```

## Command summary

`record`, `reflect`, `learn`, `retrieve`, `list`, `stats`, `consolidate`, `obsolete`,
`forget`, `undo`, `export`, `import`, `audit`, `mode` (cloud|local), `local`
(status|model), `improve` (`--dry-run` `--train`).

See `docs/architecture.md`, `docs/workflow.md`, `docs/api.md`, `docs/local-mode.md`.
