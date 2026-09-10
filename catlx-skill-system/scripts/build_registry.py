#!/usr/bin/env python3
"""
Generate metadata/skills-registry.json from the actual SKILL.md frontmatter, and validate OpenCode
skill compatibility (name rules, folder match, description length, valid frontmatter). Windows-only
project — pure stdlib, no external deps.

Run:  python scripts/build_registry.py   (from catlx-skill-system root)
"""
import json, re, sys
from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT / "skills"
OUT = ROOT / "metadata" / "skills-registry.json"

name_re = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")

def read_frontmatter(path: Path):
    """Return (meta: dict, body, error). Parses the YAML frontmatter with a real YAML parser."""
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        return None, None, "SKILL.md must start with YAML frontmatter (---)"
    idx = text.find("\n---\n")
    if idx == -1:
        return None, None, "frontmatter not closed with ---"
    yml = text[4:idx]
    rest = text[idx+5:]
    try:
        meta = yaml.safe_load(yml)
    except Exception as e:  # noqa: BLE001
        return None, None, f"Invalid YAML in frontmatter: {e}"
    if not isinstance(meta, dict):
        return None, None, "frontmatter must be a YAML mapping"
    return meta, rest, None

def main():
    records = []
    errors = []
    if not SKILLS.exists():
        print("No skills/ directory found"); sys.exit(1)
    for child in sorted(SKILLS.iterdir()):
        if not child.is_dir():
            continue
        skill_md = child / "SKILL.md"
        if not skill_md.exists():
            errors.append(f"Missing SKILL.md in {child.name}")
            continue
        meta, _, err = read_frontmatter(skill_md)
        if err:
            errors.append(f"{child.name}: {err}")
            continue
        name = meta.get("name", "")
        desc = meta.get("description", "")
        # --- validation ---
        if not name_re.match(name):
            errors.append(f"{child.name}: name '{name}' invalid (lowercase, hyphens only)")
        if name != child.name:
            errors.append(f"{child.name}: folder '{child.name}' != name '{name}'")
        if len(name) > 64:
            errors.append(f"{child.name}: name > 64 chars")
        if not desc:
            errors.append(f"{child.name}: missing description")
        elif len(desc) > 1024:
            errors.append(f"{child.name}: description > 1024 chars")
        meta_md = meta.get("metadata") or {}
        deps = [d.strip() for d in str(meta_md.get("depends-on", "")).split(",") if d.strip()]
        aliases = [a.strip() for a in str(meta_md.get("aliases", "")).split(",") if a.strip()]
        records.append({
            "id": name,
            "name": name,
            "relative_path": str(child.relative_to(ROOT)).replace("\\", "/"),
            "skill_path": str(skill_md.relative_to(ROOT)).replace("\\", "/"),
            "description": desc,
            "capabilities": [meta_md.get("capability", "")] if meta_md.get("capability") else [],
            "aliases": aliases,
            "category": meta_md.get("category", ""),
            "subsystem": meta_md.get("subsystem", ""),
            "skill_type": meta_md.get("skill-type", ""),
            "depends_on": deps,
            "version": meta_md.get("version", "1.0.0"),
            "source": meta_md.get("source", ""),
        })

    # Top-level manifest docs
    out = {
        "manifest_version": 1,
        "name": "CATLX Universal AI Operating System skill ecosystem",
        "description": "Windows-only, USB-free: ability-compiled skill ecosystem derived from CATLX_Universal_AI_OS_Specification.pdf",
        "target_runtime": "OpenCode (SKILL.md, skill tool)",
        "root_skill": "catlx",
        "skill_count": len(records),
        "skills": records,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Wrote {OUT.relative_to(ROOT)} with {len(records)} skills.")
    if errors:
        print("\nVALIDATION ISSUES:")
        for e in errors:
            print("  -", e)
        sys.exit(1)
    print("All skills passed basic OpenCode frontmatter validation.")

if __name__ == "__main__":
    main()
