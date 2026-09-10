from __future__ import annotations

import os
import platform
import shutil
from typing import Any

TOOLS = [
    "python3",
    "python",
    "pip",
    "pip3",
    "node",
    "npm",
    "pnpm",
    "yarn",
    "git",
    "gcc",
    "g++",
    "make",
    "cmake",
    "javac",
    "java",
    "mvn",
    "gradle",
    "go",
    "cargo",
    "rustc",
    "dotnet",
    "php",
    "ruby",
    "docker",
    "docker-compose",
    "kubectl",
    "terraform",
    "ruff",
    "pytest",
    "eslint",
    "tsc",
]


def detect() -> dict[str, Any]:
    found = {name: shutil.which(name) for name in TOOLS}
    langs = []
    if found["python3"] or found["python"]:
        langs.append("python")
    if found["node"]:
        langs.append("javascript/typescript")
    if found["javac"]:
        langs.append("java")
    if found["gcc"]:
        langs.append("c")
    if found["g++"]:
        langs.append("cpp")
    if found["go"]:
        langs.append("go")
    if found["cargo"]:
        langs.append("rust")
    if found["dotnet"]:
        langs.append("csharp")
    if found["php"]:
        langs.append("php")
    if found["ruby"]:
        langs.append("ruby")
    return {
        "os": platform.system(),
        "platform": platform.platform(),
        "arch": platform.machine(),
        "python": platform.python_version(),
        "tools": {k: v for k, v in found.items() if v},
        "missing_common": [k for k, v in found.items() if not v and k in {"go", "cargo", "dotnet", "docker", "php", "ruby"}],
        "languages_available": langs,
        "git": bool(found["git"]),
        "docker": bool(found["docker"]),
        "can_python": bool(found["python3"] or found["python"]),
        "can_node": bool(found["node"] and found["npm"]),
        "can_c": bool(found["gcc"] and found["make"]),
        "can_java": bool(found["javac"]),
        "can_go": bool(found["go"]),
        "can_rust": bool(found["cargo"]),
        "cwd": os.getcwd(),
    }
