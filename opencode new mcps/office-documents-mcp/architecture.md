# Office Documents MCP — Architecture

## Why this shape

Existing Office MCPs either (a) wrap one library function per tool, or (b) only generate files from markdown. Real work is mixed: inspect an unknown workbook, patch a range, restyle a heading, dump tables to CSV, then batch-convert a folder.

The architecture therefore has:

1. **Semantic tools** aligned to jobs-to-be-done.
2. **Domain adapters** so python-docx/openpyxl/python-pptx can be replaced.
3. **A shared security/path/error kernel** used by every tool.
4. **Optional conversion adapter** that is detected at runtime, never assumed.

```
MCP client (Claude, Cursor, …)
        │  stdio JSON-RPC
        ▼
┌───────────────────┐
│  office_mcp.server │  tool registration, result wrapping
└─────────┬─────────┘
          ▼
┌───────────────────┐
│  domain layer      │  models, limits, validation, batch plans
└─────────┬─────────┘
          ▼
┌───────────────────┐
│  adapters          │
│  word / excel /    │
│  pptx / ooxml /    │
│  conversion        │
└─────────┬─────────┘
          ▼
 python-docx  openpyxl  python-pptx  lxml  pandas  soffice?
```

## Technology selection (architecture view)

| Concern | Choice | Why |
|---------|--------|-----|
| Protocol | Official `mcp` Python SDK | Tier-1, decorator tools, stdio |
| Word | python-docx adapter | Only mature RW Python API |
| Excel | openpyxl adapter | RW + styles + charts |
| PPT | python-pptx adapter | Only mature RW Python API |
| Package forensics | zipfile + lxml | Diagnostics without loading object models |
| Analysis | pandas | Vectorized profiling |
| HTML/MD extract | mammoth | Better semantics than raw XML text |
| PDF | LibreOffice adapter | Highest OSS fidelity |

## Tool surface (semantic)

Format-agnostic:

- `office_inspect` — type, parts, macros, encryption, counts
- `office_create` — new document with optional seed content
- `office_metadata` — get/set Dublin-core-like properties
- `office_convert` — md/html/csv/json/txt/pdf
- `office_validate` — package + required parts
- `office_ooxml_inspect` — parts, content types, XML peek
- `office_compare` — text/structure diff
- `office_batch` — map an operation over a folder

Word:

- `word_extract` — blocks, tables, comments, headers, images
- `word_edit` — list of operations (paragraph, heading, list, table, image, break, comment)
- `word_find_replace`
- `word_layout` — sections, headers/footers, styles, page setup

Excel:

- `excel_read` / `excel_write`
- `excel_sheets`
- `excel_format`
- `excel_structure` — merge, freeze, filter, tables, names
- `excel_charts`
- `excel_analyze`
- `excel_recalculate` — optional LibreOffice

PowerPoint:

- `pptx_extract`
- `pptx_edit`

## Result contract

Every tool returns JSON:

```json
{
  "ok": true,
  "data": {},
  "warnings": [],
  "meta": {"elapsed_ms": 12, "adapter": "openpyxl"}
}
```

Failures:

```json
{
  "ok": false,
  "error": {
    "code": "VALIDATION|NOT_FOUND|PERMISSION|UNSUPPORTED|DEPENDENCY_MISSING|MALFORMED|TIMEOUT|INTERNAL|SECURITY",
    "message": "...",
    "details": {}
  }
}
```

Tools do not raise uncaught exceptions to the LLM; adapters raise typed errors that the server maps.

## Extension points

- `adapters/conversion.py` — add COM or Gotenberg
- `adapters/word.py` — add byte-preserving OOXML patcher
- config env: `OFFICE_MCP_ROOT`, `OFFICE_MCP_MAX_BYTES`, `OFFICE_MCP_ALLOW_WRITE`
