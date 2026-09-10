"""Format conversion including optional LibreOffice PDF."""

from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path
from typing import Any

from office_mcp.adapters import excel as excel_ad
from office_mcp.adapters import pptx_adapter as pptx_ad
from office_mcp.adapters import word as word_ad
from office_mcp.adapters.ooxml import detect_kind
from office_mcp.config import SETTINGS
from office_mcp.errors import DependencyMissing, TimeoutError_, UnsupportedError, ValidationError


def soffice_bin() -> str | None:
    for name in ("soffice", "libreoffice"):
        found = shutil.which(name)
        if found:
            return found
    return None


def convert(src: Path, dest: Path, to_format: str, **opts: Any) -> dict[str, Any]:
    to_format = to_format.lower().lstrip(".")
    kind = detect_kind(src)
    dest.parent.mkdir(parents=True, exist_ok=True)

    if to_format in {"md", "markdown"}:
        if kind not in {"docx", "docm"}:
            raise UnsupportedError("Markdown export currently supports DOCX")
        text = _docx_to_markdown(src)
        dest.write_text(text, encoding="utf-8")
        return {"path": str(dest), "format": "markdown"}

    if to_format in {"html", "htm"}:
        if kind not in {"docx", "docm"}:
            raise UnsupportedError("HTML export currently supports DOCX")
        html = _docx_to_html(src)
        dest.write_text(html, encoding="utf-8")
        return {"path": str(dest), "format": "html"}

    if to_format in {"txt", "text"}:
        dest.write_text(_to_text(src, kind), encoding="utf-8")
        return {"path": str(dest), "format": "txt"}

    if to_format == "csv":
        if kind not in {"xlsx", "xlsm"}:
            raise UnsupportedError("CSV export requires XLSX")
        excel_ad.to_csv(src, dest, sheet=opts.get("sheet"))
        return {"path": str(dest), "format": "csv"}

    if to_format == "json":
        dest.write_text(_to_json(src, kind), encoding="utf-8")
        return {"path": str(dest), "format": "json"}

    if to_format == "docx" and src.suffix.lower() in {".md", ".markdown", ".txt"}:
        word_ad.markdown_to_docx(src.read_text(encoding="utf-8"), dest, title=opts.get("title"))
        return {"path": str(dest), "format": "docx"}

    if to_format == "xlsx" and src.suffix.lower() in {".csv", ".tsv"}:
        excel_ad.from_csv(src, dest, sheet=opts.get("sheet") or "Sheet1")
        return {"path": str(dest), "format": "xlsx"}

    if to_format == "pdf":
        return _to_pdf(src, dest)

    raise UnsupportedError(
        f"Conversion {kind} → {to_format} is not supported without extra tooling",
        {"from": kind, "to": to_format},
    )


def _docx_to_html(src: Path) -> str:
    try:
        import mammoth
    except ImportError:
        return "<pre>" + word_ad.extract(src)["plain_text"] + "</pre>"
    with src.open("rb") as f:
        result = mammoth.convert_to_html(f)
    return result.value


def _docx_to_markdown(src: Path) -> str:
    try:
        import mammoth
    except ImportError:
        return word_ad.extract(src)["plain_text"]
    with src.open("rb") as f:
        result = mammoth.convert_to_markdown(f)
    return result.value


def _to_text(src: Path, kind: str) -> str:
    if kind in {"docx", "docm"}:
        return word_ad.extract(src)["plain_text"]
    if kind in {"xlsx", "xlsm"}:
        data = excel_ad.read_range(src)
        lines = []
        for row in data["values"]:
            lines.append("\t".join("" if c is None else str(c) for c in row))
        return "\n".join(lines)
    if kind in {"pptx", "pptm"}:
        return pptx_ad.extract(src)["plain_text"]
    return src.read_text(encoding="utf-8", errors="replace")


def _to_json(src: Path, kind: str) -> str:
    if kind in {"xlsx", "xlsm"}:
        data = excel_ad.read_range(src)
        return json.dumps(data, indent=2, default=str)
    if kind in {"docx", "docm"}:
        return json.dumps(word_ad.extract(src), indent=2, default=str)
    if kind in {"pptx", "pptm"}:
        return json.dumps(pptx_ad.extract(src), indent=2, default=str)
    raise UnsupportedError("JSON export not available for this type")


def _to_pdf(src: Path, dest: Path) -> dict[str, Any]:
    if not SETTINGS.allow_soffice:
        raise DependencyMissing("LibreOffice conversion is disabled (OFFICE_MCP_ALLOW_SOFFICE)")
    binary = soffice_bin()
    if not binary:
        raise DependencyMissing(
            "LibreOffice (soffice) is not installed. PDF conversion is optional.",
            {"install": "apt install libreoffice or brew install --cask libreoffice"},
        )
    outdir = dest.parent
    cmd = [
        binary,
        "--headless",
        "--nologo",
        "--nofirststartwizard",
        "--norestore",
        "--convert-to",
        "pdf",
        "--outdir",
        str(outdir),
        str(src),
    ]
    try:
        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=SETTINGS.conversion_timeout,
            check=False,
        )
    except subprocess.TimeoutExpired as exc:
        raise TimeoutError_("LibreOffice conversion timed out") from exc
    produced = outdir / (src.stem + ".pdf")
    if proc.returncode != 0 or not produced.exists():
        raise ValidationError(
            "LibreOffice failed to convert to PDF",
            {"stderr": (proc.stderr or "")[-2000:], "stdout": (proc.stdout or "")[-1000:]},
        )
    if produced != dest:
        produced.replace(dest)
    return {"path": str(dest), "format": "pdf", "adapter": "libreoffice"}
