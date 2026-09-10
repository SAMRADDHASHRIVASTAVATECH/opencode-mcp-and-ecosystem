"""Low-level OOXML package inspection (ZIP of XML parts)."""

from __future__ import annotations

import zipfile
from pathlib import Path
from typing import Any
from xml.etree import ElementTree as ET

try:
    from defusedxml import ElementTree as DefusedET
except ImportError:  # pragma: no cover
    DefusedET = ET  # type: ignore

from office_mcp.errors import MalformedError, ValidationError

CONTENT_TYPES = "[Content_Types].xml"
MACRO_HINTS = ("vbaProject.bin", "vbaData.xml")
ENC_HINTS = ("EncryptedPackage", "encryption.xml", "EncryptionInfo")

NS = {
    "ct": "http://schemas.openxmlformats.org/package/2006/content-types",
    "rel": "http://schemas.openxmlformats.org/package/2006/relationships",
    "cp": "http://schemas.openxmlformats.org/package/2006/metadata/core-properties",
    "dc": "http://purl.org/dc/elements/1.1/",
    "dcterms": "http://purl.org/dc/terms/",
    "ep": "http://schemas.openxmlformats.org/officeDocument/2006/extended-properties",
}


def is_ooxml(path: Path) -> bool:
    if not zipfile.is_zipfile(path):
        return False
    with zipfile.ZipFile(path) as zf:
        names = set(zf.namelist())
        return CONTENT_TYPES in names or any(
            n.startswith(("word/", "xl/", "ppt/")) for n in names
        )


def detect_kind(path: Path) -> str:
    suffix = path.suffix.lower()
    mapping = {
        ".docx": "docx",
        ".dotx": "docx",
        ".docm": "docm",
        ".xlsx": "xlsx",
        ".xlsm": "xlsm",
        ".xltx": "xlsx",
        ".pptx": "pptx",
        ".pptm": "pptm",
        ".potx": "pptx",
        ".csv": "csv",
        ".tsv": "tsv",
        ".json": "json",
        ".md": "markdown",
        ".html": "html",
        ".htm": "html",
        ".txt": "text",
        ".pdf": "pdf",
        ".doc": "doc-legacy",
        ".xls": "xls-legacy",
        ".ppt": "ppt-legacy",
    }
    if suffix in mapping:
        return mapping[suffix]
    if is_ooxml(path):
        with zipfile.ZipFile(path) as zf:
            names = zf.namelist()
            if any(n.startswith("word/") for n in names):
                return "docx"
            if any(n.startswith("xl/") for n in names):
                return "xlsx"
            if any(n.startswith("ppt/") for n in names):
                return "pptx"
        return "ooxml"
    return "unknown"


def inspect_package(path: Path, peek_part: str | None = None, peek_chars: int = 4000) -> dict[str, Any]:
    if not zipfile.is_zipfile(path):
        raise MalformedError("Not a ZIP/OOXML package", {"path": str(path)})
    with zipfile.ZipFile(path) as zf:
        names = zf.namelist()
        macros = [n for n in names if any(h in n for h in MACRO_HINTS)]
        encrypted = any(any(h in n for h in ENC_HINTS) for n in names)
        externals = _external_rels(zf)
        core = _core_props(zf)
        peek = None
        if peek_part:
            if peek_part not in names:
                raise ValidationError(f"Part not in package: {peek_part}")
            data = zf.read(peek_part)
            try:
                peek = data.decode("utf-8")[:peek_chars]
            except UnicodeDecodeError:
                peek = f"<binary {len(data)} bytes content_type unknown>"
        return {
            "path": str(path),
            "kind": detect_kind(path),
            "part_count": len(names),
            "parts": sorted(names)[:500],
            "has_macros": bool(macros),
            "macro_parts": macros,
            "encrypted_hints": encrypted,
            "external_relationships": externals[:50],
            "core_properties": core,
            "peek": peek,
        }


def _external_rels(zf: zipfile.ZipFile) -> list[dict[str, str]]:
    found: list[dict[str, str]] = []
    for name in zf.namelist():
        if not name.endswith(".rels"):
            continue
        try:
            root = DefusedET.fromstring(zf.read(name))
        except Exception:
            continue
        for rel in root.findall(".//{http://schemas.openxmlformats.org/package/2006/relationships}Relationship"):
            mode = rel.attrib.get("TargetMode", "Internal")
            if mode.lower() == "external":
                found.append(
                    {
                        "part": name,
                        "target": rel.attrib.get("Target", ""),
                        "type": rel.attrib.get("Type", ""),
                    }
                )
    return found


def _core_props(zf: zipfile.ZipFile) -> dict[str, str]:
    for candidate in ("docProps/core.xml", "docProps/app.xml"):
        if candidate not in zf.namelist():
            continue
    if "docProps/core.xml" not in zf.namelist():
        return {}
    try:
        root = DefusedET.fromstring(zf.read("docProps/core.xml"))
    except Exception:
        return {}
    out: dict[str, str] = {}
    for child in list(root):
        tag = child.tag.rsplit("}", 1)[-1]
        if child.text:
            out[tag] = child.text
    return out


def extract_part_text(path: Path, part: str) -> str:
    with zipfile.ZipFile(path) as zf:
        if part not in zf.namelist():
            raise ValidationError(f"Part not in package: {part}")
        data = zf.read(part)
        try:
            xml = DefusedET.fromstring(data)
        except Exception:
            return data.decode("utf-8", errors="replace")
        texts = [t for t in xml.itertext() if t and t.strip()]
        return "\n".join(texts)
