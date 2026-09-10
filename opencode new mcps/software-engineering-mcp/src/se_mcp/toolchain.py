"""Build / test / run using detected project type — no user shell strings."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from se_mcp.config import SETTINGS
from se_mcp.discover import discover
from se_mcp.errors import DependencyMissing, ValidationError
from se_mcp.runner import run_cmd


def execute(root: Path, action: str) -> dict[str, Any]:
    info = discover(root)
    if info.get("android") and action in {"build", "test"}:
        raise DependencyMissing(
            "This looks like an Android Gradle project. Use android_gradle / android_run_tests on the Android MCP — do not duplicate that toolchain here.",
            {"route": "android-development-mcp"},
        )
    cmd = None
    if action == "build":
        cmd = info.get("build")
        if info["kind"] == "python":
            # install extras not required; compile check
            cmd = ["python3", "-m", "compileall", "-q", str(root)]
        if info["kind"] == "node" and not (root / "package.json").exists():
            cmd = None
        if info["kind"] == "static-web":
            return {"ok": True, "note": "Static site has no compile step", "kind": info["kind"]}
        if info["kind"] == "native-c":
            cmd = ["make"]
        if info["kind"] == "java-cli" or (root / "Makefile").exists() and info["kind"] in {"unknown", "native-c"}:
            if (root / "Makefile").exists():
                cmd = ["make"]
    elif action == "test":
        cmd = info.get("test")
        if info["kind"] == "python":
            cmd = ["python3", "-m", "pytest", "-q"]
        if info["kind"] == "node":
            cmd = ["npm", "test", "--silent"]
        if info["kind"] == "native-c" or (root / "Makefile").exists():
            # make test may not exist; compile as smoke
            cmd = ["make"]
    elif action == "run":
        cmd = _run(root, info)
    else:
        raise ValidationError("action must be build|test|run")
    if not cmd:
        raise DependencyMissing(f"No {action} command for kind={info['kind']}", info)
    result = run_cmd(cmd, cwd=str(root), timeout=SETTINGS.timeout)
    result["kind"] = info["kind"]
    result["action"] = action
    if not result["ok"]:
        from se_mcp.analyze import diagnose

        result["analysis"] = diagnose((result["stderr"] or "") + "\n" + (result["stdout"] or ""))
    return result


def _run(root: Path, info: dict[str, Any]) -> list[str] | None:
    if info["kind"] == "python":
        # find cli module
        for p in root.glob("src/*/cli.py"):
            mod = p.parent.name
            return ["python3", "-m", f"{mod}.cli"]
        for p in root.glob("src/*/app.py"):
            return ["python3", "-c", f"print('app module {p}')"]
        for p in root.glob("src/*/main.py"):
            return ["python3", str(p)]
    if info["kind"] == "node":
        return ["npm", "start"]
    if (root / "Makefile").exists():
        return ["make", "run"]
    if info["kind"] == "go":
        return ["go", "run", "."]
    if info["kind"] == "rust":
        return ["cargo", "run"]
    return None
