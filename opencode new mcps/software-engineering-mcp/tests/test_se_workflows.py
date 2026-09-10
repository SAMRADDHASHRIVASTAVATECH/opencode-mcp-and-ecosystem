from pathlib import Path

import pytest

from se_mcp.config import Settings
from se_mcp.analyze import diagnose
from se_mcp.language_catalog import categories, get, reset_cache, search, summary, tag_to_languages
from se_mcp.discover import discover
from se_mcp.ecosystem import route, snapshot
from se_mcp.env import detect
from se_mcp.errors import PolicyError
from se_mcp.scaffold import TEMPLATES, create_project
from se_mcp.security import safe_path
from se_mcp.toolchain import execute


@pytest.fixture
def sandbox(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    settings = Settings(root=tmp_path.resolve(), read_only=False, timeout=30, ecosystem_root=Path("/home/user").resolve())
    monkeypatch.setattr("se_mcp.security.SETTINGS", settings)
    monkeypatch.setattr("se_mcp.config.SETTINGS", settings)
    monkeypatch.setattr("se_mcp.ecosystem.SETTINGS", settings)
    monkeypatch.setattr("se_mcp.toolchain.SETTINGS", settings)
    return tmp_path


def test_detect_has_python_and_node() -> None:
    env = detect()
    assert env["can_python"]
    assert env["can_node"]
    assert env["can_java"]
    assert env["can_c"]
    assert env["can_go"] is False
    assert env["can_rust"] is False


def test_route_android_not_local_stack() -> None:
    r = route("Build an Android Jetpack Compose application and install the APK")
    assert r["specialist"]["id"] == "android-development"
    assert r["local_stack"] is None


def test_route_office_and_cli() -> None:
    assert route("create a Word document")["specialist"]["id"] == "office-documents"
    r = route("python command line tool to greet users")
    assert r["specialist"] is None
    assert r["local_stack"] == "python-cli"


def test_ecosystem_finds_specialists() -> None:
    snap = snapshot()
    ids = {s["id"] for s in snap["specialists"] if s["installed"]}
    assert "office-documents" in ids
    assert "android-development" in ids
    assert "database-sql" in ids
    assert "windows-system" in ids
    skill_ids = {s["id"] for s in snap["skills"]}
    assert "software-engineering" in skill_ids
    assert "mcp-routing" in skill_ids


def test_create_python_cli_build_test(sandbox: Path) -> None:
    dest = sandbox / "greet"
    create_project(dest, name="Greet", template="python-cli")
    info = discover(dest)
    assert info["kind"] == "python"
    built = execute(dest, "build")
    assert built["ok"] is True
    tested = execute(dest, "test")
    assert tested["ok"] is True


def test_create_many_stacks(sandbox: Path) -> None:
    for t in ("python-lib", "static-web", "java-cli", "c-cli", "node-cli", "go-cli", "rust-cli"):
        d = sandbox / t
        create_project(d, name="Demo", template=t)
        assert any(d.iterdir())
    assert "python-fastapi" in TEMPLATES
    html = (sandbox / "static-web" / "index.html").read_text()
    assert "<h1>" in html


def test_c_cli_make(sandbox: Path) -> None:
    dest = sandbox / "cproj"
    create_project(dest, name="Cproj", template="c-cli")
    r = execute(dest, "build")
    assert r["ok"] is True
    assert (dest / "bin" / "app").exists()


def test_android_project_not_built_here(sandbox: Path) -> None:
    dest = sandbox / "fake-android"
    dest.mkdir()
    (dest / "settings.gradle.kts").write_text('include(":app")\n')
    (dest / "AndroidManifest.xml").write_text("<manifest/>\n")
    with pytest.raises(Exception) as ei:
        execute(dest, "build")
    assert "android" in str(ei.value).lower() or "Android" in str(ei.value)


def test_diagnose_and_secrets(sandbox: Path) -> None:
    d = diagnose("ModuleNotFoundError: No module named 'foo'")
    assert d["primary"]["kind"] == "python"
    dest = sandbox / "lib"
    create_project(dest, name="Lib", template="python-lib")
    (dest / "src" / "lib" / "bad.py").write_text('api_key = "sk_live_abcdefghijk"\n', encoding="utf-8")
    from se_mcp.analyze import analyze

    a = analyze(dest)
    assert a["secrets"]


def test_sandbox(sandbox: Path) -> None:
    with pytest.raises(PolicyError):
        safe_path("/etc/passwd")


def test_skill_frontmatter() -> None:
    root = Path("/home/user/skills")
    skills = list(root.glob("*/SKILL.md"))
    assert len(skills) >= 12
    for p in skills:
        text = p.read_text(encoding="utf-8")
        assert text.startswith("---")
        assert "name:" in text.split("---")[1]
        assert "description:" in text.split("---")[1]


def test_language_catalog_loaded() -> None:
    reset_cache()
    s = summary()
    assert s["primary_categories"] >= 25
    assert s["languages_total"] >= 152
    cats = categories()
    assert len(cats) >= 25
    assert sum(c["count"] for c in cats) >= 130


def test_language_catalog_lookup_and_search() -> None:
    java = get("Java")
    assert java is not None
    assert java["name"] == "Java"
    assert java.get("categories")
    hits = search("android")
    assert any(h["name"].lower() == "java" for h in hits) or bool(hits)
    hits = search("python")
    assert hits


def test_language_catalog_tag_mapping() -> None:
    from se_mcp.language_catalog import _load

    tag = next(iter((_load().get("tag_mapping") or {}).keys()))
    assert tag_to_languages(tag)
