#!/usr/bin/env python3
"""
Generate metadata/capability-index.json — the deterministic, small-model routing core.

This is NOT a second knowledge source. It is a *view* over the canonical skill registry that:
  - maps natural-language capability phrases -> skill ids (intent routing),
  - records per-skill capabilities (action phrases), aliases, dependencies, delegation targets,
    references, workflows, and source locations,
  - assigns a small `routing_hint` so a lightweight local model can pick the best entry skill quickly.

Curated intent/capability text is source-derived (built from each skill's purpose + the source parts it
covers). Run:  python scripts/build_routing.py
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REG = ROOT / "metadata" / "skills-registry.json"
OUT = ROOT / "metadata" / "capability-index.json"

# Per-skill: capabilities (action phrases a user might ask for) and one-line routing hint.
CAPS = {
 "catlx": {"capabilities": ["route a CATLX request", "enter the skill system", "get a subsystem overview"],
           "hint": "Generic/first entry. Route to a subsystem; prefer the most specific skill."},
 "catlx-hardware-adaptation": {"capabilities": ["detect hardware tier", "read the capability matrix",
    "run the boot hardware scan", "get the capability map", "reconfigure for available hardware",
    "pick ocr/stt/tts/llm/vector backend per tier", "adapt to a weak or strong machine"],
    "hint": "Any hardware/tier/capability-map or 'runs on any machine' question."},
 "catlx-silexis-modules": {"capabilities": ["manage modules", "extract a module", "analyze a module",
    "build a module", "package a module", "query the module registry", "read a module manifest",
    "understand capability tokens", "version and dependency-graph a module"],
    "hint": "Modules, module registry, manifests, packaging, SILEXIS."},
 "catlx-capability-routing": {"capabilities": ["route a capability request", "choose an execution environment",
    "build a fallback chain", "where does this run", "file-backed registries", "live gui sync",
    "adaptive runtime evolution", "config routing"],
    "hint": "Where/how a capability runs, fallbacks, registries, runtime routing rules."},
 "catlx-voice-pipeline": {"capabilities": ["voice command", "set a wake word", "speech to text",
    "nlu intent parsing", "clarify an ambiguous command", "text to speech", "conversation context",
    "voice pipeline stages"],
    "hint": "Voice/speech/wake-word/STT/NLU/TTS/interaction lifecycle."},
 "catlx-desktop-control": {"capabilities": ["control the mouse", "type keyboard input", "manage windows",
    "operate on files", "automate a browser", "automate an application", "multi-monitor control",
    "overlay hud", "native notifications"],
    "hint": "Any 'do something on the desktop' mouse/keyboard/window/file/browser/app action."},
 "catlx-screen-understanding": {"capabilities": ["run ocr", "read the screen", "detect ui elements",
    "extract a screen model", "understand a screenshot", "find a button/field/link"],
    "hint": "OCR, screen content, UI-element/screen model extraction."},
 "catlx-memory": {"capabilities": ["remember events", "store facts and preferences", "recall a past interaction",
    "workspace state", "knowledge graph query", "resolve conflicting memories", "compress memory",
    "retrieve context for ai (rag)"],
    "hint": "Memory, remembering, facts/preferences, knowledge graph, RAG."},
 "catlx-ai-provider": {"capabilities": ["run ai inference", "call an llm", "route between providers",
    "failover between providers", "cost-optimize a call", "host a local llm", "generate embeddings",
    "choose a model for the tier"],
    "hint": "AI inference, providers, routing/failover, cost, local models."},
 "catlx-workflow-engine": {"capabilities": ["run a workflow", "schedule a task", "execute a dag",
    "checkpoint a run", "replay a run", "roll back a run", "define a state machine",
    "write a workflow in yaml"],
    "hint": "Multi-step tasks, scheduling, checkpoint/replay/rollback, workflow YAML."},
 "catlx-security": {"capabilities": ["store credentials", "manage permissions", "enforce least privilege",
    "sandbox a plugin", "audit actions", "detect risk", "enter safe mode", "read the credential vault",
    "authentication / authorization"],
    "hint": "Credentials, permissions, sandboxing, audit, risk, safe/recovery mode."},
 "catlx-telemetry": {"capabilities": ["trace an operation", "record metrics", "view observability dashboard",
    "profile slow code", "query causal lineage", "why did catlx do x", "read a telemetry report"],
    "hint": "Tracing, metrics, profiling, lineage, observability."},
 "catlx-electron-shell": {"capabilities": ["open the command palette", "manage shell windows",
    "configure the hud", "use the tray", "secure inter-process communication",
    "persist workspace state"],
    "hint": "The shell/GUI: windows, palette, HUD, tray, IPC, workspace persistence."},
 "catlx-plugin-ecosystem": {"capabilities": ["install a plugin", "write a plugin", "use the plugin sdk",
    "publish to the marketplace", "hot reload a plugin", "resolve plugin dependencies"],
    "hint": "Plugins, SDK, marketplace, hot reload, plugin dependency resolution."},
 "catlx-docker": {"capabilities": ["run a container service", "deploy with compose", "use gpu containers",
    "make volumes relocatable", "use offline containers", "docker swarm / kubernetes", "degrade gracefully"],
    "hint": "Containers/Docker, Compose, relocatable volumes, offline, Swarm/K8s."},
 "catlx-portability": {"capabilities": ["install portably", "resolve relative paths", "bundle node runtime",
    "run from an external ssd", "cross-machine identity", "move the install without reconfiguration"],
    "hint": "Portability, relative paths, portable mode, cross-machine identity."},
 "catlx-recovery": {"capabilities": ["recover from a crash", "enter safe mode", "restore a checkpoint",
    "recovery matrix", "troubleshoot startup", "resume an interrupted workflow"],
    "hint": "Crash recovery, safe/recovery mode, checkpoint restore, resilience."},
 "catlx-runtime-lifecycle": {"capabilities": ["explain boot order", "trace the voice lifecycle",
    "trace the workflow lifecycle", "trace the plugin lifecycle", "trace the recovery lifecycle",
    "initialize the runtime"],
    "hint": "Ordered runtime sequences: boot, voice, workflow, plugin, recovery."},
}

# Natural-language intent -> ordered candidate skills (best entry first). Source-derived.
INTENT = {
 "deploy": ["catlx-docker", "catlx-workflow-engine", "catlx-capability-routing", "catlx-portability"],
 "deployment": ["catlx-docker", "catlx-workflow-engine", "catlx-capability-routing", "catlx-portability"],
 "deployment failing": ["catlx-recovery", "catlx-telemetry", "catlx-docker", "catlx-capability-routing", "catlx-security"],
 "deployment is failing": ["catlx-recovery", "catlx-telemetry", "catlx-docker", "catlx-capability-routing", "catlx-security"],
 "deployment failure": ["catlx-recovery", "catlx-telemetry", "catlx-docker", "catlx-capability-routing", "catlx-security"],
 "deployment keeps failing": ["catlx-recovery", "catlx-telemetry", "catlx-docker", "catlx-capability-routing", "catlx-security"],
 "diagnose deployment": ["catlx-recovery", "catlx-telemetry", "catlx-docker", "catlx-capability-routing", "catlx-security"],
 "deployment troubleshooting": ["catlx-recovery", "catlx-telemetry", "catlx-docker", "catlx-capability-routing", "catlx-security"],
 "deployment credentials": ["catlx-security", "catlx-docker", "catlx-recovery"],
 "deployment credentials not working": ["catlx-security", "catlx-docker", "catlx-recovery"],
 "credentials not working": ["catlx-security", "catlx-recovery"],
 "credentials dont work": ["catlx-security", "catlx-recovery"],
 "what is wrong": ["catlx-recovery", "catlx-telemetry", "catlx-capability-routing", "catlx-security"],
 "whats wrong": ["catlx-recovery", "catlx-telemetry", "catlx-capability-routing", "catlx-security"],
 "why does": ["catlx-recovery", "catlx-telemetry", "catlx-security"],
 "release application": ["catlx-docker", "catlx-workflow-engine", "catlx-portability"],
 "deployment is broken": ["catlx-recovery", "catlx-telemetry", "catlx-docker", "catlx-capability-routing"],
 "release": ["catlx-docker", "catlx-workflow-engine", "catlx-portability"],
 "publish": ["catlx-plugin-ecosystem", "catlx-docker", "catlx-silexis-modules"],
 "configure": ["catlx-capability-routing", "catlx-hardware-adaptation", "catlx-security"],
 "configuration": ["catlx-capability-routing", "catlx-hardware-adaptation", "catlx-security"],
 "authenticate": ["catlx-security"],
 "authentication": ["catlx-security"],
 "credential": ["catlx-security"],
 "login": ["catlx-security"],
 "permission": ["catlx-security"],
 "authorize": ["catlx-security"],
 "debug": ["catlx-recovery", "catlx-telemetry", "catlx-security", "catlx-workflow-engine", "catlx-capability-routing"],
 "troubleshoot": ["catlx-recovery", "catlx-telemetry", "catlx-capability-routing", "catlx-workflow-engine"],
 "why is it failing": ["catlx-recovery", "catlx-telemetry", "catlx-security", "catlx-capability-routing"],
 "fix this problem": ["catlx-recovery", "catlx-telemetry", "catlx-security", "catlx-capability-routing"],
 "test": ["catlx-workflow-engine", "catlx-security"],
 "validate": ["catlx-workflow-engine", "catlx-security", "catlx-capability-routing"],
 "security": ["catlx-security", "catlx-plugin-ecosystem", "catlx-docker"],
 "sandbox": ["catlx-security", "catlx-plugin-ecosystem", "catlx-docker"],
 "memory": ["catlx-memory"],
 "remember": ["catlx-memory"],
 "recall": ["catlx-memory"],
 "facts": ["catlx-memory"],
 "knowledge graph": ["catlx-memory"],
 "voice": ["catlx-voice-pipeline"],
 "speech": ["catlx-voice-pipeline"],
 "wake word": ["catlx-voice-pipeline"],
 "speak": ["catlx-voice-pipeline"],
 "automate": ["catlx-desktop-control", "catlx-workflow-engine", "catlx-screen-understanding"],
 "mouse": ["catlx-desktop-control"],
 "keyboard": ["catlx-desktop-control"],
 "window": ["catlx-desktop-control", "catlx-electron-shell"],
 "files": ["catlx-desktop-control"],
 "browser": ["catlx-desktop-control"],
 "screen": ["catlx-screen-understanding", "catlx-desktop-control"],
 "ocr": ["catlx-screen-understanding"],
 "clipboard": ["catlx-desktop-control"],
 "build": ["catlx-silexis-modules", "catlx-plugin-ecosystem", "catlx-workflow-engine"],
 "package": ["catlx-silexis-modules", "catlx-plugin-ecosystem"],
 "module": ["catlx-silexis-modules"],
 "plugin": ["catlx-plugin-ecosystem"],
 "container": ["catlx-docker", "catlx-capability-routing"],
 "docker": ["catlx-docker", "catlx-capability-routing"],
 "compose": ["catlx-docker"],
 "monitor": ["catlx-telemetry", "catlx-electron-shell"],
 "telemetry": ["catlx-telemetry"],
 "metrics": ["catlx-telemetry"],
 "log": ["catlx-telemetry"],
 "profile": ["catlx-telemetry"],
 "shell": ["catlx-electron-shell"],
 "gui": ["catlx-electron-shell"],
 "palette": ["catlx-electron-shell"],
 "tray": ["catlx-electron-shell"],
 "crash": ["catlx-recovery", "catlx-runtime-lifecycle"],
 "recover": ["catlx-recovery"],
 "restore": ["catlx-recovery", "catlx-memory"],
 "checkpoint": ["catlx-workflow-engine", "catlx-recovery"],
 "workflow": ["catlx-workflow-engine"],
 "schedule": ["catlx-workflow-engine"],
 "pipeline": ["catlx-workflow-engine", "catlx-voice-pipeline"],
 "llm": ["catlx-ai-provider"],
 "model": ["catlx-ai-provider", "catlx-hardware-adaptation"],
 "inference": ["catlx-ai-provider"],
 "embedding": ["catlx-ai-provider", "catlx-memory"],
 "hardware": ["catlx-hardware-adaptation"],
 "tier": ["catlx-hardware-adaptation"],
 "path": ["catlx-portability"],
 "portable": ["catlx-portability"],
 "identity": ["catlx-portability", "catlx-security"],
 "boot": ["catlx-runtime-lifecycle", "catlx-hardware-adaptation"],
 "startup": ["catlx-runtime-lifecycle", "catlx-recovery"],
 "lifecycle": ["catlx-runtime-lifecycle"],
 "route": ["catlx-capability-routing"],
 "fallback": ["catlx-capability-routing", "catlx-ai-provider"],
 "offline": ["catlx-docker", "catlx-ai-provider", "catlx-capability-routing"],
}

# delegation targets (mirrors DEPENDENCY-GRAPH.md / gen_graph.py)
DELEGATES = {
 "catlx-hardware-adaptation": ["catlx-capability-routing"],
 "catlx-silexis-modules": ["catlx-capability-routing", "catlx-docker", "catlx-plugin-ecosystem"],
 "catlx-capability-routing": ["catlx-hardware-adaptation", "catlx-silexis-modules", "catlx-docker", "catlx-electron-shell", "catlx-plugin-ecosystem"],
 "catlx-voice-pipeline": ["catlx-ai-provider", "catlx-workflow-engine", "catlx-memory", "catlx-capability-routing", "catlx-desktop-control"],
 "catlx-desktop-control": ["catlx-screen-understanding", "catlx-security", "catlx-electron-shell", "catlx-workflow-engine", "catlx-capability-routing"],
 "catlx-screen-understanding": ["catlx-hardware-adaptation", "catlx-capability-routing", "catlx-desktop-control", "catlx-security", "catlx-docker"],
 "catlx-memory": ["catlx-ai-provider", "catlx-workflow-engine", "catlx-hardware-adaptation", "catlx-portability"],
 "catlx-ai-provider": ["catlx-memory", "catlx-hardware-adaptation", "catlx-docker", "catlx-capability-routing", "catlx-security"],
 "catlx-workflow-engine": ["catlx-capability-routing", "catlx-ai-provider", "catlx-memory", "catlx-desktop-control", "catlx-security", "catlx-docker", "catlx-recovery", "catlx-telemetry"],
 "catlx-security": ["catlx-docker", "catlx-recovery", "catlx-telemetry", "catlx-plugin-ecosystem", "catlx-hardware-adaptation"],
 "catlx-telemetry": ["catlx-electron-shell", "catlx-ai-provider", "catlx-workflow-engine", "catlx-hardware-adaptation"],
 "catlx-electron-shell": ["catlx-hardware-adaptation", "catlx-telemetry", "catlx-memory", "catlx-capability-routing", "catlx-desktop-control"],
 "catlx-plugin-ecosystem": ["catlx-security", "catlx-silexis-modules", "catlx-electron-shell", "catlx-docker", "catlx-capability-routing"],
 "catlx-docker": ["catlx-capability-routing", "catlx-recovery", "catlx-portability", "catlx-security", "catlx-silexis-modules"],
 "catlx-portability": ["catlx-hardware-adaptation", "catlx-docker", "catlx-memory", "catlx-capability-routing"],
 "catlx-recovery": ["catlx-workflow-engine", "catlx-ai-provider", "catlx-docker", "catlx-memory", "catlx-security"],
 "catlx-runtime-lifecycle": ["catlx-voice-pipeline", "catlx-workflow-engine", "catlx-plugin-ecosystem", "catlx-electron-shell", "catlx-security", "catlx-recovery", "catlx-hardware-adaptation", "catlx-capability-routing"],
}

# canonical knowledge references per skill (from INDEX.md "References" column)
REFS = {
 "catlx": ["concepts/pillars-and-mandates.md", "rules/architectural-rules.md"],
 "catlx-hardware-adaptation": ["references/hardware-adaptation.md", "references/component-tree.md", "references/folder-structure.md", "rules/architectural-rules.md"],
 "catlx-silexis-modules": ["references/silexis-and-routing.md", "references/folder-structure.md", "references/data-registries.md"],
 "catlx-capability-routing": ["references/silexis-and-routing.md", "references/data-registries.md", "references/hardware-adaptation.md", "rules/windows-rules.md"],
 "catlx-voice-pipeline": ["references/voice-pipeline.md", "references/runtime-lifecycle.md", "references/hardware-adaptation.md"],
 "catlx-desktop-control": ["references/desktop-control.md", "references/screen-understanding.md", "rules/windows-rules.md", "references/security.md"],
 "catlx-screen-understanding": ["references/screen-understanding.md", "references/desktop-control.md", "references/hardware-adaptation.md", "references/security.md"],
 "catlx-memory": ["references/memory-architecture.md", "references/data-registries.md", "rules/architectural-rules.md"],
 "catlx-ai-provider": ["references/ai-provider.md", "references/memory-architecture.md", "references/hardware-adaptation.md"],
 "catlx-workflow-engine": ["references/workflow-engine.md", "references/runtime-lifecycle.md", "references/data-registries.md"],
 "catlx-security": ["references/security.md", "rules/windows-rules.md", "references/data-registries.md", "rules/architectural-rules.md"],
 "catlx-telemetry": ["references/telemetry.md", "references/data-registries.md", "references/hardware-adaptation.md"],
 "catlx-electron-shell": ["references/electron-shell.md", "rules/windows-rules.md", "references/data-registries.md", "references/hardware-adaptation.md"],
 "catlx-plugin-ecosystem": ["references/plugin-ecosystem.md", "references/security.md", "references/folder-structure.md", "references/data-registries.md"],
 "catlx-docker": ["references/docker.md", "rules/windows-rules.md", "references/portability.md", "references/data-registries.md"],
 "catlx-portability": ["references/portability.md", "references/folder-structure.md", "rules/windows-rules.md", "rules/architectural-rules.md"],
 "catlx-recovery": ["references/recovery.md", "references/runtime-lifecycle.md", "references/data-registries.md", "rules/architectural-rules.md"],
 "catlx-runtime-lifecycle": ["references/runtime-lifecycle.md", "references/recovery.md", "references/workflow-engine.md", "references/voice-pipeline.md", "references/plugin-ecosystem.md", "references/data-registries.md"],
}

# workflow artifacts per skill
WORKFLOWS = {
 "catlx-workflow-engine": ["workflows/summarize-clipboard.yaml"],
}

refs = json.loads(REG.read_text(encoding="utf-8"))
by_id = {s["id"]: s for s in refs["skills"]}
# the orchestrator can delegate to any subsystem skill (all except itself and the root)
subsystem_ids = [s["id"] for s in refs["skills"] if s["id"] not in ("catlx", "catlx-orchestrator")]
DELEGATES["catlx-orchestrator"] = subsystem_ids

skills = []
for sid in sorted(by_id.keys()):
    s = by_id[sid]
    caps = CAPS.get(sid, {})
    skills.append({
        "id": sid,
        "name": s["name"],
        "skill_type": s["skill_type"],
        "description": s["description"],
        "capabilities": caps.get("capabilities", []),
        "aliases": s.get("aliases", []),
        "depends_on": s.get("depends_on", []),
        "delegates_to": sorted(DELEGATES.get(sid, [])),
        "references": s.get("references", REFS.get(sid, [])),
        "workflows": WORKFLOWS.get(sid, []),
        "source": s.get("source", ""),
        "routing_hint": caps.get("hint", ""),
    })

# Compute deterministic, source-derived "capability -> skill" phrases for a capability-oriented index.
# (The per-skill 'capabilities' arrays already carry the action phrases; this adds the reverse map.)
capability_to_skill = {}
for sid, caps in CAPS.items():
    for c in caps.get("capabilities", []):
        capability_to_skill.setdefault(c.lower(), []).append(sid)
for k in sorted(capability_to_skill):
    capability_to_skill[k] = sorted(set(capability_to_skill[k]))

# Normalize intent keys to lower; map skill ids to ensure valid
intent = {k.lower(): [x for x in v if x in by_id] for k, v in INTENT.items()}
intent = {k: v for k, v in intent.items() if v}

out = {
    "manifest_version": 1,
    "name": "CATLX capability index (deterministic routing core)",
    "purpose": "Map natural-language intents to CATLX skills so a small model can route without scanning the whole ecosystem.",
    "note": "This is a view over the canonical skill registry, NOT a second knowledge base.",
    "routing_data": ["metadata/skills-registry.json", "metadata/dependency-graph.json"],
    "intent_to_skills": intent,
    "capability_to_skill": capability_to_skill,
    "match_strategy": (
        "1) Exact request match in intent_to_skills wins. "
        "2) Else score every intent key by how many of its tokens appear in the request (token overlap), "
        "preferring longer keys that fully appear; pick the highest score. "
        "3) If a request contains a diagnostic word (failing, broken, diagnose, why, wrong, debug, "
        "troubleshoot), bias toward recovery/telemetry-capable intents over pure deployment/config intents. "
        "4) Else fall back to capability_to_skill phrase overlap. "
        "5) Translate the chosen skill id via skills[].delegates_to / depends_on for deeper traversal."
    ),
    "skills": skills,
}
OUT.write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")
print(f"Wrote {OUT.relative_to(ROOT)} with {len(skills)} skills and {len(intent)} intent entries.")
