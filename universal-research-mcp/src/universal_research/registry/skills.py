"""SkillRegistry builder + skill doc generation."""
from __future__ import annotations

from ..errors import NotFoundError
from .base import SkillRegistry
from .skills_catalog import all_skills


def build_skill_registry() -> SkillRegistry:
    reg = SkillRegistry()
    for s in all_skills():
        reg.register(s)
    return reg


def render_skills_markdown() -> dict[str, str]:
    """Render each skill to its SKILL.md body (traveling skill set)."""
    files = {}
    for s in all_skills():
        body = [
            f"# {s.name}",
            "",
            f"{s.description}",
            "",
            "## Capabilities",
        ]
        for c in s.capabilities:
            body.append(f"- {c}")
        body += ["", "## Tools mapped", ""]
        for t in s.tools:
            body.append(f"- `{t}`")
        body += ["", "## Dependencies", ""]
        if s.dependencies:
            for d in s.dependencies:
                body.append(f"- `{d}`")
        else:
            body.append("- (none)")
        body += ["", "## Input schema", "", "```json",
                 _jsonish(s.input_schema), "```",
                 "", "## Output schema", "", "```json", _jsonish(s.output_schema),
                 "```", "", "## Providers", ""]
        for p in s.providers:
            body.append(f"- `{p}`")
        if not s.providers:
            body.append("- auto/any")
        body += ["", "## Security", "", f"{s.security}"]
        files[s.name] = "\n".join(body) + "\n"
    return files


def _jsonish(d) -> str:
    import json
    return json.dumps(d, indent=2) if d else "{}"


def get_skill(reg: SkillRegistry, name: str) -> dict:
    try:
        s = reg.get(name)
        return s.to_dict() if hasattr(s, "to_dict") else {
            k: (v if isinstance(v, (list, dict, str, int, float, bool)) else str(v))
            for k, v in s.items()}
    except NotFoundError:
        raise
