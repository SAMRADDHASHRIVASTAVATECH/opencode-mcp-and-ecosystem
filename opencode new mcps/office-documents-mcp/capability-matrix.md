# Office Documents MCP — Capability Matrix

Legend: **P** = primary tool coverage, **F** = fallback/optional, **N** = not supported (documented).

## BASIC

| Capability | Class | Status | Tool(s) |
|------------|-------|--------|---------|
| Detect format & package health | BASIC | P | `office_inspect` |
| Create blank DOCX/XLSX/PPTX | BASIC | P | `office_create` |
| Read core/app metadata | BASIC | P | `office_metadata` |
| Extract Word text in reading order | BASIC | P | `word_extract` |
| Add headings, paragraphs, lists | BASIC | P | `word_edit` |
| Insert Word table | BASIC | P | `word_edit` |
| Read Excel used range | BASIC | P | `excel_read` |
| Write cells / ranges | BASIC | P | `excel_write` |
| List/add/rename/delete sheets | BASIC | P | `excel_sheets` |
| List slides and titles | BASIC | P | `pptx_extract` |
| Add/delete/reorder slides | BASIC | P | `pptx_edit` |
| Extract plain text from PPTX | BASIC | P | `pptx_extract` |

## ADVANCED

| Capability | Class | Status | Tool(s) |
|------------|-------|--------|---------|
| Headers/footers, sections, page setup | ADVANCED | P | `word_layout` |
| Images in Word | ADVANCED | P | `word_edit` |
| Find/replace (regex optional) | ADVANCED | P | `word_find_replace` |
| Comments (read/add) | ADVANCED | P | `word_extract`, `word_edit` |
| Styles listing / apply heading styles | ADVANCED | P | `word_layout` |
| Number formats, fonts, fills, borders | ADVANCED | P | `excel_format` |
| Merge/unmerge, freeze, auto-filter | ADVANCED | P | `excel_structure` |
| Named ranges | ADVANCED | P | `excel_structure` |
| Excel tables (ListObjects) | ADVANCED | P | `excel_structure` |
| Charts | ADVANCED | P | `excel_charts` |
| Conditional formatting (basic) | ADVANCED | P | `excel_format` |
| Data validation | ADVANCED | P | `excel_format` |
| Formulas write + cached value read | ADVANCED | P | `excel_write`, `excel_read` |
| Slide notes | ADVANCED | P | `pptx_edit` |
| Pictures, tables, text boxes on slides | ADVANCED | P | `pptx_edit` |
| Markdown → DOCX | ADVANCED | P | `office_convert` |
| DOCX → Markdown/HTML | ADVANCED | P | `office_convert` |
| XLSX ↔ CSV/JSON | ADVANCED | P | `office_convert` |

## EXPERT

| Capability | Class | Status | Tool(s) |
|------------|-------|--------|---------|
| OOXML part listing & XML peek | EXPERT | P | `office_ooxml_inspect` |
| Macro / VBA presence detection | EXPERT | P | `office_inspect` |
| Encryption detection | EXPERT | P | `office_inspect` |
| Content-type / relationship graph | EXPERT | P | `office_ooxml_inspect` |
| Spreadsheet statistical profile | EXPERT | P | `excel_analyze` |
| Duplicate/null/type inference | EXPERT | P | `excel_analyze` |
| Document compare (text/structure) | EXPERT | P | `office_compare` |
| Formula recalc via LibreOffice | EXPERT | F | `excel_recalculate` |
| PDF export via LibreOffice | EXPERT | F | `office_convert` |

## AUTOMATION / BATCH

| Capability | Class | Status | Tool(s) |
|------------|-------|--------|---------|
| Apply many edits in one call | AUTOMATION | P | `word_edit`, `excel_write`, `pptx_edit` (ops lists) |
| Folder batch convert/extract | BATCH | P | `office_batch` |
| Template fill (placeholder map) | AUTOMATION | P | `word_find_replace`, `excel_write` |

## DIAGNOSTICS / RECOVERY

| Capability | Class | Status | Tool(s) |
|------------|-------|--------|---------|
| Validate ZIP + required parts | DIAGNOSTICS | P | `office_validate` |
| Report missing relationships | DIAGNOSTICS | P | `office_validate` |
| Recover text from damaged package | RECOVERY | P | `office_ooxml_inspect` + extract best-effort |
| Repair is not attempted blindly | RECOVERY | N | Documented limitation |

## ANALYSIS / CONVERSION / ADMIN

| Capability | Class | Status | Tool(s) |
|------------|-------|--------|---------|
| Workbook analysis | ANALYSIS | P | `excel_analyze` |
| Presentation outline | ANALYSIS | P | `pptx_extract` |
| Format conversion | CONVERSION | P | `office_convert` |
| Set creator/title/subject | ADMINISTRATION | P | `office_metadata` |

## Explicitly out of scope

| Capability | Reason |
|------------|--------|
| Execute VBA / macros | Arbitrary code execution |
| Power Query / Power Pivot / DAX | Proprietary engine |
| Full pivot cache refresh | Needs Excel |
| SmartArt authoring | Unsupported by python-pptx |
| Pixel-perfect pagination | Needs Word layout engine |
| Password cracking | Security |
| Legacy .doc/.xls/.ppt full write | Binary OLE; extract-only if possible |
| Live COM automation of installed Office | Optional future adapter; not required |
