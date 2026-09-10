#!/usr/bin/env python3
"""Direct Python-API tour of the engine, in deterministic offline mode.

Run from the repo root:
    PYTHONPATH=src python examples/quickstart.py
or, once installed:    python examples/quickstart.py
"""
import os
import time

os.environ["UR_OFFLINE"] = "1"  # deterministic mock mode, no network

from universal_research import functions as F


def main():
    print("== registries ==")
    tools = F.list_tools()["tools"]
    skills = F.list_skills()["skills"]
    print(f"{len(tools)} tools, {len(skills)} skills")

    print("\n== web search (offline mock) ==")
    for r in F.search_web("python pdf parsing", limit=4)["results"]:
        print(f"- {r['title']} | {r['url']}")

    print("\n== fact check ==")
    fc = F.fact_check("PyMuPDF is a PDF library for Python")
    print(f"verdict={fc['verdict']} confidence={fc['confidence']}")

    print("\n== research plan ==")
    plan = F.research_plan("best open source pdf parsing library")
    print("objective:", plan.get("objective"))
    print("kind:", plan.get("kind"))
    print("steps:", len(plan.get("steps", [])))

    print("\n== deep research (async task) ==")
    dr = F.deep_research("open source python pdf parsing")
    task_id = dr["task_id"]
    print("status:", dr["status"], "task:", task_id)

    # poll to completion (offline finishes quickly)
    for _ in range(40):
        st = F.research_status(task_id)
        s = st.get("state") if isinstance(st, dict) else None
        if s in ("COMPLETED", "FAILED", "CANCELLED"):
            break
        time.sleep(0.25)

    wrapped = F.research_result(task_id)          # {task_id, result:{...}}
    result = wrapped.get("result", {}) if isinstance(wrapped, dict) else {}
    top = result.get("top_sources", []) or []
    print("\n== result ==")
    print("state:", wrapped.get("state") if isinstance(wrapped, dict) else None)
    print("method:", result.get("method"))
    for s in top[:6]:
        print("-", s.get("title"), "|", s.get("url"))


if __name__ == "__main__":
    main()
