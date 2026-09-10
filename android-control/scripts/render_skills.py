#!/usr/bin/env python3
"""Render the skill catalogue to skills/<name>/SKILL.md + skills/INDEX.md.

The callable catalogue lives in code (android_control.skills.ALL_SKILLS); this
makes each skill travel as human/agent-readable markdown in the package.
Run from the repo root:
    PYTHONPATH=src python scripts/render_skills.py
"""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
OUT = ROOT / "skills"

META = {
    "android_control": ("Universal Android Control Master", "master", ()),
    "android_discovery": ("Discover connected Android devices", "discovery", ()),
    "android_adb": ("ADB engine: server, devices, connect/pair", "adb", ()),
    "android_shell": ("Run checked Android shell commands", "shell", ()),
    "android_device_info": ("Read the full device profile", "device-info", ()),
    "android_input": ("Inject taps, swipes, text and key events", "input", ()),
    "android_screen": ("Screenshots, screen recording, display info", "screen", ()),
    "android_ui": ("Semantic UI hierarchy, find/click/type", "ui", ()),
    "android_apps": ("List/launch/stop/inspect applications", "apps", ()),
    "android_files": ("Push/pull/list/verify files", "files", ()),
    "android_intents": ("Fire Android intents", "intents", ()),
    "android_vision": ("Visual fallback observation", "vision", ()),
    "android_recovery": ("Reconnect & self-heal devices", "recovery", ()),
    "android_multi_device": ("Fleet overview, groups, parallel control", "multi-device", ()),
    "android_messaging": ("Agent<->device messaging channel", "messaging", ()),
    "android_remote_touchpad": ("Remote-Touchpad host: phone as PC touchpad/keyboard", "remote-touchpad", ()),
}


def _doc(skill):
    fn = skill.__doc__ or ""
    return " ".join(l.strip() for l in fn.splitlines() if l.strip()).strip() or \
        META.get(skill.__name__, (skill.__name__, "", ()))[0]


def main():
    from android_control.skills import ALL_SKILLS
    OUT.mkdir(parents=True, exist_ok=True)
    index = ["# android-control skills",
             "",
             "Each skill is an independently callable module under "
             "``android_control.skills``; the master skill orchestrates them. "
             "No device limit is assumed.\n"]
    for name, fn in ALL_SKILLS.items():
        d = OUT / name
        d.mkdir(parents=True, exist_ok=True)
        short, kind, _ = META.get(name, (name, "", ()))
        body = (f"# {name}\n\n{_doc(fn)}\n\n"
                f"- kind: `{kind or name}`\n"
                f"- callable: ``android_control.skills.{name}``\n"
                f"- master orchestrates: ``android_control``\n")
        (d / "SKILL.md").write_text(body)
        index.append(f"- `{name}` — {short}")
    (OUT / "INDEX.md").write_text("\n".join(index) + "\n")
    print(f"rendered {len(ALL_SKILLS)} skills into {OUT}")


if __name__ == "__main__":
    main()
