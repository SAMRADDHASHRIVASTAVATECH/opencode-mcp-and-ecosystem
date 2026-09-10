"""21-phase SDLC catalog and structure templates (from Universal SDLC Generator)."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from se_mcp.sdlc_data import PROJECT_AUDIENCES, PROJECT_CATEGORIES, SDLC_PHASES


def get_structure_template(project_name: str, complexity: str) -> dict[str, Any]:
    if complexity == "LOW":
        return {
            project_name: {
                "src/": {"main.py": "P6 Core Logic | P7 I/O", "utils.py": "P9 Helpers", "config.py": "P11 Config"},
                "data/": {"input/": "P7 Input", "output/": "P7 Output"},
                "tests/": {"test_main.py": "P12 Tests"},
                "docs/": {"notes.md": "P18 Notes"},
                "README.md": "P1 Purpose | P2 Reqs",
                ".env.example": "P10 Secrets",
                ".gitignore": "P19 Git Ignore",
                "requirements.txt": "P14 Deps",
            }
        }
    if complexity == "MEDIUM":
        return {
            project_name: {
                "assets/": {"images/": "P5 UX", "diagrams/": "P4 Design"},
                "config/": {"settings.py": "P11 Config", ".env.example": "P10 Secrets"},
                "data/": {"raw/": "P7 Data", "processed/": "P8 Storage"},
                "docs/": {"design.md": "P4 System", "api.md": "P5 API"},
                "src/": {
                    "core/": {"engine.py": "P6 Logic", "models.py": "P8 Models"},
                    "api/": {"routes.py": "P7 I/O"},
                    "utils/": {"helpers.py": "P16 Utils"},
                    "main.py": "P13 Entry",
                },
                "tests/": {"unit/": {"test_core.py": "P12 Tests"}, "conftest.py": "P12 Config"},
                "README.md": "P1 Purpose",
                "CHANGELOG.md": "P20 History",
                "requirements.txt": "P14 Deps",
                "Makefile": "P13 Build",
            }
        }
    return {
        project_name: {
            "assets/": {"architecture/": "P4 ADRs", "branding/": "P5 Assets"},
            "config/": {"environments/": {"dev.yml": "P11", "prod.yml": "P11"}},
            "deploy/": {"docker/": "P14 Docker", "kubernetes/": "P14 K8s", "terraform/": "P14 IaC"},
            "docs/": {"api/": "P5 Specs", "architecture/": "P4 Docs", "runbooks/": "P14 Ops"},
            "src/": {
                "domain/": {"models.py": "P8 Entities", "business_logic.py": "P6 Rules"},
                "infrastructure/": {"database.py": "P8 DB", "security.py": "P10 Auth"},
                "interface/": {"api/": "P7 Routes", "cli/": "P7 CLI"},
                "main.py": "P13 Entry",
            },
            "tests/": {"unit/": "P12", "integration/": "P12", "e2e/": "P12", "performance/": "P17"},
            "monitoring/": {"dashboards/": "P15 UI", "alerts/": "P15 Alerts"},
            ".github/": {"workflows/": "P14 CI/CD"},
            "README.md": "P1 Docs",
            "SECURITY.md": "P10 Sec",
            "requirements.txt": "P14",
            "Makefile": "P13 Make",
        }
    }


def blended_complexity(audience: str | None, category: str | None) -> str:
    val = {"LOW": 1, "MEDIUM": 2, "HIGH": 3}
    a = PROJECT_AUDIENCES.get(audience or "", None)
    c = PROJECT_CATEGORIES.get(category or "", {}).get("complexity") if category else None
    if a and c:
        avg = (val[a] + val[c]) / 2.0
        if avg < 1.6:
            return "LOW"
        if avg < 2.6:
            return "MEDIUM"
        return "HIGH"
    return a or c or "MEDIUM"


def catalog_summary() -> dict[str, Any]:
    return {
        "audiences": list(PROJECT_AUDIENCES.keys()),
        "categories": [
            {"name": k, "complexity": v["complexity"], "description": v.get("description"), "types": v["items"]}
            for k, v in PROJECT_CATEGORIES.items()
        ],
        "phases": [
            {"id": pk, **{x: d[x] for x in ("name", "short", "icon", "description", "depth_low", "depth_medium", "depth_high")}}
            for pk, d in SDLC_PHASES.items()
        ],
        "category_count": len(PROJECT_CATEGORIES),
        "phase_count": len(SDLC_PHASES),
    }


def search_types(query: str, limit: int = 20) -> list[dict[str, str]]:
    q = (query or "").lower().strip()
    hits = []
    for cat, data in PROJECT_CATEGORIES.items():
        for item in data["items"]:
            blob = f"{cat} {item} {data.get('description','')}".lower()
            if q in blob:
                hits.append({"category": cat, "type": item, "complexity": data["complexity"]})
            if len(hits) >= limit:
                return hits
    return hits


def build_tree_lines(structure: dict[str, Any], prefix: str = "") -> list[str]:
    lines = []
    items = list(structure.items())
    for i, (name, content) in enumerate(items):
        last = i == len(items) - 1
        branch = "└── " if last else "├── "
        extra = f"  ← {content}" if isinstance(content, str) else ""
        lines.append(f"{prefix}{branch}{name}{extra}")
        if isinstance(content, dict):
            lines.extend(build_tree_lines(content, prefix + ("    " if last else "│   ")))
    return lines


def generate_blueprint(
    project_name: str,
    audience: str,
    category: str,
    type_name: str,
    complexity: str | None = None,
) -> dict[str, Any]:
    name = project_name.replace(" ", "_").replace("-", "_")
    level = complexity or blended_complexity(audience, category)
    structure = get_structure_template(name, level)
    phase_lines = []
    for pk, d in SDLC_PHASES.items():
        depth = d.get(f"depth_{level.lower()}", "Standard")
        phase_lines.append(f"{d['icon']} {pk.replace('PHASE_', 'P'):4} {d['name']:25} → {depth}")
    ascii_tree = "\n".join(build_tree_lines(structure))
    return {
        "project_name": name,
        "audience": audience,
        "category": category,
        "type": type_name,
        "complexity": level,
        "structure": structure,
        "ascii_tree": ascii_tree,
        "phases": phase_lines,
        "route_hint": _route_hint(category, type_name),
    }


def _route_hint(category: str, type_name: str) -> str:
    blob = f"{category} {type_name}".lower()
    if "android" in blob:
        return "android-development-mcp"
    if "office" in blob or "spreadsheet" in blob or "word processor" in blob:
        return "office-documents-mcp"
    if "database" in blob or "sql" in blob:
        return "database-sql-mcp"
    if "printer" in blob or "windows" in blob and "os" in blob:
        return "windows-system-mcp"
    return "software-engineering-mcp"


def export_structure(base_dir: Path, structure: dict[str, Any]) -> dict[str, Any]:
    created = {"dirs": 0, "files": 0}

    def rec(current: Path, struct: dict[str, Any]) -> None:
        for name, content in struct.items():
            as_dir = isinstance(content, dict) or str(name).endswith("/")
            path = current / str(name).rstrip("/\\")
            if as_dir:
                path.mkdir(parents=True, exist_ok=True)
                created["dirs"] += 1
                if isinstance(content, dict):
                    rec(path, content)
                else:
                    note = path / "README.md"
                    if not note.exists():
                        note.write_text(f"# {path.name}\n\nContext: {content}\n", encoding="utf-8")
                        created["files"] += 1
            else:
                path.parent.mkdir(parents=True, exist_ok=True)
                if not path.exists():
                    path.write_text(f"# Auto-generated\n# Context: {content}\n\n", encoding="utf-8")
                    created["files"] += 1

    rec(base_dir, structure)
    created["base"] = str(base_dir)
    return created
