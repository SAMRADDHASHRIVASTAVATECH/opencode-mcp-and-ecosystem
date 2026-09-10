"""Format-agnostic Office tools."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from office_mcp.adapters import excel as excel_ad
from office_mcp.adapters import pptx_adapter as pptx_ad
from office_mcp.adapters import word as word_ad
from office_mcp.adapters.conversion import convert
from office_mcp.adapters.ooxml import detect_kind, extract_part_text, inspect_package, is_ooxml
from office_mcp.config import SETTINGS
from office_mcp.errors import UnsupportedError, ValidationError
from office_mcp.security import (
    check_overwrite,
    check_size,
    ensure_writable,
    inspect_zip_bomb,
    safe_path,
)
from office_mcp.tools._wrap import run


def register(mcp: Any) -> None:
    @mcp.tool()
    def office_inspect(path: str, peek_part: str | None = None) -> dict[str, Any]:
        """Inspect an Office file: format, OOXML parts, macros, encryption hints, metadata.

        Args:
            path: Path to the document under the sandbox root.
            peek_part: Optional ZIP part name to preview (e.g. word/document.xml).
        """
        return run(_inspect, path=path, peek_part=peek_part)

    @mcp.tool()
    def office_create(
        path: str,
        kind: str,
        title: str | None = None,
        overwrite: bool = False,
        sheets: list[str] | None = None,
    ) -> dict[str, Any]:
        """Create a new blank DOCX, XLSX, or PPTX file.

        Args:
            path: Destination path.
            kind: docx, xlsx, or pptx.
            title: Optional document title.
            overwrite: Replace an existing file.
            sheets: Optional sheet names when kind=xlsx.
        """
        return run(_create, path=path, kind=kind, title=title, overwrite=overwrite, sheets=sheets)

    @mcp.tool()
    def office_metadata(path: str, set_props: dict[str, Any] | None = None) -> dict[str, Any]:
        """Get or set core document properties (title, author, subject, keywords).

        Args:
            path: Document path.
            set_props: If provided, properties to write. Omit to only read.
        """
        return run(_metadata, path=path, set_props=set_props)

    @mcp.tool()
    def office_convert(
        path: str,
        to_format: str,
        dest: str | None = None,
        overwrite: bool = False,
        sheet: str | None = None,
    ) -> dict[str, Any]:
        """Convert between Office and interchange formats (md, html, txt, csv, json, pdf, docx, xlsx).

        PDF requires LibreOffice. Missing converter returns DEPENDENCY_MISSING rather than faking output.

        Args:
            path: Source file.
            to_format: Target format.
            dest: Optional destination path.
            overwrite: Replace dest if it exists.
            sheet: Sheet name for CSV export.
        """
        return run(
            _convert,
            path=path,
            to_format=to_format,
            dest=dest,
            overwrite=overwrite,
            sheet=sheet,
        )

    @mcp.tool()
    def office_validate(path: str) -> dict[str, Any]:
        """Validate that a file is a well-formed OOXML package with expected parts."""
        return run(_validate, path=path)

    @mcp.tool()
    def office_ooxml_inspect(path: str, peek_part: str | None = None, extract_part: str | None = None) -> dict[str, Any]:
        """Low-level OOXML package forensics: parts, external relationships, XML text extract.

        Args:
            path: OOXML file.
            peek_part: Part to preview as text.
            extract_part: Part whose inner text nodes should be concatenated.
        """
        return run(_ooxml, path=path, peek_part=peek_part, extract_part=extract_part)

    @mcp.tool()
    def office_compare(path_a: str, path_b: str) -> dict[str, Any]:
        """Compare two documents by extracted plain text and high-level structure."""
        return run(_compare, path_a=path_a, path_b=path_b)

    @mcp.tool()
    def office_batch(
        folder: str,
        action: str,
        pattern: str = "*",
        to_format: str | None = None,
        recursive: bool = False,
    ) -> dict[str, Any]:
        """Batch inspect or convert files in a folder.

        Args:
            folder: Directory under the sandbox.
            action: inspect or convert.
            pattern: Glob, e.g. *.docx.
            to_format: Required when action=convert.
            recursive: Recurse into subfolders.
        """
        return run(
            _batch,
            folder=folder,
            action=action,
            pattern=pattern,
            to_format=to_format,
            recursive=recursive,
        )


def _inspect(path: str, peek_part: str | None) -> dict[str, Any]:
    p = safe_path(path, must_exist=True)
    check_size(p)
    kind = detect_kind(p)
    extra: dict[str, Any] = {"path": str(p), "kind": kind, "size": p.stat().st_size}
    if is_ooxml(p):
        inspect_zip_bomb(p)
        extra.update(inspect_package(p, peek_part=peek_part))
        extra.pop("parts")
        extra["part_sample"] = inspect_package(p)["parts"][:40]
    return extra


def _create(path: str, kind: str, title: str | None, overwrite: bool, sheets: list[str] | None) -> dict[str, Any]:
    ensure_writable()
    dest = safe_path(path)
    check_overwrite(dest, overwrite)
    dest.parent.mkdir(parents=True, exist_ok=True)
    kind = kind.lower().lstrip(".")
    if kind == "docx":
        word_ad.create_document(dest, title=title)
    elif kind == "xlsx":
        excel_ad.create_workbook(dest, sheets=sheets, title=title)
    elif kind == "pptx":
        pptx_ad.create(dest, title=title)
    else:
        raise ValidationError("kind must be docx, xlsx, or pptx")
    return {"path": str(dest), "kind": kind}


def _metadata(path: str, set_props: dict[str, Any] | None) -> dict[str, Any]:
    p = safe_path(path, must_exist=True)
    kind = detect_kind(p)
    if set_props:
        ensure_writable()
        if kind in {"docx", "docm"}:
            return word_ad.set_core_props(p, set_props)
        if kind in {"xlsx", "xlsm"}:
            return excel_ad.set_props(p, set_props)
        if kind in {"pptx", "pptm"}:
            return pptx_ad.set_props(p, set_props)
        raise UnsupportedError(f"Metadata write not supported for {kind}")
    if kind in {"docx", "docm"}:
        return word_ad.get_core_props(p)
    if kind in {"xlsx", "xlsm"}:
        return excel_ad.get_props(p)
    if kind in {"pptx", "pptm"}:
        return pptx_ad.get_props(p)
    raise UnsupportedError(f"Metadata not supported for {kind}")


def _convert(path: str, to_format: str, dest: str | None, overwrite: bool, sheet: str | None) -> dict[str, Any]:
    ensure_writable()
    src = safe_path(path, must_exist=True)
    check_size(src)
    if dest:
        out = safe_path(dest)
    else:
        out = src.with_suffix("." + to_format.lstrip(".").replace("markdown", "md"))
    check_overwrite(out, overwrite or (out == src))
    if is_ooxml(src):
        inspect_zip_bomb(src)
    return convert(src, out, to_format, sheet=sheet)


def _validate(path: str) -> dict[str, Any]:
    p = safe_path(path, must_exist=True)
    issues: list[str] = []
    kind = detect_kind(p)
    if kind.endswith("legacy"):
        issues.append("Legacy OLE binary format is not fully supported")
        return {"valid": False, "kind": kind, "issues": issues}
    if not is_ooxml(p):
        return {"valid": False, "kind": kind, "issues": ["Not an OOXML ZIP package"]}
    inspect_zip_bomb(p)
    pkg = inspect_package(p)
    required = {
        "docx": ["word/document.xml"],
        "docm": ["word/document.xml"],
        "xlsx": ["xl/workbook.xml"],
        "xlsm": ["xl/workbook.xml"],
        "pptx": ["ppt/presentation.xml"],
        "pptm": ["ppt/presentation.xml"],
    }
    for part in required.get(kind, []):
        if part not in pkg["parts"]:
            issues.append(f"Missing required part {part}")
    if pkg["encrypted_hints"]:
        issues.append("Package looks password-encrypted")
    return {
        "valid": not issues,
        "kind": kind,
        "issues": issues,
        "has_macros": pkg["has_macros"],
        "external_relationships": pkg["external_relationships"],
    }


def _ooxml(path: str, peek_part: str | None, extract_part: str | None) -> dict[str, Any]:
    p = safe_path(path, must_exist=True)
    inspect_zip_bomb(p)
    data = inspect_package(p, peek_part=peek_part)
    if extract_part:
        data["extracted_text"] = extract_part_text(p, extract_part)[: SETTINGS.max_text]
    return data


def _plain(path: Path) -> str:
    kind = detect_kind(path)
    if kind in {"docx", "docm"}:
        return word_ad.extract(path)["plain_text"]
    if kind in {"xlsx", "xlsm"}:
        rows = excel_ad.read_range(path)["values"]
        return "\n".join("\t".join("" if c is None else str(c) for c in row) for row in rows)
    if kind in {"pptx", "pptm"}:
        return pptx_ad.extract(path)["plain_text"]
    return path.read_text(encoding="utf-8", errors="replace")


def _compare(path_a: str, path_b: str) -> dict[str, Any]:
    a = safe_path(path_a, must_exist=True)
    b = safe_path(path_b, must_exist=True)
    ta, tb = _plain(a), _plain(b)
    la, lb = ta.splitlines(), tb.splitlines()
    only_a = [ln for ln in la if ln not in lb][:80]
    only_b = [ln for ln in lb if ln not in la][:80]
    return {
        "kind_a": detect_kind(a),
        "kind_b": detect_kind(b),
        "equal_text": ta == tb,
        "len_a": len(ta),
        "len_b": len(tb),
        "lines_only_in_a": only_a,
        "lines_only_in_b": only_b,
    }


def _batch(folder: str, action: str, pattern: str, to_format: str | None, recursive: bool) -> dict[str, Any]:
    d = safe_path(folder, must_exist=True)
    if not d.is_dir():
        raise ValidationError("folder must be a directory")
    globber = d.rglob if recursive else d.glob
    files = [p for p in globber(pattern) if p.is_file()][: SETTINGS.max_batch]
    results = []
    for f in files:
        rel = str(f)
        try:
            if action == "inspect":
                results.append({"path": rel, "kind": detect_kind(f), "size": f.stat().st_size})
            elif action == "convert":
                if not to_format:
                    raise ValidationError("to_format required for convert")
                ensure_writable()
                dest = f.with_suffix("." + to_format.lstrip("."))
                convert(f, dest, to_format)
                results.append({"path": rel, "dest": str(dest), "ok": True})
            else:
                raise ValidationError("action must be inspect or convert")
        except Exception as exc:
            results.append({"path": rel, "ok": False, "error": str(exc)})
    return {"count": len(results), "results": results}


# keep json import used if we later pretty-print
_ = json
