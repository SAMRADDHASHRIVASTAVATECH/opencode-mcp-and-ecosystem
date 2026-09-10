"""Map of specialist MCPs and skills — reuse, do not duplicate."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from se_mcp.config import SETTINGS

SPECIALISTS = [
    {
        "id": "office-documents",
        "module": "office_mcp",
        "dir": "office-documents-mcp",
        "when": ["docx", "xlsx", "pptx", "word", "excel", "powerpoint", "spreadsheet", "office document"],
        "tools_hint": ["office_create", "word_edit", "excel_write", "pptx_edit"],
        "do_not_rebuild": "Office Open XML authoring",
    },
    {
        "id": "database-sql",
        "module": "database_mcp",
        "dir": "database-sql-mcp",
        "when": ["sql", "sqlite", "postgres", "mysql", "database schema", "duckdb"],
        "tools_hint": ["db_connect", "db_query", "db_introspect"],
        "do_not_rebuild": "SQL execution and schema inspection",
    },
    {
        "id": "windows-system",
        "module": "windows_mcp",
        "dir": "windows-system-mcp",
        "when": ["printer", "spooler", "windows service", "win32", "cim", "print job"],
        "tools_hint": ["win_diagnose_printer", "win_services"],
        "do_not_rebuild": "Windows admin / print stack",
    },
    {
        "id": "android-development",
        "module": "android_mcp",
        "dir": "android-development-mcp",
        "when": ["android", "apk", "aab", "jetpack compose", "gradle android", "adb", "avd"],
        "tools_hint": ["android_create_project", "android_gradle", "android_devices"],
        "do_not_rebuild": "Android app lifecycle",
    },
]


def ecosystem_root() -> Path:
    r = SETTINGS.ecosystem_root
    if (r / "office-documents-mcp").exists() or (r / "android-development-mcp").exists():
        return r
    # software-engineering-mcp/src/se_mcp → repo parent
    here = Path(__file__).resolve()
    for p in [here.parents[i] for i in range(2, min(6, len(here.parents)))]:
        if (p / "office-documents-mcp").exists():
            return p
    return r


def snapshot() -> dict[str, Any]:
    root = ecosystem_root()
    specialists = []
    for spec in SPECIALISTS:
        d = root / spec["dir"]
        specialists.append({**spec, "installed": d.exists(), "path": str(d) if d.exists() else None})
    skills_root = root / "skills"
    skills = []
    if skills_root.exists():
        for p in sorted(skills_root.glob("*/SKILL.md")):
            skills.append({"id": p.parent.name, "path": str(p)})
    return {
        "ecosystem_root": str(root),
        "specialists": specialists,
        "skills": skills,
        "this_mcp": "software-engineering",
        "rule": "Route domain work to specialists. This MCP handles general software engineering and orchestration.",
    }


def route(request: str) -> dict[str, Any]:
    q = (request or "").lower()
    hits = []
    for spec in SPECIALISTS:
        score = sum(1 for k in spec["when"] if k in q)
        if score:
            hits.append({**spec, "score": score})
    hits.sort(key=lambda h: h["score"], reverse=True)
    stack = infer_stack(q)
    return {
        "request": request,
        "specialist": hits[0] if hits else None,
        "also": hits[1:3],
        "local_stack": stack,
        "use_this_mcp": not hits or stack is not None,
        "advice": _advice(hits, stack, q),
        "skills": _skills_for(q, hits),
    }


def infer_stack(q: str) -> str | None:
    mapping = [
        (("android", "apk", "compose"), None),  # specialist
        (("fastapi", "python api"), "python-fastapi"),
        (("flask",), "python-flask"),
        (("python library", "pypi", "python package"), "python-lib"),
        (("python cli", "click", "argparse"), "python-cli"),
        (("express", "node api", "node backend"), "node-express"),
        (("node cli", "npm cli"), "node-cli"),
        (("node library", "npm package"), "node-library"),
        (("static site", "html page", "landing page"), "static-web"),
        (("electron", "desktop"), "python-desktop"),
        (("tkinter", "desktop"), "python-desktop"),
        (("go cli", "golang"), "go-cli"),
        (("rust cli", "cargo"), "rust-cli"),
        (("java cli",), "java-cli"),
        (("c program", "makefile"), "c-cli"),
        (("rest api", "http api", "backend"), "python-fastapi"),
        (("cli", "command line"), "python-cli"),
        (("library", "sdk"), "python-lib"),
        (("web app", "website"), "static-web"),
    ]
    for keys, stack in mapping:
        if any(k in q for k in keys):
            return stack
    return None


def _advice(hits: list, stack: str | None, q: str) -> list[str]:
    out = []
    if hits:
        out.append(f"Use specialist MCP '{hits[0]['id']}' for domain operations; do not reimplement {hits[0]['do_not_rebuild']}.")
    if stack:
        out.append(f"Scaffold with se_create_project template={stack} then se_build / se_test.")
    if not hits and not stack:
        out.append("Clarify target: language, app kind (cli/lib/api/web/desktop), then se_plan.")
    if "ios" in q or "swiftui" in q:
        out.append("iOS is not covered by a specialist here; do not pretend Android MCP can build iOS.")
    return out


def _skills_for(q: str, hits: list) -> list[str]:
    skills = ["software-engineering", "technology-selection"]
    if hits:
        skills.append("mcp-routing")
    if any(k in q for k in ("test", "qa")):
        skills.append("testing")
    if any(k in q for k in ("debug", "crash", "fail")):
        skills.append("debugging")
    if any(k in q for k in ("secure", "auth", "owasp")):
        skills.append("security")
    if any(k in q for k in ("deploy", "release", "package")):
        skills.append("release-engineering")
    if any(k in q for k in ("architect", "design", "module")):
        skills.append("architecture")
    return skills
