"""AndroidManifest.xml edits."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any
from xml.etree import ElementTree as ET

from android_mcp.errors import NotFoundError, ValidationError
from android_mcp.inspect import find_root, inspect_project

NS = "http://schemas.android.com/apk/res/android"
ET.register_namespace("android", NS)


def _manifest_path(project: Path) -> Path:
    root = find_root(project)
    report = inspect_project(root)
    p = report.get("manifest")
    if not p:
        raise NotFoundError("AndroidManifest.xml not found")
    return Path(p)


def modify_manifest(
    project: Path,
    *,
    add_permission: str | None = None,
    remove_permission: str | None = None,
    set_exported: dict[str, Any] | None = None,
    add_activity: str | None = None,
) -> dict[str, Any]:
    path = _manifest_path(project)
    text = path.read_text(encoding="utf-8")
    changed = []
    if add_permission:
        if add_permission not in text:
            perm = f'    <uses-permission android:name="{add_permission}" />\n'
            text = text.replace("<manifest", "<manifest", 1)
            text = re.sub(r"(<manifest[^>]*>)", r"\1\n" + perm, text, count=1)
            changed.append(f"added permission {add_permission}")
    if remove_permission:
        new, n = re.subn(
            rf'\s*<uses-permission android:name="{re.escape(remove_permission)}"\s*/>',
            "",
            text,
        )
        if n:
            text = new
            changed.append(f"removed permission {remove_permission}")
    if add_activity:
        snippet = f'''
        <activity android:name="{add_activity}" android:exported="false" />
'''
        if add_activity not in text:
            if "</application>" not in text:
                raise ValidationError("No <application> in manifest")
            text = text.replace("</application>", snippet + "    </application>", 1)
            changed.append(f"added activity {add_activity}")
    if set_exported:
        name = set_exported.get("name")
        exported = "true" if set_exported.get("exported") else "false"
        if not name:
            raise ValidationError("set_exported requires name")
        pattern = rf'(<activity[^>]*android:name="{re.escape(name)}"[^>]*)(android:exported="[^"]*")?'
        def repl(m: re.Match[str]) -> str:
            head = m.group(1)
            if "android:exported=" in head:
                return re.sub(r'android:exported="[^"]*"', f'android:exported="{exported}"', m.group(0))
            return head + f' android:exported="{exported}"'
        text2, n = re.subn(pattern, repl, text, count=1)
        if n:
            text = text2
            changed.append(f"set exported={exported} on {name}")
    path.write_text(text, encoding="utf-8")
    return {"path": str(path), "changes": changed}
