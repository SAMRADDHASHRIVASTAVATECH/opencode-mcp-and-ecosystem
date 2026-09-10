"""Local LLM self-improvement cycle (Local mode).

Turns the engine's *verified* persistent learning into a fine-tuning dataset
and hands it to the project's own Python trainer (`selfimprove.trainer`) to
produce progressively better local checkpoints. LM Studio is not involved in
training at all - it only ever *loads* a finished adapter/model afterwards.

Runs are recorded in an audited, versioned registry under ``<state>/local/`` so
improvement stays controlled and reversible. Dataset construction is
deterministic: records are derived from the stored verified knowledge fields,
never fabricated by a model.
"""
from __future__ import annotations

import json
import time
from pathlib import Path

from . import model as M
from . import mode as MO
from .errors import ValidationError

SYSTEM_PERSONA = (
    "You are an AI assistant that performs {category} tasks for the user and "
    "continuously improves from verified experience."
)


def _verified(lesson: dict) -> bool:
    """A lesson is 'verified' learning worth training on."""
    if lesson.get("protected"):
        return True                     # protected lessons are always honoured
    src = lesson.get("source")
    return (lesson.get("status") == M.STRONG
            or int(lesson.get("times_validated", 0)) >= 1
            or src in (M.SOURCE_SUCCESS, M.SOURCE_CORRECTION))


# --------------------------------------------------------------------------- #
# Dataset building (deterministic, from stored verified knowledge)
# --------------------------------------------------------------------------- #
def build_dataset(engine, *, include_experiences=True, max_experiences=8,
                  only_verified=True) -> list[dict]:
    """Turn verified memory into an ordered list of fine-tuning records."""
    records = []
    lessons = sorted(engine.store.list_lessons(),
                     key=lambda l: -float(l.get("confidence", 0)))
    for l in lessons:
        if l.get("status") in (M.ARCHIVED, M.OBSOLETE):
            continue
        if only_verified and not _verified(l):
            continue
        rec = _lesson_record(l)
        if rec:
            records.append(rec)
    if include_experiences:
        for e in engine.store.list_experiences(limit=100000)[:max_experiences]:
            rec = _experience_record(e)
            if rec:
                records.append(rec)
    return records


def _lesson_record(l: dict):
    statement = (l.get("statement") or "").strip()
    if not statement:
        return None
    category = l.get("category") or "general"
    detail = (l.get("detail") or "").strip()
    context = (l.get("context") or "").strip()
    tags = " ".join("#" + t for t in l.get("tags", []))
    sys = SYSTEM_PERSONA.format(category=category)

    if statement.lower().startswith("avoid"):
        body = (f"While doing this task do NOT do the following. Reason: it failed.\n"
                f"{statement}")
        if detail:
            body += f"\nHow to handle it instead: {detail}"
        if context:
            body += f"\nContext: {context}"
        user_q = f"Avoid making this mistake during {category} tasks."
    elif l.get("source") == M.SOURCE_CORRECTION:
        body = f"Follow this rule for {category} tasks: {statement}"
        if detail:
            body += f"\nDetails: {detail}"
        user_q = f"Remember and apply this rule in future {category} tasks."
    else:
        body = (f"When working on {category} tasks, apply this verified approach:\n"
                f"{statement}")
        if detail:
            body += f"\n{detail}"
        if context:
            body += f"\nApplies when: {context}"
        user_q = f"What is the right way to handle a {category} task?"
    if tags:
        body += f"\nTags: {tags}"
    return {"messages": [
        {"role": "system", "content": sys},
        {"role": "user", "content": user_q},
        {"role": "assistant", "content": body},
    ], "metadata": {
        "kind": "lesson", "lesson_id": l.get("id"), "statement": statement,
        "status": l.get("status"), "times_validated": l.get("times_validated", 0),
        "confidence": l.get("confidence"), "source": l.get("source"),
        "protected": l.get("protected", False),
    }}


def _experience_record(e: dict):
    action = (e.get("action") or "").strip()
    if not action:
        return None
    category = e.get("category") or "general"
    fix = (e.get("fix") or "").strip()
    error = (e.get("error") or "").strip()
    verdict = (e.get("verdict") or "").strip()
    sys = SYSTEM_PERSONA.format(category=category)
    if e.get("outcome") == M.OUTCOME_FAIL and error:
        ans = f"You attempted \"{action}\" and it failed ({error})."
        ans += f" The fix that worked: {fix}." if fix \
            else " Analyse the cause before retrying."
    elif e.get("outcome") == M.OUTCOME_OK and verdict:
        ans = f"\"{action}\" succeeds when {verdict}."
    else:
        return None
    return {"messages": [
        {"role": "system", "content": sys},
        {"role": "user", "content": f"Record what happened with \"{action}\"."},
        {"role": "assistant", "content": ans},
    ], "metadata": {"kind": "experience", "experience_id": e.get("id"),
                    "outcome": e.get("outcome")}}


def detect_trainer() -> dict:
    """Report which Python trainer backend is usable right here."""
    override = (__import__("os").environ.get("SELFIMPROVE_TRAINER", "")
                .strip().lower())
    if override:
        return {"backend": override, "source": "env override",
                "ready": override in ("unsloth", "transformers", "full")}
    from . import trainer as T
    have = T.backend_report()
    ready = all(have.get(m) for m in
                ("torch", "transformers", "trl", "peft", "datasets"))
    backend = "unsloth" if have.get("unsloth") and ready \
        else ("transformers+peft+trl" if ready else "")
    return {"backend": backend, "ready": bool(backend), "modules": have,
            "source": "auto-detect"}


class ImprovementRun:
    """One Local-mode improvement cycle: dataset -> Python fine-tune."""

    def __init__(self, engine, cfg):
        self.engine = engine
        self.store = engine.store
        self.cfg = cfg
        self.local_dir = Path(cfg.local_dir)
        self.checkpoints = self.local_dir / "checkpoints"
        self.local_dir.mkdir(parents=True, exist_ok=True)
        self.checkpoints.mkdir(parents=True, exist_ok=True)

    def run(self, *, dry_run=False, invoke_trainer=False,
            only_verified=True) -> dict:
        if MO.get_mode(self.store) != MO.MODE_LOCAL:
            raise ValidationError(
                "Local improvement requires Local mode. Run `selfimprove mode local` "
                "first.")
        lmodel = MO.get_local_model(self.store)

        records = build_dataset(self.engine, only_verified=only_verified)
        run_id = f"run_{int(time.time()*1000)}"
        dataset_path = self.local_dir / f"{run_id}.dataset.jsonl"
        meta_path = self.local_dir / f"{run_id}.metadata.jsonl"
        out_dir = self.checkpoints / run_id

        base = {"run_id": run_id, "records": len(records),
                "dataset": str(dataset_path), "model": lmodel.get("model"),
                "base_model": lmodel.get("base_model"),
                "output_dir": str(out_dir)}
        if dry_run:
            return {**base, "dry_run": True}

        # write deterministic dataset (+ provenance metadata sidecar)
        with open(dataset_path, "w", encoding="utf-8") as f:
            for r in records:
                f.write(json.dumps(r["messages"], ensure_ascii=False) + "\n")
        with open(meta_path, "w", encoding="utf-8") as f:
            for r in records:
                f.write(json.dumps(r.get("metadata", {}), ensure_ascii=False)
                        + "\n")

        self.store.log("local.dataset", "local", run_id,
                       after={"path": str(dataset_path), "records": len(records)})

        backend = detect_trainer()
        result = {**base, "trainer": backend}
        if invoke_trainer:
            if not lmodel.get("base_model"):
                result["trained"] = False
                result["message"] = ("base model not configured. Set it with "
                                     "`selfimprove local model NAME --base BASE` "
                                     "then retry, or run the trainer directly:")
                result["message"] += (f"\n  selfimprove train --data {dataset_path}"
                                      " --model BASE --output <dir>")
            elif not backend["ready"]:
                result["trained"] = False
                result["message"] = (
                    "No Python ML runtime detected here. The dataset is ready at "
                    f"{dataset_path}. On a GPU machine install "
                    "`torch transformers peft trl datasets accelerate` "
                    "(+ `unsloth[colab-new]` for 4-bit/GGUF) and run:\n"
                    f"  selfimprove train --data {dataset_path} "
                    f"--model {lmodel['base_model']} --output {out_dir}")
            else:
                from . import trainer as T
                try:
                    trained = T.run_fine_tune(
                        base_model=lmodel["base_model"],
                        dataset=str(dataset_path), output_dir=str(out_dir))
                    result.update(trained)
                    result["trained"] = True
                    result["message"] = trained["message"]
                except Exception as e:            # noqa
                    result["trained"] = False
                    result["message"] = f"fine-tune failed: {e}"
        else:
            result["trained"] = False
            result["message"] = ("dataset ready. To fine-tune with this Python code:"
                                 f"\n  selfimprove train --data {dataset_path} "
                                 f"--model {lmodel['base_model'] or '<BASE>'} "
                                 f"--output {out_dir}")

        self.store.log("local.train", "local", run_id, after=result)
        return result
