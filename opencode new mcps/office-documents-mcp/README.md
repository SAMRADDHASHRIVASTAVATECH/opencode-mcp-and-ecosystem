# Office Documents MCP

Standalone Model Context Protocol server for **DOCX, XLSX, and PPTX**. It does not require Microsoft Office.

This server was designed after researching OOXML, python-docx / openpyxl / python-pptx, existing Office MCPs, LibreOffice conversion, and the security properties of ZIP+XML packages. See:

- `research-report.md`
- `capability-matrix.md`
- `technology-evaluation.md`
- `architecture.md`
- `security-model.md`

## Why these libraries

| Format | Library | Why |
|--------|---------|-----|
| Word | python-docx | Only mature cross-platform read/write Python API |
| Excel | openpyxl | Read/write + styles, charts, tables, validation |
| PowerPoint | python-pptx | Only mature cross-platform read/write Python API |
| DOCX→HTML/MD | mammoth | Semantic extract |
| Analysis | pandas | Spreadsheet profiling |
| PDF | LibreOffice (optional) | Highest OSS fidelity; never faked if missing |

Macros are **detected, never executed**. Formulas are stored; they are **not** calculated unless LibreOffice is available.

## Install

```bash
pip install -e ./office-documents-mcp
```

## Run

```bash
python -m office_mcp
```

Claude Desktop / MCP client:

```json
{
  "mcpServers": {
    "office-documents": {
      "command": "python",
      "args": ["-m", "office_mcp"],
      "env": {
        "OFFICE_MCP_ROOT": "/path/you/allow"
      }
    }
  }
}
```

## Environment

| Variable | Default | Meaning |
|----------|---------|---------|
| `OFFICE_MCP_ROOT` | cwd | Sandbox root for all file I/O |
| `OFFICE_MCP_READ_ONLY` | false | Block writes |
| `OFFICE_MCP_MAX_BYTES` | 50MiB | Max file size |
| `OFFICE_MCP_MAX_CELLS` | 200000 | Max cells per read |
| `OFFICE_MCP_ALLOW_SOFFICE` | true | Allow LibreOffice if installed |

## Tools

Format-agnostic: `office_inspect`, `office_create`, `office_metadata`, `office_convert`, `office_validate`, `office_ooxml_inspect`, `office_compare`, `office_batch`

Word: `word_extract`, `word_edit`, `word_find_replace`, `word_layout`

Excel: `excel_read`, `excel_write`, `excel_sheets`, `excel_format`, `excel_structure`, `excel_charts`, `excel_analyze`, `excel_recalculate`

PowerPoint: `pptx_extract`, `pptx_edit`

## Unavailable (honest)

- VBA execution, Power Query, Power Pivot
- Pixel-perfect Word pagination
- SmartArt authoring
- Password cracking
- Full Excel calculation engine without Excel/LibreOffice

## Tests

```bash
pip install -e "./office-documents-mcp[dev]"
pytest office-documents-mcp/tests
```
