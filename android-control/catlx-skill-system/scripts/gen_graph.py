#!/usr/bin/env python3
"""Build metadata/dependency-graph.json from the registry + a delegates_to map (from DEPENDENCY-GRAPH.md).
Pure stdlib. Run from catlx-skill-system root."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REG = ROOT / "metadata" / "skills-registry.json"
OUT = ROOT / "metadata" / "dependency-graph.json"

# delegates_to map mirrored from DEPENDENCY-GRAPH.md (skill -> [targets])
DELEGATES = {
    "catlx": [],
    "catlx-orchestrator": [],
    "catlx-hardware-adaptation": ["catlx-capability-routing", "catlx-voice-pipeline",
        "catlx-screen-understanding", "catlx-telemetry", "catlx-electron-shell", "catlx-security"],
    "catlx-silexis-modules": ["catlx-capability-routing", "catlx-docker", "catlx-plugin-ecosystem"],
    "catlx-capability-routing": ["catlx-hardware-adaptation", "catlx-silexis-modules",
        "catlx-docker", "catlx-electron-shell", "catlx-plugin-ecosystem"],
    "catlx-voice-pipeline": ["catlx-ai-provider", "catlx-workflow-engine", "catlx-memory",
        "catlx-capability-routing", "catlx-desktop-control"],
    "catlx-desktop-control": ["catlx-screen-understanding", "catlx-security",
        "catlx-electron-shell", "catlx-workflow-engine", "catlx-capability-routing"],
    "catlx-screen-understanding": ["catlx-hardware-adaptation", "catlx-capability-routing",
        "catlx-desktop-control", "catlx-security", "catlx-docker"],
    "catlx-memory": ["catlx-ai-provider", "catlx-workflow-engine", "catlx-hardware-adaptation",
        "catlx-portability"],
    "catlx-ai-provider": ["catlx-memory", "catlx-hardware-adaptation", "catlx-docker",
        "catlx-capability-routing", "catlx-security"],
    "catlx-workflow-engine": ["catlx-capability-routing", "catlx-ai-provider", "catlx-memory",
        "catlx-desktop-control", "catlx-security", "catlx-docker", "catlx-recovery", "catlx-telemetry"],
    "catlx-security": ["catlx-docker", "catlx-recovery", "catlx-telemetry",
        "catlx-plugin-ecosystem", "catlx-hardware-adaptation"],
    "catlx-telemetry": ["catlx-electron-shell", "catlx-ai-provider", "catlx-workflow-engine",
        "catlx-hardware-adaptation"],
    "catlx-electron-shell": ["catlx-hardware-adaptation", "catlx-telemetry", "catlx-memory",
        "catlx-capability-routing", "catlx-desktop-control"],
    "catlx-plugin-ecosystem": ["catlx-security", "catlx-silexis-modules", "catlx-electron-shell",
        "catlx-docker", "catlx-capability-routing"],
    "catlx-docker": ["catlx-capability-routing", "catlx-recovery", "catlx-portability",
        "catlx-security", "catlx-silexis-modules"],
    "catlx-portability": ["catlx-hardware-adaptation", "catlx-docker", "catlx-memory",
        "catlx-capability-routing"],
    "catlx-recovery": ["catlx-workflow-engine", "catlx-ai-provider", "catlx-docker",
        "catlx-memory", "catlx-security"],
    "catlx-runtime-lifecycle": ["catlx-voice-pipeline", "catlx-workflow-engine",
        "catlx-plugin-ecosystem", "catlx-electron-shell", "catlx-security", "catlx-recovery",
        "catlx-hardware-adaptation", "catlx-capability-routing"],
}

reg = json.loads(REG.read_text(encoding="utf-8"))
nodes, edges = [], []
reg = json.loads(REG.read_text(encoding="utf-8"))
ids = {s["id"] for s in reg["skills"]}
# the orchestrator can route to any subsystem skill (all except itself)
DELEGATES["catlx-orchestrator"] = sorted(ids - {"catlx-orchestrator"} - {"catlx"})

def add_edge(src, dst, kind):
    edges.append({"source": src, "target": dst, "kind": kind, "cycle_safe": True})

for s in reg["skills"]:
    sid = s["id"]
    nodes.append({"id": sid, "name": s["name"],
                  "type": "root" if sid == "catlx" else "skill",
                  "path": s["skill_path"], "description": s["description"]})
    for d in s["depends_on"]:
        d = d.strip()
        if d in ids:
            add_edge(sid, d, "depends_on")
    for d in DELEGATES.get(sid, []):
        if d in ids:
            add_edge(sid, d, "delegates_to")

graph = {
    "nodes": nodes,
    "edges": edges,
    "note": "Cycle protection: single-pass delegation with an active-chain check; cycles identified in DEPENDENCY-GRAPH.md are bounded/peer relationships, not recursion.",
    "version": 1,
}
OUT.write_text(json.dumps(graph, indent=2, ensure_ascii=False), encoding="utf-8")
print(f"Wrote {OUT.relative_to(ROOT)} with {len(nodes)} nodes, {len(edges)} edges.")
