from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from se_mcp.discover import discover

SECRET = re.compile(r"(api[_-]?key|secret|password|token)\s*[:=]\s*['\"][^'\"]{8,}['\"]", re.I)
TODO = re.compile(r"\b(TODO|FIXME|HACK|XXX)\b")


def analyze(root: Path) -> dict[str, Any]:
    info = discover(root)
    secrets, todos, evals = [], [], []
    for p in root.rglob("*"):
        if not p.is_file() or p.suffix.lower() not in {".py", ".js", ".ts", ".go", ".rs", ".java", ".kt", ".c", ".env", ".json"}:
            continue
        if any(x in p.parts for x in {".git", "node_modules", ".venv", "dist", "__pycache__"}):
            continue
        try:
            text = p.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        rel = str(p.relative_to(root))
        if SECRET.search(text):
            secrets.append(rel)
        if TODO.search(text):
            todos.append(rel)
        if re.search(r"\beval\s*\(|exec\s*\(|pickle\.loads|innerHTML\s*=", text):
            evals.append(rel)
    info["secrets"] = secrets[:40]
    info["todos"] = todos[:40]
    info["dangerous_apis"] = evals[:40]
    return info


DIAG = [
    (r"ModuleNotFoundError|No module named", "Missing Python package — se_deps or pip install", "python"),
    (r"Cannot find module|ERR! code ERESOLVE", "Node dependency/resolution — npm install", "node"),
    (r"error: failed to run custom build command|linker `cc` not found", "Rust needs C toolchain", "rust"),
    (r"go: cannot find module", "Go module missing — go mod tidy", "go"),
    (r"javac: command not found", "JDK missing", "java"),
    (r"SDK location not found|ANDROID_HOME", "Android SDK — use android_detect_environment", "android"),
    (r"ECONNREFUSED|connection refused", "Service not listening / wrong port", "network"),
    (r"PermissionError|EACCES|Access is denied", "Filesystem permissions", "os"),
    (r"SyntaxError", "Syntax error in source", "syntax"),
    (r"FAILED|AssertionError", "Test assertion failed", "test"),
]


def diagnose(log: str) -> dict[str, Any]:
    hits = []
    for pat, cause, kind in DIAG:
        if re.search(pat, log, re.I):
            hits.append({"pattern": pat, "cause": cause, "kind": kind})
    if not hits:
        hits.append({"pattern": None, "cause": "Unrecognized. Inspect last error line; se_discover_project.", "kind": "unknown"})
    return {"matches": hits, "primary": hits[0]}
