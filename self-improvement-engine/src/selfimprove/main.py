"""CLI for the self-improvement / experience-memory engine.

Commands:
  record      record a raw experience (may auto-derive a lesson)
  learn       explicitly store a lesson
  reflect     reflection pass after a session/task
  retrieve    search memory for guidance relevant to a new task
  list        list lessons (optionally by status/category)
  stats       memory statistics
  consolidate run the daily consolidation cycle
  obsolete    mark a lesson obsolete
  forget      archive a lesson (reversible)
  undo        revert the last lesson-mutating change
  export      write a portable JSON snapshot
  import      load lessons/experiences from a JSON snapshot
  audit       show the audit/undo log
  mode        show/set improvement mode (cloud | local)
  local       local-mode status / select the local model
  improve     local cycle: build fine-tune dataset (+ optional --train)
  train       fine-tune a local model with this project's Python trainer
"""
from __future__ import annotations

import argparse
import json
import sys

from .factory import open_engine


def _print(obj):
    print(json.dumps(obj, ensure_ascii=False, indent=2, default=str))


def main(argv=None):
    ap = argparse.ArgumentParser(prog="selfimprove",
                                 description="Experience-memory self-improvement "
                                             "engine")
    ap.add_argument("--state-dir", default="", help="Memory state dir "
                    "(default ~/.selfimprove in the workspace).")
    sub = ap.add_subparsers(dest="cmd", required=True)

    def add(name, help_):
        return sub.add_parser(name, help=help_)

    p = add("record", "Record an experience (optionally derive a lesson)")
    p.add_argument("action")
    p.add_argument("--outcome", choices=["success", "failure"], required=True)
    p.add_argument("--error", default="")
    p.add_argument("--fix", default="")
    p.add_argument("--verdict", default="")
    p.add_argument("--detail", default="")
    p.add_argument("--category", default="general")
    p.add_argument("--tag", action="append", default=[])
    p.add_argument("--derive", action="store_true",
                   help="Auto-derive a lesson from this experience.")

    p = add("learn", "Store an explicit lesson")
    p.add_argument("statement")
    p.add_argument("--detail", default="")
    p.add_argument("--category", default="general")
    p.add_argument("--tag", action="append", default=[])
    p.add_argument("--source", default="discovery")

    p = add("reflect", "Reflection pass after a session/task")
    p.add_argument("--label", default="session")
    p.add_argument("--worked", default="")
    p.add_argument("--failed", default="")
    p.add_argument("--fix", default="")
    p.add_argument("--category", default="general")

    p = add("retrieve", "Retrieve relevant experience for a task")
    p.add_argument("task")
    p.add_argument("--limit", type=int, default=6)

    p = add("list", "List lessons")
    p.add_argument("--status", default="")
    p.add_argument("--category", default="")

    p = add("stats", "Memory statistics")

    p = add("consolidate", "Daily consolidation cycle")
    p.add_argument("--dry-run", action="store_true")

    p = add("obsolete", "Mark a lesson obsolete")
    p.add_argument("lesson_id")
    p.add_argument("--reason", default="")

    p = add("forget", "Archive a lesson (reversible)")
    p.add_argument("lesson_id")

    p = add("undo", "Revert the last lesson-mutating change")

    p = add("export", "Write a portable JSON snapshot")
    p.add_argument("--path", default="")

    p = add("import", "Load a JSON snapshot")
    p.add_argument("path")

    p = add("audit", "Show audit log")
    p.add_argument("--limit", type=int, default=30)

    p = add("mode", "Show or set improvement mode: cloud (memory) or local (memory + local model fine-tuning)")
    p.add_argument("value", nargs="?", default="",
                   help="cloud | local (omit to print current mode)")

    p = add("local", "Local LLM mode status/config")
    p.add_argument("action", nargs="?", default="status",
                   choices=["status", "model"], help="default: status")
    p.add_argument("model", nargs="?", default="",
                   help="name/id of the local model that performs your tasks")
    p.add_argument("--base", default="", help="base model to fine-tune (path or HF repo)")

    p = add("improve", "Run the Local-mode improvement cycle (build dataset; optionally fine-tune)")
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--train", action="store_true",
                   help="Invoke the Python fine-tuner now (needs base model + ML runtime)")
    p.add_argument("--include-unverified", action="store_true",
                   help="Also emit non-verified lessons into the dataset")

    p = add("train", "Fine-tune a local model with this project's own Python trainer")
    p.add_argument("--data", required=True, help="JSONL messages dataset to train on")
    p.add_argument("--model", default="",
                   help="base model to fine-tune (HF repo or local path)")
    p.add_argument("--output", default="", help="output checkpoint directory")
    p.add_argument("--epochs", type=int, default=3)
    p.add_argument("--lr", type=float, default=2e-4)
    p.add_argument("--max-seq-length", type=int, default=2048)
    p.add_argument("--gguf", action="store_true",
                   help="also export an LM Studio/llama.cpp GGUF (needs unsloth)")

    args = ap.parse_args(argv)
    eng, cfg, store = open_engine(args.state_dir)

    if args.cmd == "record":
        r = eng.record(action=args.action, outcome=args.outcome, error=args.error,
                       fix=args.fix, verdict=args.verdict, detail=args.detail,
                       category=args.category, tags=args.tag,
                       derive_lesson=args.derive)
        _print(r)
    elif args.cmd == "learn":
        _print(eng.learn(statement=args.statement, detail=args.detail,
                         category=args.category, tags=args.tag,
                         source=args.source))
    elif args.cmd == "reflect":
        _print(eng.reflect_session(session_label=args.label,
                                   what_worked=args.worked,
                                   what_failed=args.failed, fix=args.fix,
                                   category=args.category))
    elif args.cmd == "retrieve":
        _print(eng.retrieve(args.task, limit=args.limit))
    elif args.cmd == "list":
        _print({"lessons": eng.list_lessons(status=args.status or None,
                                            category=args.category)})
    elif args.cmd == "stats":
        _print(eng.stats())
    elif args.cmd == "consolidate":
        _print(eng.consolidate(dry_run=args.dry_run))
    elif args.cmd == "obsolete":
        _print(eng.mark_obsolete(args.lesson_id, args.reason))
    elif args.cmd == "forget":
        _print(eng.delete_lesson(args.lesson_id))
    elif args.cmd == "undo":
        _print(eng.undo() or {"result": "nothing to undo"})
    elif args.cmd == "export":
        path = args.path or cfg.snapshot_path
        data = eng.store.export_json()
        from pathlib import Path
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2, default=str)
        _print({"written": path, "lessons": len(data["lessons"]),
                "experiences": len(data["experiences"])})
    elif args.cmd == "import":
        with open(args.path, "r", encoding="utf-8") as f:
            data = json.load(f)
        _print(store.import_json(data))
    elif args.cmd == "audit":
        _print({"audit": store.recent_audit(args.limit)})
    elif args.cmd == "mode":
        if args.value:
            _print(eng.set_mode(args.value))
        else:
            _print({"mode": eng.mode})
    elif args.cmd == "local":
        if args.action == "model":
            _print(eng.set_local_model(model=args.model, base_model=args.base))
        else:
            from . import mode as MO
            lmodel = eng.local_model()
            _print({"mode": eng.mode,
                    "local": lmodel,
                    "mode_local_enabled": eng.mode == MO.MODE_LOCAL,
                    "memory": eng.memory_path})
    elif args.cmd == "improve":
        from .factory import improvement
        runner = improvement(eng, cfg)
        _print(runner.run(dry_run=args.dry_run,
                          invoke_trainer=args.train,
                          only_verified=not args.include_unverified))
    elif args.cmd == "train":
        from .trainer import run_fine_tune
        model = args.model
        out = args.output
        if not model:
            model = eng.local_model().get("base_model") or ""
        if not out:
            out = cfg.local_dir + "/checkpoints/run_" + str(int(__import__("time").time()*1000))
        try:
            _print(run_fine_tune(base_model=model, dataset=args.data,
                                 output_dir=out, epochs=args.epochs,
                                 learning_rate=args.lr,
                                 max_seq_length=args.max_seq_length,
                                 export_gguf=args.gguf))
        except Exception as e:          # noqa - clean actionable message
            print(str(e), file=sys.stderr)
            sys.exit(3)
    store.close()


if __name__ == "__main__":
    main(sys.argv[1:])
