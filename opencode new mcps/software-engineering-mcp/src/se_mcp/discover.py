from __future__ import annotations

from pathlib import Path
from typing import Any

MARKERS = {
    "pyproject.toml": "python-packaging",
    "setup.py": "python-setuptools",
    "requirements.txt": "python-pip",
    "Pipfile": "python-pipenv",
    "package.json": "node",
    "pnpm-lock.yaml": "pnpm",
    "yarn.lock": "yarn",
    "Cargo.toml": "rust",
    "go.mod": "go",
    "pom.xml": "maven",
    "build.gradle": "gradle",
    "build.gradle.kts": "gradle-kts",
    "settings.gradle.kts": "android-or-gradle",
    "CMakeLists.txt": "cmake",
    "Makefile": "make",
    "Gemfile": "ruby",
    "composer.json": "php",
    "*.csproj": "dotnet",
    "Dockerfile": "docker",
    "docker-compose.yml": "compose",
    "AndroidManifest.xml": "android",
}


def discover(root: Path, max_files: int = 400) -> dict[str, Any]:
    markers: dict[str, str] = {}
    files = 0
    langs = set()
    tests = []
    for p in root.rglob("*"):
        if files >= max_files:
            break
        if not p.is_file():
            continue
        if any(part in {".git", "node_modules", ".venv", "dist", "build", "__pycache__"} for part in p.parts):
            continue
        files += 1
        name = p.name
        if name in MARKERS:
            markers[name] = MARKERS[name]
        suf = p.suffix.lower()
        langmap = {
            ".py": "python",
            ".js": "javascript",
            ".ts": "typescript",
            ".go": "go",
            ".rs": "rust",
            ".java": "java",
            ".kt": "kotlin",
            ".c": "c",
            ".cpp": "cpp",
            ".cs": "csharp",
            ".rb": "ruby",
            ".php": "php",
            ".html": "html",
        }
        if suf in langmap:
            langs.add(langmap[suf])
        if "test" in name.lower() or p.parent.name in {"tests", "test", "__tests__"}:
            tests.append(str(p.relative_to(root)))
    kind = _kind(markers, langs)
    return {
        "root": str(root),
        "markers": markers,
        "languages": sorted(langs),
        "kind": kind,
        "test_files_sample": tests[:30],
        "build": _build_cmd(kind, markers),
        "test": _test_cmd(kind, markers),
        "run": _run_cmd(kind, root),
        "android": "AndroidManifest.xml" in markers or "settings.gradle.kts" in markers,
        "route_if_android": "android-development-mcp" if ("AndroidManifest.xml" in markers or "settings.gradle.kts" in markers) else None,
    }


def _kind(markers: dict[str, str], langs: set[str]) -> str:
    if "AndroidManifest.xml" in markers or "settings.gradle.kts" in markers:
        return "android"
    if "Cargo.toml" in markers:
        return "rust"
    if "go.mod" in markers:
        return "go"
    if "pom.xml" in markers:
        return "maven-java"
    if "package.json" in markers:
        return "node"
    if "pyproject.toml" in markers or "setup.py" in markers or "requirements.txt" in markers:
        return "python"
    if "CMakeLists.txt" in markers or "Makefile" in markers:
        return "native-c"
    if "html" in langs:
        return "static-web"
    return "unknown"


def _build_cmd(kind: str, markers: dict[str, str]) -> list[str] | None:
    return {
        "python": ["python3", "-m", "pip", "install", "-e", "."],
        "node": ["npm", "run", "build"],
        "rust": ["cargo", "build"],
        "go": ["go", "build", "./..."],
        "maven-java": ["mvn", "-q", "package"],
        "native-c": ["make"],
        "android": None,
    }.get(kind)


def _test_cmd(kind: str, markers: dict[str, str]) -> list[str] | None:
    return {
        "python": ["python3", "-m", "pytest", "-q"],
        "node": ["npm", "test", "--silent"],
        "rust": ["cargo", "test"],
        "go": ["go", "test", "./..."],
        "maven-java": ["mvn", "-q", "test"],
        "native-c": ["make", "test"],
        "android": None,
    }.get(kind)


def _run_cmd(kind: str, root: Path) -> list[str] | None:
    if kind == "python":
        if (root / "src").exists():
            return ["python3", "-m"]
        return ["python3"]
    if kind == "node":
        return ["npm", "start"]
    if kind == "go":
        return ["go", "run", "."]
    if kind == "rust":
        return ["cargo", "run"]
    return None
