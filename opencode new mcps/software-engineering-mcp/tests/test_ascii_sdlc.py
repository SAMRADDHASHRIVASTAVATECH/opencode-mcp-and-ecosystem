from pathlib import Path

from se_mcp.ascii_tree import create_from_tree, folder_to_ascii_tree, parse_ascii_tree
from se_mcp.lang_templates import build_interconnected_boilerplate
from se_mcp.sdlc import catalog_summary, export_structure, generate_blueprint, search_types
from se_mcp.sdlc_data import SDLC_PHASES
from se_mcp.tools import _ascii, _sdlc

TREE = """demo_app/
├── src/
│   ├── main.py
│   └── helpers.py
├── tests/
│   └── test_main.py
└── README.md
"""


def test_parse_nested_ascii_tree() -> None:
    parsed = parse_ascii_tree(TREE)
    kinds = dict(parsed)
    assert kinds["demo_app"] == "dir"
    assert kinds[str(Path("demo_app") / "src")] == "dir"
    assert kinds[str(Path("demo_app") / "src" / "main.py")] == "file"
    assert kinds[str(Path("demo_app") / "README.md")] == "file"


def test_parse_without_trailing_slash_on_dirs() -> None:
    parsed = dict(
        parse_ascii_tree(
            """root\n├── src\n│   └── a.py\n└── b.py\n"""
        )
    )
    assert parsed["root"] == "dir"
    assert parsed[str(Path("root") / "src")] == "dir"
    assert parsed[str(Path("root") / "src" / "a.py")] == "file"


def test_create_injects_python_boilerplate(tmp_path: Path) -> None:
    result = create_from_tree(TREE, tmp_path, inject_boilerplate=True)
    assert result["files_created"] >= 3
    main = (tmp_path / "demo_app" / "src" / "main.py").read_text(encoding="utf-8")
    assert "def main" in main
    assert "helpers" in main
    readme = (tmp_path / "demo_app" / "README.md").read_text(encoding="utf-8")
    assert "PLACEHOLDER" in readme


def test_scan_roundtrip(tmp_path: Path) -> None:
    create_from_tree(TREE, tmp_path)
    rendered = folder_to_ascii_tree(tmp_path / "demo_app")
    assert "main.py" in rendered
    assert "tests/" in rendered or "tests" in rendered


def test_go_main_uses_calls_not_mods() -> None:
    text = build_interconnected_boilerplate("cmd/app.go", ".go", ["cmd/app.go", "internal/util.go"])
    assert "func main" in text
    assert "util.Main()" in text


def test_sdlc_catalog_has_21_phases() -> None:
    cat = catalog_summary()
    assert cat["phase_count"] == 21
    assert len(SDLC_PHASES) == 21
    assert cat["category_count"] >= 15
    assert "Kids (Age 6-12)" in cat["audiences"]


def test_sdlc_search_and_generate() -> None:
    hits = search_types("android")
    assert hits
    assert any("Android" in h["type"] for h in hits)
    bp = generate_blueprint(
        "PayApp",
        "Startups",
        "Mobile Development",
        "Native Android App",
        None,
    )
    assert bp["complexity"] == "HIGH"
    assert bp["route_hint"] == "android-development-mcp"
    assert "PayApp" in bp["ascii_tree"]
    assert len(bp["phases"]) == 21


def test_sdlc_export_writes_dirs(tmp_path: Path) -> None:
    bp = generate_blueprint("Tiny", "Hobbyists & Makers", "Utilities & Tools", "Calculator", "LOW")
    written = export_structure(tmp_path, bp["structure"])
    assert written["dirs"] >= 1
    assert (tmp_path / "Tiny").is_dir()
    assert (tmp_path / "Tiny" / "README.md").exists()


def test_gui_scripts_exist() -> None:
    from se_mcp.tools import _gui_script

    assert _gui_script("ascii_tree").exists()
    assert _gui_script("sdlc").exists()


def test_tool_wrappers_parse_and_catalog(tmp_path: Path) -> None:
    parsed = _ascii("parse", TREE, None, True, False)
    assert parsed["count"] >= 5
    cat = _sdlc("catalog", None, None, None, None, None, None, None, False, 20)
    assert cat["phase_count"] == 21
    gen = _sdlc(
        "generate",
        None,
        "X",
        "Students (College/Uni)",
        "Web Development",
        "Static Website",
        None,
        None,
        False,
        20,
    )
    assert "ascii_tree" in gen
