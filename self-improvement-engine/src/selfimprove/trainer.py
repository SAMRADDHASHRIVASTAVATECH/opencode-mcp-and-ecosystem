"""Self-contained Python fine-tuner for Local LLM mode.

This module IS the thing that fine-tunes. It takes a dataset the agent/engine
collected (JSONL of OpenAI ``messages``) plus a base model, and runs a real
LoRA / full fine-tune producing versioned checkpoints that you load back into
LM Studio. LM Studio is never involved in training.

Run directly:
    python -m selfimprove.trainer --model BASE --data data.jsonl --output out
Or via the CLI (the agent-facing entry point):
    selfimprove train --data data.jsonl --model BASE --output out [--gguf]

Requires an ML runtime where it is invoked (your GPU machine):
    pip install torch transformers peft trl datasets accelerate
    # optional, for 4-bit + GGUF (LM Studio-ready) output:
    pip install 'unsloth[colab-new]' bitsandbytes
If that stack is absent this raises a clean, actionable error instead of a
traceback. The heavy imports below are lazy so the rest of the engine works
without them.
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import sys
import time
from pathlib import Path

REQUIRED_PIP = "pip install torch transformers peft trl datasets accelerate"
UNSLOTH_PIP = "pip install 'unsloth[colab-new]' bitsandbytes"


def backend_report() -> dict:
    import importlib.util
    return {m: bool(importlib.util.find_spec(m)) for m in
            ("torch", "transformers", "trl", "peft", "datasets",
             "unsloth", "bitsandbytes", "accelerate")}


def _require(mod: str, hint: str) -> None:
    import importlib.util
    if importlib.util.find_spec(mod) is None:
        raise RuntimeError(
            f"Local fine-tuning needs '{mod}', which is not installed here.\n"
            f"Install the ML runtime where this runs (a GPU machine), e.g.:\n"
            f"    {hint}\n"
            f"The dataset is already ready to train on; nothing about LM Studio "
            f"is needed for training.")


def run_fine_tune(*, base_model: str, dataset: str, output_dir: str,
                  epochs: int = 3, learning_rate: float = 2e-4,
                  max_seq_length: int = 2048, export_gguf: bool = False,
                  seed: int = 42) -> dict:
    """Fine-tune ``base_model`` on the JSONL dataset in ``dataset``.

    Deterministic seed; results written under ``output_dir``. Pure Python - the
    project's own training code, no external model server.
    """
    ds_path = Path(dataset)
    if not ds_path.exists():
        raise FileNotFoundError(f"dataset not found: {dataset}")
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    record_count = sum(1 for _ in ds_path.open(encoding="utf-8")
                       if _.strip())

    # ---- imports (lazy; fail cleanly if the ML runtime is missing) ---------
    _require("torch", REQUIRED_PIP)
    _require("transformers", REQUIRED_PIP)
    _require("trl", REQUIRED_PIP)
    _require("peft", REQUIRED_PIP)
    _require("datasets", REQUIRED_PIP)
    if export_gguf:
        _require("unsloth", "unsloth[colab-new] " + REQUIRED_PIP)

    import datasets as hf_datasets
    import torch

    raw = hf_datasets.load_dataset("json", data_files=str(ds_path),
                                   split="train")

    have_unsloth = importlib_has("unsloth")
    use_unsloth = have_unsloth

    result = {"base_model": base_model, "dataset": str(ds_path),
              "records": record_count, "output_dir": str(out),
              "seed": seed, "backend": "unsloth" if use_unsloth else "transformers+peft+trl",
              "export_gguf": export_gguf, "started": time.time()}

    if use_unsloth:
        from unsloth import FastLanguageModel, is_bfloat16_supported
        from trl import SFTTrainer, SFTConfig
        model, tokenizer = FastLanguageModel.from_pretrained(
            model_name=base_model, max_seq_length=max_seq_length,
            dtype=None, load_in_4bit=True)
        model = FastLanguageModel.get_peft_model(
            model, r=16,
            target_modules=["q_proj", "k_proj", "v_proj", "o_proj",
                            "gate_proj", "up_proj", "down_proj"],
            lora_alpha=16, lora_dropout=0, bias="none",
            use_gradient_checkpointing="unsloth")

        def fmt(examples):
            return {"text": [tokenizer.apply_chat_template(m, tokenize=False)
                             for m in examples["messages"]]}
        ds = raw.map(fmt, batched=True)
        tr = SFTTrainer(model=model, tokenizer=tokenizer, train_dataset=ds,
                        args=SFTConfig(
                            dataset_text_field="text",
                            max_seq_length=max_seq_length,
                            per_device_train_batch_size=2,
                            gradient_accumulation_steps=4, warmup_steps=5,
                            num_train_epochs=epochs,
                            learning_rate=learning_rate,
                            fp16=not is_bfloat16_supported(),
                            bf16=is_bfloat16_supported(),
                            logging_steps=1, seed=seed,
                            output_dir=str(out / "training"), report_to="none"))
        tr.train()
        # Reversible: save the LoRA adapter AND a merged model.
        tr.save_model(str(out / "adapter"))
        model.save_pretrained_merged(str(out / "merged"), tokenizer,
                                     save_method="merged_16bit")
        if export_gguf:
            model.save_pretrained_gguf(str(out / "gguf"), tokenizer,
                                       quantization_method="q4_k_m")
            result["gguf_dir"] = str(out / "gguf")
    else:
        # Plain transformers + peft + trl (CPU/GPU, no 4-bit, no GGUF).
        from transformers import (AutoModelForCausalLM, AutoTokenizer,
                                  TrainingArguments)
        from peft import LoraConfig, get_peft_model
        from trl import SFTTrainer
        model = AutoModelForCausalLM.from_pretrained(base_model,
                                                     torch_dtype="auto")
        tokenizer = AutoTokenizer.from_pretrained(base_model)
        if tokenizer.pad_token is None:
            tokenizer.pad_token = tokenizer.eos_token

        def fmt(examples):
            return {"text": [tokenizer.apply_chat_template(m, tokenize=False)
                             for m in examples["messages"]]}
        ds = raw.map(fmt, batched=True)
        lora = LoraConfig(r=16, lora_alpha=16, target_modules=[
            "q_proj", "k_proj", "v_proj", "o_proj",
            "gate_proj", "up_proj", "down_proj"], lora_dropout=0.0)
        model = get_peft_model(model, lora)
        tr = SFTTrainer(model=model, tokenizer=tokenizer, train_dataset=ds,
                        args=TrainingArguments(
                            output_dir=str(out / "training"),
                            per_device_train_batch_size=2,
                            gradient_accumulation_steps=4,
                            num_train_epochs=epochs,
                            learning_rate=learning_rate,
                            logging_steps=1, seed=seed, report_to="none"))
        tr.train()
        tr.save_model(str(out / "adapter"))
        merged = model.merge_and_unload()
        merged.save_pretrained(str(out / "merged"))
        tokenizer.save_pretrained(str(out / "merged"))

    result["finished"] = time.time()
    result["trained"] = True
    result["message"] = "fine-tune complete -> " + str(out)
    (out / "run.json").write_text(json.dumps(result, ensure_ascii=False,
                                             indent=2), encoding="utf-8")
    (out / "done.txt").write_text("ok\n")
    return result


def importlib_has(name: str) -> bool:
    import importlib.util
    return importlib.util.find_spec(name) is not None


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(
        prog="selfimprove.trainer",
        description="Self-contained Python fine-tuner (Local LLM mode).")
    ap.add_argument("--model", required=True, help="base model (HF repo or local path)")
    ap.add_argument("--data", required=True, help="JSONL dataset of messages to train on")
    ap.add_argument("--output", required=True, help="output checkpoint directory")
    ap.add_argument("--epochs", type=int, default=3)
    ap.add_argument("--lr", type=float, default=2e-4)
    ap.add_argument("--max-seq-length", type=int, default=2048)
    ap.add_argument("--gguf", action="store_true",
                    help="also export an LM Studio/llama.cpp GGUF (needs unsloth)")
    a = ap.parse_args(argv)
    try:
        res = run_fine_tune(base_model=a.model, dataset=a.data,
                            output_dir=a.output, epochs=a.epochs,
                            learning_rate=a.lr,
                            max_seq_length=a.max_seq_length,
                            export_gguf=a.gguf)
        print(json.dumps(res, ensure_ascii=False, indent=2, default=str))
        return 0
    except RuntimeError as e:                       # backend missing -> clean msg
        print(str(e), file=sys.stderr)
        return 3
    except Exception as e:                          # noqa
        print(f"ERROR: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
