"""Definition registry & package discovery.

Implements the acceptance criterion:
    "Could another compatible JARVIS installation inspect this package and
     discover exactly what capabilities/skills/policies/agents/MCPs/schemas/
     contracts it is receiving?"

A host inspects the package tree via these helpers (or reads the files directly)
to learn exactly what additive components it receives. Every helper is pure and
does not touch any external JARVIS.
"""
from __future__ import annotations

import os

import yaml


def _walk_yaml(root, sub):
    """Yield (name, path) for every YAML leaf directly under ROOT/sub."""
    base = os.path.join(root, sub)
    if not os.path.isdir(base):
        return
    for fn in sorted(os.listdir(base)):
        if fn.endswith(".yaml") or fn.endswith(".yml"):
            yield fn, os.path.join(base, fn)


def load_dir(root, sub):
    """Load all YAML files in a subdirectory into {id_or_name: dict}."""
    out = {}
    for fn, path in _walk_yaml(root, sub):
        with open(path) as f:
            doc = yaml.safe_load(f) or {}
        key = doc.get("skill_id") or doc.get("agent_id") or \
              doc.get("mcp_id") or doc.get("tool_id") or doc.get("policy_id") or \
              doc.get("capability_id") or doc.get("event") or fn.replace(".yaml", "")
        out[key] = doc
    return out


def inventory(root):
    """Return counts of additive definitions shipped by the package."""
    def count(sub):
        return len([1 for _ in _walk_yaml(root, sub)])

    caps = sum(1 for _ in os.listdir(os.path.join(root, "capabilities"))
               if os.path.isdir(os.path.join(root, "capabilities", _)))
    schemas = sum(1 for _ in os.listdir(os.path.join(root, "schemas"))
                  if _.endswith(".json"))
    return {
        "capabilities": caps,
        "skills": count("skills"),
        "policies": count("policies"),
        "agents": count("agents"),
        "mcps": count("mcps"),
        "tools": count("tools"),
        "events": count("events"),
        "schemas": schemas,
        "contracts": count("contracts"),
    }


def discover_capabilities(root):
    """Return one dict per capability area, each listing its component refs."""
    caps = {}
    for cap in sorted(os.listdir(os.path.join(root, "capabilities"))):
        p = os.path.join(root, "capabilities", cap, "capability.yaml")
        if not os.path.exists(p):
            continue
        with open(p) as f:
            caps[cap] = yaml.safe_load(f)
    return caps
