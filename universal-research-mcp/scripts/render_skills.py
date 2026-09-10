#!/usr/bin/env python3
"""Render the built-in skill catalog to skills/<name>/SKILL.md files + INDEX.md.

The canonical definitions live in code (registry/skills_catalog.py); this makes
them travel as human/agent-readable markdown in the package.
Run: python scripts/render_skills.py
"""
from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
from universal_research.registry.skills_catalog import all_skills  # noqa: E402

OUT = ROOT / "skills"


def render_one(s) -> str:
    L = []
    L.append(f"# {s.name}\n")
    L.append(f"{s.description}\n")
    L.append("## Metadata")
    L.append(f"- tools: {', '.join('`'+t+'`' for t in s.tools) or '(none)'}")
    L.append(f"- dependencies: {', '.join('`'+d+'`' for d in s.dependencies) or '(none)'}")
    L.append(f"- providers: {', '.join('`'+p+'`' for p in s.providers) or 'auto/any'}\n")
    L.append("## Capabilities")
    for c in s.capabilities:
        L.append(f"- {c}")
    L.append("\n## Input schema")
    L.append("```json")
    import json
    L.append(json.dumps(s.input_schema, indent=2) if s.input_schema else "{}")
    L.append("```")
    L.append("\n## Output schema")
    L.append("```json")
    L.append(json.dumps(s.output_schema, indent=2) if s.output_schema else "{}")
    L.append("```")
    L.append("\n## Security")
    L.append(s.security)
    return "\n".join(L) + "\n"


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    index = ["# Built-in research skills", "",
             "Every skill below ships with the package and is registered "
             "automatically. Each is individually callable (via its tools) and "
             "composable by the deep-research orchestrator.\n"]
    for s in all_skills():
        d = OUT / s.name
        d.mkdir(parents=True, exist_ok=True)
        fm = (f"---\nname: {s.name}\n"
              f"tools: {','.join(s.tools)}\n"
              f"dependencies: {','.join(s.dependencies)}\n---\n")
        (d / "SKILL.md").write_text(fm + render_one(s))
        index.append(f"- `{s.name}` — {s.description} (tools: "
                     f"{', '.join('`'+t+'`' for t in s.tools)})")
    (OUT / "INDEX.md").write_text("\n".join(index) + "\n")
    print(f"rendered {len(all_skills())} skills into {OUT}")


if __name__ == "__main__":
    main()
