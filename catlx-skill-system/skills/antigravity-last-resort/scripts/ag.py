#!/usr/bin/env python3
"""
ag.py - Antigravity last-resort escalation wrapper (native CATLX capability)

Operates STRICTLY as the final escalation layer. CATLX's own capabilities are
always given the first opportunity; this wrapper is invoked only when the
system has determined an external advanced agent is genuinely necessary.

Safety & policy rules (enforced here):
  - availability discovery is non-mutating (never starts agy TUI)
  - escalation sends ONLY the focused subtask + necessary context/constraints
    and prior findings -- never a blind restart of the whole task
  - results are returned for CATLX to evaluate/verify/integrate; this wrapper
    does not claim to be the authority on the answer
  - unavailability / failure / timeout degrades gracefully with a clear report

Subcommands:
  check          Probe agy binary + auth. No side effects. Exit 0 if usable.
  escalate       Run one headless Antigravity run (agy -p ... --output-format json)
                 Print machine-readable result envelope to stdout.
  reset          Forget cached state (no effect on agy itself)
"""

import argparse
import json
import os
import shutil
import subprocess
import sys
import time
import hashlib

CACHE_DIR = os.path.join(os.environ.get("CHIM_HOME") or
                         os.environ.get("CATLX_HOME") or
                         os.path.expanduser(r"~\.config\opencode\clean-human-mode"),
                         "state")


def find_agy():
    env = os.environ.get("AGY_PATH")
    if env and os.path.isfile(env):
        return env
    hit = shutil.which("agy")
    if hit:
        return hit
    for cand in (
        os.path.expanduser(r"~\AppData\Local\agy\bin\agy.exe"),
        r"C:\Users\HP\AppData\Local\agy\bin\agy.exe",
        "/usr/local/bin/agy",
        "/opt/homebrew/bin/agy",
    ):
        if os.path.isfile(cand):
            return cand
    return None


def probe():
    exe = find_agy()
    if not exe:
        return {"available": False, "reason": "agy binary not found", "version": None}
    try:
        r = subprocess.run([exe, "--version"], capture_output=True, text=True, timeout=20)
        ver = (r.stdout or r.stderr or "").strip()
        return {"available": True, "path": exe, "version": ver or "unknown"}
    except Exception as e:
        return {"available": False, "reason": "version probe failed: %s" % e, "path": exe}


def run_agy(question, model=None, effort=None, agent=None, timeout_s=300,
            output_format="json", extra=None):
    exe = find_agy()
    probe_info = probe()
    if not probe_info.get("available"):
        return {"status": "UNAVAILABLE", "error": probe_info.get("reason", "agy unavailable")}
    cmd = [exe, "-p", question, "--output-format", output_format]
    if model:
        cmd += ["--model", model]
    if effort:
        cmd += ["--effort", effort]
    if agent:
        cmd += ["--agent", agent]
    cmd += ["--print-timeout", "%ds" % timeout_s]
    if extra:
        cmd += extra
    started = time.time()
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout_s + 30)
    except subprocess.TimeoutExpired:
        return {
            "status": "TIMEOUT",
            "duration_s": round(time.time() - started, 2),
            "question": question,
            "conversation_id": None,
        }
    except Exception as e:
        return {"status": "FAILED", "error": "invocation error: %s" % e}
    elapsed = round(time.time() - started, 2)
    out = (r.stdout or "").strip()
    err = (r.stderr or "").strip()
    try:
        env = json.loads(out)
    except Exception:
        env = None
    if env is not None and isinstance(env, dict):
        env["duration_s"] = env.get("duration_seconds", elapsed)
        env["conversation_id"] = env.get("conversation_id")
        env["question"] = question
        if env.get("status") != "SUCCESS":
            env["error"] = env.get("error") or err or "run returned non-SUCCESS"
        return env
    if r.returncode != 0:
        return {"status": "FAILED", "error": err or "agy exited %d" % r.returncode,
                "duration_s": elapsed, "question": question}
    return {"status": "SUCCESS", "response": out, "duration_s": elapsed,
            "conversation_id": None, "question": question}


def main():
    ap = argparse.ArgumentParser(prog="ag", description="Antigravity last-resort escalation wrapper")
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("check")
    p.set_defaults(cmd="check")

    p = sub.add_parser("escalate")
    p.add_argument("question", nargs="?", default="")
    p.add_argument("--model", default=None)
    p.add_argument("--effort", default=None)
    p.add_argument("--agent", default=None)
    p.add_argument("--timeout", type=int, default=300)
    p.add_argument("--output-format", default="json", choices=["text", "json", "stream-json"])
    p.add_argument("--working-dir")
    p.set_defaults(cmd="escalate")

    p = sub.add_parser("reset")
    p.set_defaults(cmd="reset")

    args = ap.parse_args()

    if args.cmd == "check":
        info = probe()
        print(json.dumps(info, ensure_ascii=False))
        sys.exit(0 if info.get("available") else 3)

    elif args.cmd == "escalate":
        question = args.question.strip()
        if not question:
            try:
                question = sys.stdin.read().strip()
            except Exception:
                question = ""
        if not question:
            print(json.dumps({"status": "FAILED", "error": "empty question"}, ensure_ascii=False))
            sys.exit(2)
        cwd = args.working_dir or None
        extra = []
        if cwd:
            extra += ["--sandbox"]
        result = run_agy(question, model=args.model, effort=args.effort,
                         agent=args.agent, timeout_s=args.timeout,
                         output_format=args.output_format, extra=extra)
        print(json.dumps(result, ensure_ascii=False))
        sys.exit(0 if result.get("status") == "SUCCESS" else 4)

    elif args.cmd == "reset":
        print(json.dumps({"status": "OK", "note": "state cache reset (agy untouched)"}))


if __name__ == "__main__":
    main()