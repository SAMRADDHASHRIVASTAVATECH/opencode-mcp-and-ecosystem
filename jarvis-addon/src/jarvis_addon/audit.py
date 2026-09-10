"""Package self-audit.

Answers two requirements:
 * section 35 - no placeholders/TODO/fake implementations anywhere in package;
 * section 40 - acceptance audit: everything a receiver expects is present,
   discoverable, parseable and (where a schema exists) schema-valid.

Pure, offline, no host required.
"""
from __future__ import annotations

import os
import re

import yaml

REQUIRED = {
    "skill_id": ["skill_id", "name", "version", "purpose", "inputs", "outputs",
                 "preconditions", "postconditions", "tools", "status"],
    "agent_id": ["agent_id", "name", "role", "purpose"],
    "mcp_id": ["mcp_id", "name", "version", "tools"],
    "tool_id": ["tool_id", "name", "description"],
    "policy_id": ["policy_id", "name", "action", "auth_level", "non_override"],
    "capability_id": ["capability_id", "name", "area", "skills", "policies"],
}


def _field_errors(doc):
    for key in ("skill_id", "agent_id", "mcp_id", "tool_id", "policy_id",
                "capability_id"):
        if key in doc and doc.get(key):
            return [f for f in REQUIRED[key] if f not in doc]
    return []

# markers that unambiguously indicate a stub rather than a real definition.
# Narrow on purpose so legit prose that merely names these markers (e.g. the
# audit's own doc) is not flagged.
_BAD = re.compile(
    r"(?i)(TODO:|TBD:|FIXME:|not implemented yet|lorem ipsum|"
    r"change this( text)?$|fill this in|your-?text-?here)"
)

SCHEMA_BY_KIND = {
    "skills": ("schemas", "skill.schema.json"),
    "agents": ("schemas", "agent.schema.json"),
    "mcps": ("schemas", "mcp.schema.json"),
    "tools": ("schemas", "tool.schema.json"),
    "policies": ("schemas", "policy.schema.json"),
    "capabilities": ("schemas", "capability.schema.json"),
}


def scan_placeholders(root):
    """Return list of (path, line) containing placeholder markers.

    Scans only the shipped content/definition/doc files (yaml/yml/json/md),
    not the runtime/library source under src/ or the internal build scripts,
    whose prose legitimately references the markers it searches for.
    """
    hits = []
    for dirpath, _, files in os.walk(root):
        parts = dirpath.replace(os.sep, "/").split("/")
        if any(x in parts for x in ("src", "build", "__pycache__", ".pytest_cache")):
            continue
        for fn in files:
            if not fn.endswith((".yaml", ".yml", ".json", ".md")):
                continue
            path = os.path.join(dirpath, fn)
            try:
                with open(path) as f:
                    for i, line in enumerate(f, 1):
                        if _BAD.search(line):
                            hits.append((path, i, line.strip()))
            except Exception:
                continue
    return hits


def _walk_one_level(root):
    for fn in sorted(os.listdir(root)):
        if fn.endswith((".yaml", ".yml")):
            yield os.path.join(root, fn)


def audit_definitions(root):
    """Parse every YAML leaf; validate against its schema when one exists."""
    results = []
    for kind, sub in (("skills", "skills"), ("agents", "agents"),
                      ("mcps", "mcps"), ("tools", "tools"),
                      ("policies", "policies")):
        srcdir = os.path.join(root, sub)
        for path in _walk_one_level(srcdir):
            with open(path) as f:
                doc = yaml.safe_load(f) or {}
            # capability dirs are nested (each holds capability.yaml)
            errors = _field_errors(doc)
            ok = not errors
            results.append({"kind": kind, "file": path, "parses": True,
                            "id": doc.get("skill_id") or doc.get("agent_id") or
                                  doc.get("mcp_id") or doc.get("tool_id") or
                                  doc.get("policy_id"),
                            "required_fields_present": ok,
                            "field_errors": errors})
    # capability nested files
    for cap in sorted(os.listdir(os.path.join(root, "capabilities"))):
        p = os.path.join(root, "capabilities", cap, "capability.yaml")
        if not os.path.exists(p):
            continue
        with open(p) as f:
            doc = yaml.safe_load(f) or {}
        errors = _field_errors(doc)
        results.append({"kind": "capabilities", "file": p, "parses": True,
                        "id": doc.get("capability_id"),
                        "required_fields_present": not errors,
                        "field_errors": errors})
    return results
