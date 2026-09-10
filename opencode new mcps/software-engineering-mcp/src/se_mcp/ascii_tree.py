"""Parse ASCII trees and materialize folders/files (from the Tree Creator app)."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from se_mcp.lang_templates import get_all_code_files, placeholder_for


def _strip_annotation(name: str) -> str:
    if "  ← " in name:
        name = name.split("  ← ", 1)[0]
    if " <- " in name:
        name = name.split(" <- ", 1)[0]
    return name.strip()


def _name_and_depth(line: str) -> tuple[int, str, bool]:
    """Return (depth, name, is_dir). Depth is one unit per tree level."""
    s = line.replace("\t", "    ")
    s = s.replace("│", " ").replace("|", " ")
    depth = 0
    while s.startswith("    "):
        depth += 1
        s = s[4:]
    s = s.lstrip(" ")
    for br in ("├── ", "└── ", "├──", "└──", "+-- ", "`-- ", "|-- ", "+--", "`--", "|--"):
        if s.startswith(br):
            s = s[len(br) :].lstrip()
            break
    name = _strip_annotation(s.strip())
    is_dir = name.endswith("/") or name.endswith("\\")
    name = name.strip("/\\ ").rstrip(":")
    return depth, name, is_dir


def parse_ascii_tree(ascii_text: str) -> list[tuple[str, str]]:
    lines = [ln.rstrip() for ln in ascii_text.strip().splitlines() if ln.strip() and not ln.strip().startswith("#")]
    if not lines:
        raise ValueError("Input tree is empty.")
    outputs: list[tuple[str, str]] = []
    stack: list[dict[str, Any]] = []

    _, root_name, _ = _name_and_depth(lines[0])
    if not root_name:
        raise ValueError("Root directory name not found")
    outputs.append((root_name, "dir"))
    stack.append({"depth": -1, "name": root_name})

    for i, line in enumerate(lines[1:], start=2):
        depth, name, is_dir = _name_and_depth(line)
        if not name:
            continue
        while len(stack) > 1 and depth <= stack[-1]["depth"]:
            stack.pop()
        if not stack:
            raise ValueError(f"Parsing error at line {i}: indent for '{name}' has no parent")
        parts = [item["name"] for item in stack] + [name]
        item_path = os.path.join(*parts)
        outputs.append((item_path, "dir" if is_dir else "file"))
        stack.append({"depth": depth, "name": name})
    as_dir = {p for p, t in outputs if t == "dir"}
    for p, _t in outputs:
        parent = os.path.dirname(p)
        while parent:
            as_dir.add(parent)
            parent = os.path.dirname(parent)
    return [(p, "dir" if p in as_dir else t) for p, t in outputs]


def folder_to_ascii_tree(root_path: str | Path) -> str:
    root_path = str(root_path)
    lines: list[str] = [os.path.basename(root_path.rstrip(os.sep)) + "/"]

    def rec(current: str, prefix: str) -> None:
        try:
            entries = sorted(
                os.listdir(current),
                key=lambda s: (not os.path.isdir(os.path.join(current, s)), s.lower()),
            )
        except PermissionError:
            lines.append(f"{prefix}└── [PERMISSION DENIED]")
            return
        except OSError as e:
            lines.append(f"{prefix}└── [OS ERROR: {e}]")
            return
        for i, name in enumerate(entries):
            last = i == len(entries) - 1
            conn = "└── " if last else "├── "
            full = os.path.join(current, name)
            is_dir = os.path.isdir(full)
            lines.append(f"{prefix}{conn}{name}{'/' if is_dir else ''}")
            if is_dir:
                rec(full, prefix + ("    " if last else "│   "))

    rec(root_path, "")
    return "\n".join(lines)


def create_from_tree(
    ascii_tree: str,
    target: Path,
    *,
    inject_boilerplate: bool = True,
    overwrite_empty_only: bool = True,
) -> dict[str, Any]:
    parsed = parse_ascii_tree(ascii_tree)
    codefiles = get_all_code_files(parsed)
    files_created = folders_created = skipped = 0
    errors: list[str] = []
    created_dirs: set[str] = set()
    target = Path(target)
    target.mkdir(parents=True, exist_ok=True)
    for path, typ in parsed:
        abspath = target / path
        try:
            if typ == "dir":
                if not abspath.exists():
                    abspath.mkdir(parents=True, exist_ok=True)
                    created_dirs.add(str(abspath))
                    folders_created += 1
                else:
                    abspath.mkdir(parents=True, exist_ok=True)
            else:
                abspath.parent.mkdir(parents=True, exist_ok=True)
                write_it = (not abspath.exists()) or (abspath.stat().st_size == 0) or not overwrite_empty_only
                if overwrite_empty_only and abspath.exists() and abspath.stat().st_size > 0:
                    skipped += 1
                    continue
                if write_it:
                    content = placeholder_for(path, inject_boilerplate, codefiles)
                    abspath.write_text(content, encoding="utf-8")
                    files_created += 1
        except Exception as e:
            errors.append(f"{path}: {e}")
    return {
        "parsed": parsed,
        "folders_created": folders_created,
        "files_created": files_created,
        "skipped_existing": skipped,
        "errors": errors,
        "target": str(target),
    }


def preview_boilerplate(ascii_tree: str) -> list[dict[str, str]]:
    parsed = parse_ascii_tree(ascii_tree)
    codefiles = get_all_code_files(parsed)
    out = []
    for path, typ in parsed:
        if typ != "file":
            continue
        out.append({"path": path, "content": placeholder_for(path, True, codefiles)})
    return out
