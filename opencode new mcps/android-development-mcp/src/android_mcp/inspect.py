"""Inspect an existing Android Gradle project."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from android_mcp.errors import ValidationError


def find_root(path: Path) -> Path:
    p = path.resolve()
    if p.is_file():
        p = p.parent
    cur = p
    for _ in range(8):
        if (cur / "settings.gradle.kts").exists() or (cur / "settings.gradle").exists():
            return cur
        if cur.parent == cur:
            break
        cur = cur.parent
    if (p / "app").exists() or list(p.glob("**/AndroidManifest.xml")):
        return p
    raise ValidationError(f"Not an Android Gradle project: {path}")


def _read(p: Path) -> str:
    try:
        return p.read_text(encoding="utf-8")
    except OSError:
        return ""


def inspect_project(path: Path) -> dict[str, Any]:
    root = find_root(path)
    settings = _read(root / "settings.gradle.kts") or _read(root / "settings.gradle")
    modules = re.findall(r'include\(":?([^"]+)"\)', settings)
    if not modules:
        modules = re.findall(r"include\s+'?:?([^']+)'", settings)
    modules = [m.replace(":", "/") for m in modules] or _guess_modules(root)
    catalog = root / "gradle" / "libs.versions.toml"
    kts = (root / "build.gradle.kts").exists()
    app_mod = _pick_app_module(root, modules)
    app_gradle = _module_gradle(root, app_mod)
    gtxt = _read(app_gradle) if app_gradle else ""
    manifest = _find_manifest(root, app_mod)
    mtxt = _read(manifest) if manifest else ""
    compose = "compose = true" in gtxt or "compose true" in gtxt or "kotlin.compose" in gtxt
    views = "R.layout" in _concat_kt(root, app_mod) or (root / app_mod / "src/main/res/layout").exists() if app_mod else False
    report = {
        "root": str(root),
        "dsl": "kotlin" if kts else "groovy",
        "version_catalog": catalog.exists(),
        "modules": modules,
        "application_module": app_mod,
        "application_id": _first(gtxt, r'applicationId\s*=\s*"([^"]+)"', r'applicationId\s+"([^"]+)"'),
        "namespace": _first(gtxt, r'namespace\s*=\s*"([^"]+)"', r'namespace\s+"([^"]+)"'),
        "compile_sdk": _int(_first(gtxt, r"compileSdk\s*=\s*(\d+)", r"compileSdk(?:Version)?\s+(\d+)")),
        "min_sdk": _int(_first(gtxt, r"minSdk\s*=\s*(\d+)", r"minSdk(?:Version)?\s+(\d+)")),
        "target_sdk": _int(_first(gtxt, r"targetSdk\s*=\s*(\d+)", r"targetSdk(?:Version)?\s+(\d+)")),
        "compose": compose,
        "xml_views": bool(views),
        "has_ndk": "ndkVersion" in gtxt or "externalNativeBuild" in gtxt,
        "manifest": str(manifest) if manifest else None,
        "permissions": re.findall(r'android:name="([^"]+)"', "\n".join(re.findall(r"<uses-permission[^>]+>", mtxt))),
        "activities": re.findall(r'<activity[^>]*android:name="([^"]+)"', mtxt),
        "services": re.findall(r'<service[^>]*android:name="([^"]+)"', mtxt),
        "receivers": re.findall(r'<receiver[^>]*android:name="([^"]+)"', mtxt),
        "providers": re.findall(r'<provider[^>]*android:name="([^"]+)"', mtxt),
        "debuggable": 'android:debuggable="true"' in mtxt,
        "allow_backup": 'android:allowBackup="true"' in mtxt,
        "has_network_security_config": "networkSecurityConfig" in mtxt,
        "gradle_wrapper": (root / "gradle/wrapper/gradle-wrapper.properties").exists(),
        "wrapper_jar": (root / "gradle/wrapper/gradle-wrapper.jar").exists(),
        "local_properties": (root / "local.properties").exists(),
        "architecture_guess": _arch_guess(root, app_mod),
        "test_dirs": {
            "unit": any((root / m / "src/test").exists() for m in modules if (root / m).exists()),
            "android": any((root / m / "src/androidTest").exists() for m in modules if (root / m).exists()),
        },
        "catalog_versions": _catalog_versions(catalog) if catalog.exists() else {},
    }
    return report


def _guess_modules(root: Path) -> list[str]:
    out = []
    for child in root.iterdir():
        if child.is_dir() and (
            (child / "build.gradle.kts").exists() or (child / "build.gradle").exists()
        ):
            out.append(child.name)
    return out or ["app"]


def _pick_app_module(root: Path, modules: list[str]) -> str:
    for m in modules:
        g = _module_gradle(root, m)
        if g and "com.android.application" in _read(g):
            return m
    return modules[0] if modules else "app"


def _module_gradle(root: Path, module: str) -> Path | None:
    for name in ("build.gradle.kts", "build.gradle"):
        p = root / module / name
        if p.exists():
            return p
    return None


def _find_manifest(root: Path, module: str) -> Path | None:
    for rel in (
        f"{module}/src/main/AndroidManifest.xml",
        "app/src/main/AndroidManifest.xml",
        "src/main/AndroidManifest.xml",
    ):
        p = root / rel
        if p.exists():
            return p
    found = list(root.glob("**/src/main/AndroidManifest.xml"))
    return found[0] if found else None


def _concat_kt(root: Path, module: str) -> str:
    d = root / module / "src/main"
    if not d.exists():
        return ""
    parts = []
    for p in list(d.rglob("*.kt"))[:40] + list(d.rglob("*.java"))[:20]:
        parts.append(_read(p)[:4000])
    return "\n".join(parts)


def _arch_guess(root: Path, module: str) -> str:
    text = _concat_kt(root, module)
    if "UseCase" in text and "Repository" in text:
        return "clean"
    if "ViewModel" in text and "Repository" in text:
        return "mvvm"
    if "ViewModel" in text:
        return "mvvm-lite"
    return "unknown"


def _catalog_versions(path: Path) -> dict[str, str]:
    text = _read(path)
    in_versions = False
    out: dict[str, str] = {}
    for line in text.splitlines():
        if line.strip() == "[versions]":
            in_versions = True
            continue
        if line.startswith("[") and in_versions:
            break
        if in_versions:
            m = re.match(r'(\w+)\s*=\s*"([^"]+)"', line.strip())
            if m:
                out[m.group(1)] = m.group(2)
    return out


def _first(text: str, *pats: str) -> str | None:
    for p in pats:
        m = re.search(p, text)
        if m:
            return m.group(1)
    return None


def _int(v: str | None) -> int | None:
    try:
        return int(v) if v else None
    except ValueError:
        return None
