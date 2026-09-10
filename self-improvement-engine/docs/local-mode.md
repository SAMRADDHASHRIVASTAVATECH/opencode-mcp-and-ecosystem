# Local LLM Self-Improvement Mode

The engine runs in two modes that share one persistent, audited memory store:

- **Cloud mode** (default) — memory-based self-improvement only.
- **Local mode** — memory-based learning **plus** progressive fine-tuning of the
  local model you use for tasks, so it becomes more specialised, more capable, and
  better adapted to your system over time.

**The fine-tuning is executed by Python code in this project — never by LM
Studio.** LM Studio is only the *viewer* where you load the finished
adapter/merged model afterwards; it is never contacted during training.

## Activation

Local mode is **explicit** — it only turns on when you say you are using a local
model:

```bash
selfimprove mode local
selfimprove local model qwen2.5-coder-7b \
    --base "Qwen/Qwen2.5-Coder-7B-Instruct"    # pick the model that does your tasks
```

The choice is stored persistently (memory DB `kv`). Switch back any time with
`selfimprove mode cloud`. The **base model** is the thing fine-tuned; the
**model** is the human-friendly id of what you load in LM Studio afterwards.

## Improvement cycle (end of each completed task / learning cycle)

Local mode does not change how memory is recorded. At the end of a task the agent
hands the data it collected to the Python trainer:

```bash
# normal memory learning for the session...
selfimprove record ... ; selfimprove reflect ... ; selfimprove learn ...
# close the loop - build the dataset then fine-tune:
selfimprove improve --train     # or: selfimprove improve  then  selfimprove train --data <ds>
```

`selfimprove improve` builds the dataset and, with `--train`, invokes the Python
fine-tuner (`selfimprove.trainer`) on a configured base model. Alternatively call
the trainer directly on any dataset with:

```bash
selfimprove train --data run_<ts>.dataset.jsonl \
    --model "Qwen/Qwen2.5-Coder-7B-Instruct" \
    --output ~/.selfimprove/local/out [--gguf]
```

This is the intended agent-facing call: hand it the dataset produced from the
task's experiences and it performs the fine-tune.

## What a Local run produces (in `<state>/local/`)

```
local/
├── run_<ts>.dataset.jsonl      # verified fine-tuning data (chat "messages" JSONL)
├── run_<ts>.metadata.jsonl     # per-record provenance (lesson id, validated, source)
└── checkpoints/run_<ts>/       # versioned trainer output:
    ├── training/               #   TrainerState (step logs / checkpoints)
    ├── adapter/                #   swappable LoRA adapter (reversible)
    ├── merged/                 #   merged 16-bit model
    ├── gguf/                   #   (only with --gguf) LM Studio/llama.cpp GGUF
    ├── run.json                #   full run report
    └── done.txt
```

Every run is audit-logged as `local.dataset` and `local.train` so improvement is
traceable and reversible.

## The Python trainer (`src/selfimprove/trainer.py`)

`run_fine_tune(base_model=…, dataset=…, output_dir=…, …)` is self-contained Python:

- preferred backend **unsloth** (4-bit LoRA, `--gguf` export);
- fallback backend plain `transformers` + `peft` + `trl` (works without unsloth);
- both save a reversible **LoRA adapter** and a **merged** model, so you can either
  keep the base intact (adapter) or replace the target model (merged);
- lazy heavy imports: if the ML runtime isn't installed it raises a **clean,
  actionable** error (never a traceback).

Requires an ML runtime where it runs (your GPU machine):
`pip install torch transformers peft trl datasets accelerate` (+
`unsloth[colab-new] bitsandbytes` for 4-bit/GGUF).

## Verified-learning dataset

Training records are built **deterministically** from stored knowledge — a lesson is
included when it is *verified*: `strong`, `times_validated >= 1`, or its source is a
success or a direct user correction. `Protected` lessons are always honoured and
included verbatim. Records distinguish:

- `Do:` / success / discovery lessons → the correct approach for a task domain;
- `Avoid:` lessons → what not to repeat and the fix that worked;
- `user_correction` lessons → a direct instruction to follow;
- failure/success experiences → concrete mistake→fix demonstrations.

Nothing is fabricated by a model; there is no dependency on any running server.

## Auto-detection & `--train`

`selfimprove improve --train` reports which Python trainer backend is usable
(`detect_trainer()`), requires a configured **base model**, then invokes the trainer.
If no ML runtime or no base model is present it reports exactly what to install/run
and leaves the dataset ready — it never fails silently and never falls back to an
external server.

## Safety

- The engine/assistant model and its safeguards/security controls are never touched.
- In Local mode only the separately chosen local model is a fine-tune target.
- Checkpoints are versioned and kept; `local model … --base …` can point at a new
  base or an earlier checkpoint at any time. Adapter output is non-destructive to
  the base; a merged snapshot is saved alongside only when you fine-tune.
