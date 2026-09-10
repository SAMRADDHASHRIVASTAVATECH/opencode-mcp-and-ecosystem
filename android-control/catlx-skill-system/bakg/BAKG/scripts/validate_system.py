#!/usr/bin/env python3
"""Validate BAKG internal coherence, relative refs, and skill completeness."""
from __future__ import annotations
import os, re, sys, json

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
errors = []
warnings = []

def err(msg): errors.append(msg)
def warn(msg): warnings.append(msg)

REQUIRED_TOP = [
    "README.md","INDEX.md","MANIFEST.md","IMPORT.md","SYSTEM.md",
    "registry/skills.yaml","registry/domains.yaml","registry/capability-index.md",
    "orchestration/router.md","orchestration/modes.md","orchestration/ultimate-test.md",
    "orchestration/delegation.md","orchestration/dependency-order.md",
    "context/identity.md","context/conventions.md","context/production-economy.md",
    "dependencies/skill-graph.yaml","checklists/master.md",
]

SKILL_SECTIONS = [
    "Purpose","Scope","Activation Conditions","Non-Activation Conditions",
    "Instructions","Procedures","Inputs","Outputs","Dependencies",
    "Related Skills","Delegation Rules",
]

def exists(rel):
    return os.path.exists(os.path.join(ROOT, rel))

for rel in REQUIRED_TOP:
    if not exists(rel):
        err(f"missing required file: {rel}")

# skills
skills_dir = os.path.join(ROOT, "skills")
skill_ids = []
if not os.path.isdir(skills_dir):
    err("missing skills/")
else:
    for name in sorted(os.listdir(skills_dir)):
        p = os.path.join(skills_dir, name)
        if not os.path.isdir(p):
            continue
        skill_ids.append(name)
        sm = os.path.join(p, "SKILL.md")
        if not os.path.isfile(sm):
            err(f"missing SKILL.md for {name}")
            continue
        text = open(sm, encoding="utf-8").read()
        if not text.startswith("---"):
            err(f"{name}: missing YAML frontmatter")
        for sec in SKILL_SECTIONS:
            if f"## {sec}" not in text:
                err(f"{name}: missing section ## {sec}")
        # CATLX leak
        if re.search(r"CATLX", text):
            err(f"{name}: accidental CATLX reference")
        # relative knowledge refs
        for m in re.finditer(r"`(knowledge/[^`]+)`", text):
            rel = m.group(1)
            if not exists(rel):
                err(f"{name}: broken knowledge ref {rel}")

# knowledge files non-empty
know = os.path.join(ROOT, "knowledge")
kcount = 0
for dirpath, _, files in os.walk(know):
    for fn in files:
        if fn.endswith(".md"):
            kcount += 1
            fp = os.path.join(dirpath, fn)
            if os.path.getsize(fp) < 200:
                warn(f"very small knowledge file: {os.path.relpath(fp, ROOT)}")
if kcount < 40:
    err(f"expected ~50 knowledge files, found {kcount}")

# CATLX leak anywhere except this script
for dirpath, dirs, files in os.walk(ROOT):
    dirs[:] = [d for d in dirs if d not in {".git","__pycache__"}]
    for fn in files:
        if fn == "validate_system.py":
            continue
        fp = os.path.join(dirpath, fn)
        try:
            t = open(fp, encoding="utf-8").read()
        except Exception:
            continue
        if "CATLX" in t:
            err(f"CATLX reference in {os.path.relpath(fp, ROOT)}")

print(f"skills: {len(skill_ids)}")
print(f"knowledge files: {kcount}")
print(f"errors: {len(errors)}")
print(f"warnings: {len(warnings)}")
for e in errors:
    print("ERROR:", e)
for w in warnings:
    print("WARN:", w)
sys.exit(1 if errors else 0)
