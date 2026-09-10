from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

from se_mcp import language_catalog
from se_mcp.analyze import analyze, diagnose
from se_mcp.ascii_tree import create_from_tree, folder_to_ascii_tree, parse_ascii_tree, preview_boilerplate
from se_mcp.config import SETTINGS
from se_mcp.discover import discover
from se_mcp.ecosystem import route, snapshot
from se_mcp.env import detect
from se_mcp.errors import NotFoundError, ValidationError
from se_mcp.results import run
from se_mcp.runner import run_cmd
from se_mcp.scaffold import TEMPLATES, create_project
from se_mcp.sdlc import catalog_summary, export_structure, generate_blueprint, search_types
from se_mcp.security import ensure_writable, require_confirm, safe_path
from se_mcp.toolchain import execute


def register(mcp: Any) -> None:
    @mcp.tool()
    def se_detect_environment() -> dict[str, Any]:
        """Detect languages, compilers, package managers, git, docker on this host. Never assume a toolchain exists."""
        return run(detect)

    @mcp.tool()
    def se_ecosystem() -> dict[str, Any]:
        """Map installed specialist MCPs (office, database, windows, android) and skills. Use this before duplicating work."""
        return run(snapshot)

    @mcp.tool()
    def se_route(request: str) -> dict[str, Any]:
        """Given a natural-language build request, choose specialist MCP vs local stack vs skills. Does not execute."""
        return run(route, request=request)

    @mcp.tool()
    def se_plan(goal: str, project: str | None = None) -> dict[str, Any]:
        """Produce a sequenced engineering plan: route, scaffold or inspect, implement, build, test, audit, package."""
        return run(_plan, goal=goal, project=project)

    @mcp.tool()
    def se_discover_project(path: str) -> dict[str, Any]:
        """Inspect a directory: languages, build markers, tests, Android routing."""
        return run(lambda: discover(safe_path(path, must_exist=True)))

    @mcp.tool()
    def se_create_project(
        path: str,
        name: str,
        template: str,
        overwrite: bool = False,
    ) -> dict[str, Any]:
        """Create a real project. Templates: python-cli, python-lib, python-fastapi, python-flask, python-desktop, node-cli, node-express, node-library, static-web, java-cli, c-cli, go-cli, rust-cli.

        Android apps: use android_create_project instead. Office/SQL/Windows admin: specialist MCPs.
        """
        return run(_create, path=path, name=name, template=template, overwrite=overwrite)

    @mcp.tool()
    def se_build(project: str) -> dict[str, Any]:
        """Build using the detected toolchain (compileall/npm/make/cargo/go). Android projects are refused and routed."""
        return run(lambda: execute(safe_path(project, must_exist=True), "build"))

    @mcp.tool()
    def se_test(project: str) -> dict[str, Any]:
        """Run tests (pytest, npm test, cargo test, go test, make). Android → android_run_tests."""
        return run(lambda: execute(safe_path(project, must_exist=True), "test"))

    @mcp.tool()
    def se_run(project: str) -> dict[str, Any]:
        """Run the project's default entry (CLI module, npm start, make run)."""
        return run(lambda: execute(safe_path(project, must_exist=True), "run"))

    @mcp.tool()
    def se_deps(
        project: str,
        action: str = "list",
        package: str | None = None,
        confirm: bool = False,
    ) -> dict[str, Any]:
        """List or add dependencies. action=list|add. add requires confirm=true (network)."""
        return run(_deps, project=project, action=action, package=package, confirm=confirm)

    @mcp.tool()
    def se_analyze(project: str) -> dict[str, Any]:
        """Structure + secret/TODO/dangerous API scan."""
        return run(lambda: analyze(safe_path(project, must_exist=True)))

    @mcp.tool()
    def se_diagnose(log: str) -> dict[str, Any]:
        """Map a build/test log to likely cause and next action."""
        return run(diagnose, log=log)

    @mcp.tool()
    def se_security_audit(project: str) -> dict[str, Any]:
        """Generic secret/eval audit. Android projects also recommend android_security_audit."""
        return run(_sec, project=project)

    @mcp.tool()
    def se_document(project: str, dest: str | None = None) -> dict[str, Any]:
        """Write or refresh README.md from se_discover_project (does not overwrite unless dest set or README missing)."""
        return run(_doc, project=project, dest=dest)

    @mcp.tool()
    def se_package(project: str) -> dict[str, Any]:
        """Explain/run packaging: python -m build if available, npm pack, make. Does not publish."""
        return run(_pkg, project=project)

    @mcp.tool()
    def se_git(project: str, action: str = "status") -> dict[str, Any]:
        """Git snapshot: status, diff, log. No push, no force."""
        return run(_git, project=project, action=action)

    @mcp.tool()
    def se_quality(project: str) -> dict[str, Any]:
        """Run ruff or eslint --version presence checks; ruff check if installed."""
        return run(_quality, project=project)

    @mcp.tool()
    def se_ascii_tree(
        action: str,
        ascii_tree: str | None = None,
        path: str | None = None,
        inject_boilerplate: bool = True,
        confirm: bool = False,
    ) -> dict[str, Any]:
        """ASCII file-tree workflow from the Tree Creator app.

        action=parse — parse an ASCII tree into (path, dir|file) rows.
        action=preview — show interconnected language boilerplate without writing.
        action=scan — render an existing folder as an ASCII tree (path required).
        action=create — materialize folders/files under path (confirm=true required).
        """
        return run(
            _ascii,
            action=action,
            ascii_tree=ascii_tree,
            path=path,
            inject_boilerplate=inject_boilerplate,
            confirm=confirm,
        )

    @mcp.tool()
    def se_sdlc(
        action: str,
        query: str | None = None,
        project_name: str | None = None,
        audience: str | None = None,
        category: str | None = None,
        type_name: str | None = None,
        complexity: str | None = None,
        path: str | None = None,
        confirm: bool = False,
        limit: int = 20,
    ) -> dict[str, Any]:
        """Universal SDLC generator (21 phases, audience × category taxonomy).

        action=catalog — audiences, categories, phases.
        action=search — find project types (query).
        action=generate — blueprint + ASCII tree (project_name, audience, category, type_name).
        action=export — write the generated structure to path (confirm=true).
        """
        return run(
            _sdlc,
            action=action,
            query=query,
            project_name=project_name,
            audience=audience,
            category=category,
            type_name=type_name,
            complexity=complexity,
            path=path,
            confirm=confirm,
            limit=limit,
        )

    @mcp.tool()
    def se_launch_gui(app: str) -> dict[str, Any]:
        """Launch a desktop GUI: app=ascii_tree (file-system creator) or app=sdlc (SDLC generator). Non-blocking."""
        return run(_launch_gui, app=app)

    @mcp.tool()
    def se_language_catalog(
        action: str,
        query: str | None = None,
        name: str | None = None,
        tag: str | None = None,
        limit: int = 25,
    ) -> dict[str, Any]:
        """Extreme Language & Project Advisor catalog: 5 tiers, 25 categories, 152 languages.

        action=summary — tiers/category names/counts/languages/abstraction levels.
        action=categories — all 25 categories with their grouped languages.
        action=search — find languages by name, tag or category keyword (query).
        action=get — full record for one language (name).
        action=by_tag — languages carrying a tag (tag).
        """
        return run(_language_catalog, action=action, query=query, name=name, tag=tag, limit=limit)


def _plan(goal: str, project: str | None) -> dict[str, Any]:
    r = route(goal)
    steps = [
        {"tool": "se_detect_environment", "why": "Know host compilers/package managers"},
        {"tool": "se_ecosystem", "why": "Reuse office/database/windows/android MCPs"},
        {"tool": "se_route", "why": "Confirm specialist vs local stack"},
    ]
    if r.get("specialist"):
        steps.append({"mcp": r["specialist"]["id"], "why": r["specialist"]["do_not_rebuild"], "tools": r["specialist"]["tools_hint"]})
    if r.get("local_stack"):
        steps.append({"tool": "se_create_project", "args": {"template": r["local_stack"]}})
        steps.append({"tool": "se_test"})
        steps.append({"tool": "se_security_audit"})
    if project:
        steps.append({"tool": "se_discover_project", "path": project})
        steps.append({"tool": "se_analyze"})
        steps.append({"tool": "se_build"})
        steps.append({"tool": "se_test"})
    steps.append({"skill": "software-engineering", "why": "Follow the one-person-team workflow"})
    return {"goal": goal, "route": r, "steps": steps, "skills": r.get("skills")}


def _create(path, name, template, overwrite):
    ensure_writable()
    return create_project(safe_path(path), name=name, template=template, overwrite=overwrite)


def _deps(project, action, package, confirm):
    root = safe_path(project, must_exist=True)
    info = discover(root)
    if action == "list":
        listing = {}
        for fname in ("pyproject.toml", "requirements.txt", "package.json", "Cargo.toml", "go.mod"):
            p = root / fname
            if p.exists():
                listing[fname] = p.read_text(encoding="utf-8")[:4000]
        return {"kind": info["kind"], "files": listing}
    if action == "add":
        require_confirm(confirm, "install dependency")
        ensure_writable()
        if not package or not re.match(r"^[\w.@/+\-]+$", package):
            raise ValidationError("package name looks unsafe")
        if info["kind"] == "python":
            return run_cmd(["python3", "-m", "pip", "install", package], cwd=str(root), timeout=SETTINGS.timeout)
        if info["kind"] == "node":
            return run_cmd(["npm", "install", package], cwd=str(root), timeout=SETTINGS.timeout)
        raise ValidationError(f"Cannot add deps for kind={info['kind']}")
    raise ValidationError("action list|add")


def _sec(project):
    root = safe_path(project, must_exist=True)
    data = analyze(root)
    extra = []
    if data.get("android"):
        extra.append("Also run android_security_audit on the Android MCP.")
    return {**data, "recommendations": extra}


def _doc(project, dest):
    ensure_writable()
    root = safe_path(project, must_exist=True)
    info = discover(root)
    md = f"""# {root.name}

Generated by software-engineering MCP.

- Kind: {info['kind']}
- Languages: {', '.join(info['languages']) or 'unknown'}
- Markers: {', '.join(info['markers']) or 'none'}
- Build: {' '.join(info['build'] or []) or 'n/a'}
- Test: {' '.join(info['test'] or []) or 'n/a'}

## Ecosystem

Do not reimplement Office/SQL/Windows/Android specialists. See se_ecosystem / se_route.
"""
    out = safe_path(dest) if dest else root / "README.md"
    if out.exists() and not dest:
        return {"skipped": True, "path": str(out), "note": "README exists; pass dest to write another file"}
    out.write_text(md, encoding="utf-8")
    return {"path": str(out)}


def _pkg(project):
    root = safe_path(project, must_exist=True)
    info = discover(root)
    if info["kind"] == "python":
        return {"kind": "python", "commands": ["python3 -m pip install build", "python3 -m build"], "note": "Does not publish to PyPI"}
    if info["kind"] == "node":
        return run_cmd(["npm", "pack", "--dry-run"], cwd=str(root), timeout=60)
    if info["kind"] == "rust":
        return {"commands": ["cargo package"]}
    return {"kind": info["kind"], "note": "No standard packager detected"}


def _git(project, action):
    root = safe_path(project, must_exist=True)
    if action not in {"status", "diff", "log"}:
        raise ValidationError("git action must be status|diff|log")
    args = ["git", "-C", str(root), action]
    if action == "log":
        args += ["-5", "--oneline"]
    if action == "diff":
        args += ["--stat"]
    return run_cmd(args, timeout=30)


def _quality(project):
    root = safe_path(project, must_exist=True)
    info = discover(root)
    out = {"kind": info["kind"], "ran": []}
    from shutil import which

    if info["kind"] == "python" and which("ruff"):
        out["ruff"] = run_cmd(["ruff", "check", str(root)], timeout=60)
        out["ran"].append("ruff")
    elif info["kind"] == "python":
        out["note"] = "ruff not installed; skip"
    if info["kind"] == "node" and which("npx"):
        out["note"] = "eslint not auto-run; add an npm script"
    return out


def _parse_or_raise(ascii_tree: str):
    try:
        return parse_ascii_tree(ascii_tree)
    except ValueError as exc:
        raise ValidationError(str(exc)) from exc


def _ascii(action, ascii_tree, path, inject_boilerplate, confirm):
    action = (action or "").lower().strip()
    if action == "parse":
        if not ascii_tree:
            raise ValidationError("ascii_tree is required for parse")
        parsed = _parse_or_raise(ascii_tree)
        return {"items": [{"path": p, "kind": k} for p, k in parsed], "count": len(parsed)}
    if action == "preview":
        if not ascii_tree:
            raise ValidationError("ascii_tree is required for preview")
        _parse_or_raise(ascii_tree)
        files = preview_boilerplate(ascii_tree)
        return {"files": files, "count": len(files)}
    if action == "scan":
        if not path:
            raise ValidationError("path is required for scan")
        root = safe_path(path, must_exist=True)
        if not root.is_dir():
            raise ValidationError("scan path must be a directory")
        return {"tree": folder_to_ascii_tree(root), "root": str(root)}
    if action == "create":
        if not ascii_tree:
            raise ValidationError("ascii_tree is required for create")
        if not path:
            raise ValidationError("path is required for create")
        require_confirm(confirm, "create filesystem from ASCII tree")
        ensure_writable()
        dest = safe_path(path)
        dest.mkdir(parents=True, exist_ok=True)
        result = create_from_tree(ascii_tree, dest, inject_boilerplate=inject_boilerplate)
        result["parsed"] = [{"path": p, "kind": k} for p, k in result["parsed"]]
        return result
    raise ValidationError("action must be parse|preview|scan|create")


def _sdlc(action, query, project_name, audience, category, type_name, complexity, path, confirm, limit):
    action = (action or "").lower().strip()
    if action == "catalog":
        return catalog_summary()
    if action == "search":
        if not query:
            raise ValidationError("query is required for search")
        return {"hits": search_types(query, limit=max(1, min(int(limit or 20), 100)))}
    if action == "generate":
        if not project_name or not audience or not category or not type_name:
            raise ValidationError("generate needs project_name, audience, category, type_name")
        if complexity and complexity.upper() not in {"LOW", "MEDIUM", "HIGH"}:
            raise ValidationError("complexity must be LOW|MEDIUM|HIGH")
        bp = generate_blueprint(project_name, audience, category, type_name, complexity.upper() if complexity else None)
        return bp
    if action == "export":
        if not project_name or not audience or not category or not type_name:
            raise ValidationError("export needs project_name, audience, category, type_name")
        if not path:
            raise ValidationError("path is required for export")
        require_confirm(confirm, "export SDLC structure to disk")
        ensure_writable()
        dest = safe_path(path)
        dest.mkdir(parents=True, exist_ok=True)
        bp = generate_blueprint(project_name, audience, category, type_name, complexity.upper() if complexity else None)
        written = export_structure(dest, bp["structure"])
        return {"blueprint": {k: bp[k] for k in ("project_name", "complexity", "ascii_tree", "route_hint")}, "written": written}
    raise ValidationError("action must be catalog|search|generate|export")


def _gui_script(app: str) -> Path:
    root = Path(__file__).resolve().parents[2] / "apps"
    mapping = {
        "ascii_tree": root / "ascii_tree_creator.py",
        "ascii": root / "ascii_tree_creator.py",
        "sdlc": root / "sdlc_generator.py",
        "sdlc_generator": root / "sdlc_generator.py",
    }
    script = mapping.get(app.lower().strip())
    if not script:
        raise ValidationError("app must be ascii_tree or sdlc")
    if not script.exists():
        raise NotFoundError(f"GUI script missing: {script}")
    return script


def _launch_gui(app: str) -> dict[str, Any]:
    script = _gui_script(app)
    proc = subprocess.Popen(  # noqa: S603 — allowlisted local GUI scripts only
        [sys.executable, str(script)],
        cwd=str(script.parent),
        start_new_session=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    return {"app": app, "pid": proc.pid, "script": str(script), "note": "GUI launched in background; needs a display."}


def _language_catalog(action, query, name, tag, limit):
    action = (action or "").lower().strip()
    if action == "summary":
        return language_catalog.summary()
    if action == "categories":
        cats = language_catalog.categories()
        return {
            "count": len(cats),
            "categories": [{"name": c["name"], "count": c["count"], "languages": c["languages"]} for c in cats],
        }
    if action == "search":
        if not query:
            raise ValidationError("query is required for search")
        hits = language_catalog.search(query, limit=max(1, min(int(limit or 25), 100)))
        return {"query": query, "count": len(hits), "hits": hits}
    if action == "get":
        if not name:
            raise ValidationError("name is required for get")
        rec = language_catalog.get(name)
        if not rec:
            return {"found": False, "name": name, "hint": "Try action=search or action=categories."}
        return {"found": True, "language": rec}
    if action == "by_tag":
        if not tag:
            raise ValidationError("tag is required for by_tag")
        langs = language_catalog.tag_to_languages(tag)
        return {"tag": tag, "count": len(langs), "languages": langs}
    raise ValidationError("action must be summary|categories|search|get|by_tag")
