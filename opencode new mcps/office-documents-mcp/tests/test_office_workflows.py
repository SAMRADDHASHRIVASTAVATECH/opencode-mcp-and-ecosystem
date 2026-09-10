from pathlib import Path

import pytest

from office_mcp.adapters import excel as excel_ad
from office_mcp.adapters import pptx_adapter as pptx_ad
from office_mcp.adapters import word as word_ad
from office_mcp.adapters.conversion import convert
from office_mcp.adapters.ooxml import detect_kind, inspect_package
from office_mcp.config import Settings
from office_mcp.errors import SecurityError
from office_mcp.security import safe_path
from office_mcp.tools import excel_tools, office_tools, pptx_tools, word_tools


@pytest.fixture
def sandbox(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    settings = Settings(
        root=tmp_path.resolve(),
        read_only=False,
        max_bytes=20_000_000,
        max_cells=50_000,
        max_batch=20,
        max_text=50_000,
        allow_soffice=False,
        conversion_timeout=5,
    )
    monkeypatch.setattr("office_mcp.security.SETTINGS", settings)
    monkeypatch.setattr("office_mcp.config.SETTINGS", settings)
    monkeypatch.setattr("office_mcp.adapters.excel.SETTINGS", settings)
    return tmp_path


def test_beginner_word(sandbox: Path) -> None:
    path = sandbox / "hello.docx"
    word_ad.create_document(path, title="Hello")
    word_ad.apply_ops(
        path,
        [
            {"op": "add_paragraph", "text": "This is a test document."},
            {"op": "add_list", "items": ["one", "two"]},
        ],
    )
    data = word_ad.extract(path)
    assert "Hello" in data["plain_text"]
    assert "test document" in data["plain_text"]
    assert detect_kind(path) == "docx"


def test_professional_excel(sandbox: Path) -> None:
    path = sandbox / "sales.xlsx"
    excel_ad.create_workbook(path, sheets=["Sales", "Summary"], title="Sales")
    excel_ad.write_cells(
        path,
        "Sales",
        start="A1",
        values=[["Item", "Qty", "Price"], ["Apples", 3, 1.2], ["Oranges", 5, 0.8], ["Total", "=B2+B3", "=C2*B2"]],
    )
    excel_ad.format_range(path, "Sales", "A1:C1", {"bold": True, "fill": "4472C4", "color": "FFFFFF"})
    excel_ad.add_chart(path, "Sales", {"type": "bar", "data": "B1:B3", "categories": "A2:A3", "title": "Qty"})
    profile = excel_ad.analyze(path, sheet="Sales")
    assert profile["rows"] >= 3
    read = excel_ad.read_range(path, "Sales", "A1:C4")
    assert read["values"][0][0] == "Item"
    assert read["formulas"][3][1] == "=B2+B3"


def test_advanced_markdown_and_replace(sandbox: Path) -> None:
    md = "# Report\n\nHello **world**.\n\n- a\n- b\n\n| H1 | H2 |\n| --- | --- |\n| 1 | 2 |\n"
    path = sandbox / "report.docx"
    word_ad.markdown_to_docx(md, path, title="Report")
    word_ad.layout(path, {"header": "Confidential", "footer": "Page"})
    word_ad.find_replace(path, "world", "team")
    text = word_ad.extract(path)["plain_text"]
    assert "team" in text
    assert "Confidential" in word_ad.extract(path)["headers"][0]["text"]


def test_pptx_workflow(sandbox: Path) -> None:
    path = sandbox / "deck.pptx"
    pptx_ad.create(path, title="Q3")
    pptx_ad.apply_ops(
        path,
        [
            {"op": "add_slide", "layout": 1, "title": "Results", "body": "Revenue up\nCosts down"},
            {"op": "set_notes", "slide": 2, "text": "Speak slowly"},
        ],
    )
    data = pptx_ad.extract(path)
    assert data["slide_count"] >= 2
    assert "Results" in data["plain_text"]


def test_batch_csv_to_xlsx(sandbox: Path) -> None:
    for i in range(3):
        (sandbox / f"t{i}.csv").write_text("a,b\n1,2\n", encoding="utf-8")
    from office_mcp.tools.office_tools import _batch

    result = _batch(str(sandbox), "convert", "*.csv", "xlsx", False)
    assert result["count"] == 3
    assert (sandbox / "t0.xlsx").exists()


def test_diagnostic_not_ooxml(sandbox: Path) -> None:
    p = sandbox / "nope.txt"
    p.write_text("hello")
    assert detect_kind(p) == "text"
    from office_mcp.tools.office_tools import _validate

    v = _validate(str(p))
    assert v["valid"] is False


def test_path_traversal_rejected(sandbox: Path) -> None:
    with pytest.raises(SecurityError):
        safe_path("/etc/passwd")


def test_ooxml_inspect(sandbox: Path) -> None:
    path = sandbox / "x.docx"
    word_ad.create_document(path, title="X")
    pkg = inspect_package(path)
    assert pkg["has_macros"] is False
    assert any(n.endswith("document.xml") for n in pkg["parts"])


def test_tool_wrappers(sandbox: Path) -> None:
    path = sandbox / "w.docx"
    r = office_tools._create(str(path), "docx", "T", True, None)
    assert Path(r["path"]).exists()
    word_tools._edit(str(path), [{"op": "add_heading", "text": "H", "level": 1}])
    extracted = word_tools._extract(str(path), True, True)
    assert extracted["paragraph_count"] >= 1
    x = sandbox / "e.xlsx"
    office_tools._create(str(x), "xlsx", None, True, ["Data"])
    excel_tools._write(str(x), "Data", None, "A1", [["A", "B"], [1, 2]])
    excel_tools._analyze(str(x), "Data")
    deck = sandbox / "p.pptx"
    office_tools._create(str(deck), "pptx", "Deck", True, None)
    pptx_tools._extract(str(deck))


def test_md_convert(sandbox: Path) -> None:
    src = sandbox / "n.md"
    src.write_text("# Hi\n\nPara", encoding="utf-8")
    dest = sandbox / "n.docx"
    convert(src, dest, "docx")
    assert dest.exists()
    assert "Hi" in word_ad.extract(dest)["plain_text"]
