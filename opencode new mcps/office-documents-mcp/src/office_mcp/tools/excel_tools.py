"""Excel-specific tools."""

from __future__ import annotations

from typing import Any

from office_mcp.adapters import excel as excel_ad
from office_mcp.adapters.conversion import soffice_bin
from office_mcp.config import SETTINGS
from office_mcp.errors import DependencyMissing
from office_mcp.security import check_size, ensure_writable, inspect_zip_bomb, safe_path
from office_mcp.tools._wrap import run


def register(mcp: Any) -> None:
    @mcp.tool()
    def excel_read(
        path: str,
        sheet: str | None = None,
        range_addr: str | None = None,
        include_formulas: bool = True,
        data_only: bool = False,
    ) -> dict[str, Any]:
        """Read values (and formulas) from a worksheet range. Omit range_addr to read the used range."""
        return run(
            _read,
            path=path,
            sheet=sheet,
            range_addr=range_addr,
            include_formulas=include_formulas,
            data_only=data_only,
        )

    @mcp.tool()
    def excel_write(
        path: str,
        sheet: str | None = None,
        cells: list[dict[str, Any]] | None = None,
        start: str | None = None,
        values: list[list[Any]] | None = None,
    ) -> dict[str, Any]:
        """Write cells. Provide either cells=[{cell,value},...] or a 2D values grid starting at start (A1)."""
        return run(_write, path=path, sheet=sheet, cells=cells, start=start, values=values)

    @mcp.tool()
    def excel_sheets(
        path: str,
        action: str = "list",
        name: str | None = None,
        new_name: str | None = None,
        index: int | None = None,
    ) -> dict[str, Any]:
        """Manage worksheets: action=list|add|delete|rename|activate."""
        return run(_sheets, path=path, action=action, name=name, new_name=new_name, index=index)

    @mcp.tool()
    def excel_format(
        path: str,
        range_addr: str,
        sheet: str | None = None,
        bold: bool | None = None,
        italic: bool | None = None,
        size: float | None = None,
        name: str | None = None,
        color: str | None = None,
        fill: str | None = None,
        number_format: str | None = None,
        align: str | None = None,
        wrap: bool | None = None,
        border: bool | None = None,
        column_width: float | None = None,
        color_scale: bool | None = None,
        validation: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Apply fonts, fills, number formats, borders, column width, color scales, or data validation."""
        spec = {
            "bold": bold,
            "italic": italic,
            "size": size,
            "name": name,
            "color": color,
            "fill": fill,
            "number_format": number_format,
            "align": align,
            "wrap": wrap,
            "border": border,
            "column_width": column_width,
            "color_scale": color_scale,
            "validation": validation,
        }
        return run(_format, path=path, sheet=sheet, range_addr=range_addr, spec=spec)

    @mcp.tool()
    def excel_structure(
        path: str,
        sheet: str | None = None,
        merge: str | None = None,
        unmerge: str | None = None,
        freeze: str | None = None,
        auto_filter: Any = None,
        table: dict[str, Any] | None = None,
        defined_name: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Merge cells, freeze panes, auto-filter, create Excel tables, or defined names."""
        spec = {
            "merge": merge,
            "unmerge": unmerge,
            "freeze": freeze,
            "auto_filter": auto_filter,
            "table": table,
            "defined_name": defined_name,
        }
        return run(_structure, path=path, sheet=sheet, spec=spec)

    @mcp.tool()
    def excel_charts(
        path: str,
        data: str,
        sheet: str | None = None,
        type: str = "bar",
        categories: str | None = None,
        title: str | None = None,
        anchor: str = "E2",
        titles_from_data: bool = True,
    ) -> dict[str, Any]:
        """Add a bar, line, pie, or scatter chart using data and optional category ranges."""
        spec = {
            "data": data,
            "type": type,
            "categories": categories,
            "title": title,
            "anchor": anchor,
            "titles_from_data": titles_from_data,
        }
        return run(_chart, path=path, sheet=sheet, spec=spec)

    @mcp.tool()
    def excel_analyze(path: str, sheet: str | None = None) -> dict[str, Any]:
        """Profile a sheet: dtypes, nulls, uniques, numeric stats, duplicate rows."""
        return run(_analyze, path=path, sheet=sheet)

    @mcp.tool()
    def excel_recalculate(path: str) -> dict[str, Any]:
        """Recalculate formulas via LibreOffice if installed. Otherwise reports DEPENDENCY_MISSING.

        openpyxl cannot run the Excel calculation engine. This tool never pretends values were calculated.
        """
        return run(_recalc, path=path)


def _read(path: str, sheet: str | None, range_addr: str | None, include_formulas: bool, data_only: bool) -> dict[str, Any]:
    p = safe_path(path, must_exist=True)
    check_size(p)
    inspect_zip_bomb(p)
    return excel_ad.read_range(
        p, sheet=sheet, range_addr=range_addr, include_formulas=include_formulas, data_only=data_only
    )


def _write(path: str, sheet: str | None, cells: list | None, start: str | None, values: list | None) -> dict[str, Any]:
    ensure_writable()
    p = safe_path(path, must_exist=True)
    return excel_ad.write_cells(p, sheet=sheet, cells=cells, start=start, values=values)


def _sheets(path: str, action: str, name: str | None, new_name: str | None, index: int | None) -> dict[str, Any]:
    if action != "list":
        ensure_writable()
    p = safe_path(path, must_exist=True)
    return excel_ad.manage_sheets(p, action, name=name, new_name=new_name, index=index)


def _format(path: str, sheet: str | None, range_addr: str, spec: dict[str, Any]) -> dict[str, Any]:
    ensure_writable()
    p = safe_path(path, must_exist=True)
    cleaned = {k: v for k, v in spec.items() if v is not None}
    return excel_ad.format_range(p, sheet, range_addr, cleaned)


def _structure(path: str, sheet: str | None, spec: dict[str, Any]) -> dict[str, Any]:
    ensure_writable()
    p = safe_path(path, must_exist=True)
    cleaned = {k: v for k, v in spec.items() if v is not None}
    return excel_ad.structure(p, sheet, cleaned)


def _chart(path: str, sheet: str | None, spec: dict[str, Any]) -> dict[str, Any]:
    ensure_writable()
    p = safe_path(path, must_exist=True)
    return excel_ad.add_chart(p, sheet, spec)


def _analyze(path: str, sheet: str | None) -> dict[str, Any]:
    p = safe_path(path, must_exist=True)
    check_size(p)
    return excel_ad.analyze(p, sheet=sheet)


def _recalc(path: str) -> dict[str, Any]:
    p = safe_path(path, must_exist=True)
    if not SETTINGS.allow_soffice or not soffice_bin():
        raise DependencyMissing(
            "Formula recalculation needs LibreOffice (soffice). "
            "openpyxl stores formulas but does not calculate them. Cached values remain until Excel/LibreOffice opens the file.",
            {"path": str(p)},
        )
    from office_mcp.adapters.conversion import convert

    ensure_writable()
    # Round-trip through LibreOffice to xlsx to force calc, saved next to original
    tmp = p.with_name(p.stem + ".recalc.xlsx")
    convert(p, tmp, "xlsx")
    return {"path": str(tmp), "note": "LibreOffice export used; open to confirm cached values."}
