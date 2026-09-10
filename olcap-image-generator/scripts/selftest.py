"""Offline self-test + diagnostics for OLCAP Image Generator.

Validates that the whole package imports, hardware detection runs, the registry,
selector, memory planner and jobs all work, the default ComfyUI workflows are
seeded, and the demo (clearly-labelled, NON-AI) pipeline produces a file.
Does NOT require a GPU or any AI model.

Usage:  python scripts/selftest.py [--state-dir PATH]
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--state-dir", default="", help="state/config dir (optional)")
    args = ap.parse_args()

    sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
    from olcap_image_gen.context import Context
    from olcap_image_gen.diagnostics import Diagnostics

    ctx = Context(args.state_dir)
    diag = Diagnostics(ctx)

    print("=== Hardware profile ===")
    print(" ", ctx.profile.summary())

    print("\n=== Diagnostics ===")
    d = diag.diagnose()
    for c in d["checks"]:
        print(f"  [{c['status']:>16}] {c['component']}: "
              f"{str(c.get('detail'))[:80]}")
    print("  counts:", d["counts"])

    print("\n=== Self-test (offline) ===")
    st = diag.self_test()
    for r in st["results"]:
        print(f"  {'OK ' if r['ok'] else 'FAIL'} {r['test']}"
              f"{'  (optional)' if not r['required'] else ''}")
    print("  ai_generation_ready:", st["ai_generation_ready"])

    print("\n=== Workflows seeded ===")
    wd = ctx.settings.resolved_workflows_dir()
    for f in sorted(wd.glob("*.json")):
        print("  ", f.name)

    ok = bool(st["success"])
    print("\nRESULT:", "PASS" if ok else "FAIL",
          "(real AI inference still requires GPU + installed model on target)")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
