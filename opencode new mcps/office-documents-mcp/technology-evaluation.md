# Office Documents MCP — Technology Evaluation

## Decision summary

| Layer | Primary | Fallback | Rejected for primary |
|-------|---------|----------|----------------------|
| MCP runtime | Official Python SDK (`mcp`, FastMCP/`MCPServer`) | — | Custom JSON-RPC |
| Word | python-docx | lxml OOXML | COM, Apache POI |
| Excel | openpyxl | pandas (analysis), write_only mode | xlsxwriter (write-only), IronXL (paid) |
| PowerPoint | python-pptx | lxml OOXML | PptxGenJS (Node) |
| Package/XML | zipfile + defusedxml/lxml | — | raw xml.etree without defuse |
| DOCX→HTML/MD | mammoth | custom text dump | pandoc (heavy optional) |
| Analysis | pandas | stdlib statistics | — |
| PDF / recalc | LibreOffice headless (optional) | structured “unavailable” | unoconv (unmaintained), MS Office COM (Windows-only) |
| Images | Pillow | — | — |
| Fast extract-only | office_oxide (optional future) | — | Not mature as a write API |

## Detailed comparisons

### Word

| Library | License | Read | Write | Comments | Headers | Maturity |
|---------|---------|------|-------|----------|---------|----------|
| python-docx | MIT | Yes | Yes | Yes (≥1.2) | Yes | Highest in Python |
| lxml on document.xml | BSD | Yes | Fragile | Manual | Manual | Expert escape hatch |
| mammoth | BSD | HTML/MD extract | No | No | Partial | Best semantic extract |
| docx-rs / office_oxide | MIT | Fast extract | Limited | — | — | Speed, not authoring |
| Open XML SDK | MIT | Yes | Yes | Yes | Yes | .NET, not this MCP |
| win32com Word | — | Yes | Yes | Yes | Yes | Requires Office |

**Choice:** python-docx is the only mature, cross-platform, MIT, read/write Python API. mammoth is added for high-quality HTML/Markdown extract.

### Excel

| Library | Read | Write | Charts | Styles | Large files | Calc |
|---------|------|-------|--------|--------|-------------|------|
| openpyxl | Yes | Yes | Yes | Yes | Medium (read_only/write_only) | No |
| xlsxwriter | No | Yes | Excellent | Yes | Fast write | No |
| pandas | Data | Data | No | Limited | Good | No |
| python-calamine / office_oxide | Fast | No | No | No | Excellent | No |
| formulas / pycel | — | — | — | — | — | Partial, incomplete Excel |
| xlrd | xls/xlsx old | No | No | No | — | No |
| pywin32 Excel | Yes | Yes | Yes | Yes | — | Yes (real Excel) |

**Choice:** openpyxl as the authoring/inspection engine (charts, styles, validation, tables). pandas for `excel_analyze`. LibreOffice optional for true recalc. xlsxwriter not primary because it cannot modify existing files.

### PowerPoint

| Library | Read | Write | Notes | Charts |
|---------|------|-------|-------|--------|
| python-pptx | Yes (limited vs create) | Yes | Yes | Yes |
| PptxGenJS | Create | Create | — | Yes |
| COM PowerPoint | Yes | Yes | Yes | Yes |

**Choice:** python-pptx is the only serious Python option.

### Conversion

| Tool | Fidelity | Deps | License | Notes |
|------|----------|------|---------|-------|
| LibreOffice `--headless --convert-to` | High | Heavy binary | MPL | Best optional PDF |
| unoconv | High | LibreOffice + unmaintained | — | Prefer soffice directly |
| docx2pdf | High on Win/Mac | MS Word | MIT | Platform-specific |
| reportlab rebuild | Low | Pure Python | BSD | Loses layout |
| mammoth | Semantic HTML | Pure Python | BSD | Not PDF |

**Choice:** detect `soffice`/`libreoffice`; if missing, conversion to PDF returns a structured `DEPENDENCY_MISSING` error. Markdown/CSV/JSON/HTML do not require it.

### MCP SDK

Official Python SDK is Tier 1. v2 renamed FastMCP → MCPServer; decorator API remains. This project uses a compatibility shim so both v1 and v2 work.

Standalone Prefect FastMCP 3.x was not chosen: extra composition features are unused; official SDK is enough.

## Installation complexity

Core (always): `mcp`, `python-docx`, `openpyxl`, `python-pptx`, `lxml`, `pillow`, `pandas`, `mammoth`, `defusedxml`

Optional: LibreOffice system package

No API keys, no accounts, no elevated privileges.

## License posture

All primary libraries are MIT/BSD. Combined project license: MIT.
