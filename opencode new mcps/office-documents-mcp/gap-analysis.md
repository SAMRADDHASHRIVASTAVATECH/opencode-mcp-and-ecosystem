# Office MCP — second research pass / gap analysis

After implementation, a second pass against python-docx 1.2, openpyxl, python-pptx, and existing Office MCPs.

## Added vs first design

- OOXML forensics and zip-bomb guards
- Markdown → DOCX
- mammoth HTML/MD extract
- Spreadsheet profiling
- Batch convert
- Structured errors for missing LibreOffice

## Still missing (documented, not pretended)

| Gap | Why not now |
|-----|-------------|
| Content controls / structured document tags | python-docx support incomplete |
| TOC field refresh | Needs Word/LibreOffice layout |
| Mail merge | Domain-specific; can be done with find_replace |
| Pivot tables | openpyxl cache only |
| Formula calculation | No Excel engine; LibreOffice optional |
| Tracked changes round-trip | Needs OOXML-level patcher |
| PPTX animations / SmartArt | python-pptx |
| Legacy .doc/.xls/.ppt write | Binary OLE |
| Byte-preserving surgical XML patch | GenOffice approach; future adapter |

## Libraries re-checked

office_oxide is extract-fast but not an authoring API — correctly not primary.
xlsxwriter remains write-only — correctly not primary.
Open XML SDK would require .NET — out of scope for this Python MCP.
