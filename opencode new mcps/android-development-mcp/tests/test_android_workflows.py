from pathlib import Path

import pytest

from android_mcp.config import Settings
from android_mcp.diagnostics import analyze_build_log, analyze_crash
from android_mcp.env import detect
from android_mcp.errors import PolicyError, ValidationError
from android_mcp.inspect import inspect_project
from android_mcp.manifest_edit import modify_manifest
from android_mcp.scaffold import create_project
from android_mcp.security import check_shell, safe_path
from android_mcp.security_audit import audit
from android_mcp.tools import _component, _deps, _plan, _res


@pytest.fixture
def sandbox(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    settings = Settings(
        root=tmp_path.resolve(),
        read_only=False,
        timeout=30,
        logcat_lines=50,
        allow_sdk_install=False,
        keystore_pass_env="ANDROID_MCP_KEYSTORE_PASS",
    )
    monkeypatch.setattr("android_mcp.security.SETTINGS", settings)
    monkeypatch.setattr("android_mcp.config.SETTINGS", settings)
    monkeypatch.setattr("android_mcp.tools.SETTINGS", settings)
    return tmp_path


def test_environment_detects_missing_sdk() -> None:
    env = detect()
    assert env["can_scaffold"] is True
    assert "missing" in env
    assert env["java"]["java"]  # java exists on this host
    # AGP 8 needs 17; this image has 11
    assert env["java"]["agp8_ok"] is False or env["java"]["major"] >= 17


def test_create_compose_and_inspect(sandbox: Path) -> None:
    dest = sandbox / "HelloCompose"
    result = create_project(
        dest,
        name="Hello Compose",
        application_id="com.example.hello",
        template="compose-app",
        architecture="mvvm",
    )
    assert (dest / "settings.gradle.kts").exists()
    assert (dest / "gradle/libs.versions.toml").exists()
    assert (dest / "app/src/main/java/com/example/hello/MainActivity.kt").exists()
    assert (dest / "app/src/main/java/com/example/hello/ui/HomeViewModel.kt").exists()
    report = inspect_project(dest)
    assert report["compose"] is True
    assert report["application_id"] == "com.example.hello"
    assert report["min_sdk"] == 26
    assert report["architecture_guess"] in {"mvvm", "clean"}
    assert "kotlin-compose" in (dest / "gradle/libs.versions.toml").read_text()
    assert result["files_written"] > 10


def test_create_views_and_multimodule(sandbox: Path) -> None:
    views = sandbox / "XmlApp"
    create_project(views, name="XmlApp", application_id="com.example.xmlapp", template="views-app", architecture="none")
    report = inspect_project(views)
    assert report["xml_views"] is True
    assert (views / "app/src/main/res/layout/activity_main.xml").exists()
    mm = sandbox / "ModApp"
    create_project(mm, name="ModApp", application_id="com.example.mod", template="multi-module")
    text = (mm / "settings.gradle.kts").read_text()
    assert ":core" in text and ":feature" in text


def test_component_manifest_resources_deps(sandbox: Path) -> None:
    dest = sandbox / "App"
    create_project(dest, name="App", application_id="com.example.app", template="compose-app")
    comp = _component(str(dest), "viewmodel", "Stats", None)
    assert Path(comp["files"][0]).exists()
    man = modify_manifest(dest, add_permission="android.permission.CAMERA")
    assert any("CAMERA" in c for c in man["changes"])
    xml = (dest / "app/src/main/AndroidManifest.xml").read_text()
    assert "CAMERA" in xml
    _res(str(dest), "welcome", "Hello", None)
    strings = (dest / "app/src/main/res/values/strings.xml").read_text()
    assert "welcome" in strings
    _deps(str(dest), "coil", "io.coil-kt", "coil", "2.7.0", "app")
    cat = (dest / "gradle/libs.versions.toml").read_text()
    assert "coil" in cat


def test_security_audit_flags_backup(sandbox: Path) -> None:
    dest = sandbox / "Sec"
    create_project(dest, name="Sec", application_id="com.example.sec")
    # plant a fake secret
    p = dest / "app/src/main/java/com/example/sec/Secrets.kt"
    p.write_text('package com.example.sec\nval api_key = "sk_live_1234567890abcd"\n', encoding="utf-8")
    result = audit(dest)
    ids = {f["id"] for f in result["findings"]}
    assert "secret" in ids
    assert result["high"] >= 1


def test_build_failure_and_crash_analysis() -> None:
    g = analyze_build_log("SDK location not found. Define location with sdk.dir")
    assert g["primary"]["code"] == "DEPENDENCY_MISSING"
    assert "android_detect_environment" in g["primary"]["next_tools"]
    c = analyze_crash(
        "FATAL EXCEPTION: main\nProcess: com.example.app\njava.lang.SecurityException: Permission Denial: reading"
    )
    assert c["fatal"] is True
    assert any("permission" in x.lower() for x in c["likely_causes"])


def test_plan_create_build(sandbox: Path) -> None:
    plan = _plan("create a compose app and build debug apk", None)
    tools = [s.get("tool") for s in plan["steps"]]
    assert "android_create_project" in tools
    assert "android_gradle" in tools


def test_sandbox_and_shell(sandbox: Path) -> None:
    with pytest.raises(PolicyError):
        safe_path("/etc/passwd")
    with pytest.raises(PolicyError):
        check_shell("rm -rf /data")
    with pytest.raises(PolicyError):
        check_shell("reboot")
    check_shell("dumpsys meminfo com.example.app")


def test_bad_package(sandbox: Path) -> None:
    with pytest.raises(ValidationError):
        create_project(sandbox / "x", name="X", application_id="invalid")
