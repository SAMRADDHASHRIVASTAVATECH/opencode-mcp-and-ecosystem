# Office Documents MCP — Implementation Plan

## Build order

1. Security kernel (paths, limits, typed errors)
2. OOXML inspector (works even if high-level libs fail)
3. Word adapter + tools
4. Excel adapter + tools
5. PowerPoint adapter + tools
6. Conversion + batch
7. Analysis
8. Tests against real workflows
9. README

## Package layout

```
office-documents-mcp/
  src/office_mcp/
    __init__.py
    server.py
    errors.py
    security.py
    config.py
    results.py
    adapters/
    tools/
  tests/
  pyproject.toml
  README.md
```

## Tests (real workflows)

- Beginner: create a DOCX with title + two paragraphs; extract text
- Professional: workbook with 2 sheets, formulas, chart, analyze
- Advanced: markdown→docx, headers, table, find/replace
- Batch: convert three CSV files to xlsx
- Diagnostic: inspect a zip that is not OOXML
- Failure: path traversal rejected; read-only blocks write
- Recovery: extract document.xml text from a slightly odd package

## Success criteria

- Independently installable (`pip install -e .`)
- `python -m office_mcp` starts stdio MCP
- No Microsoft Office required for core path
- Structured errors for missing LibreOffice
- No silent pretend-capabilities
