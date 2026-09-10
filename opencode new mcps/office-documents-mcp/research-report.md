# Office Documents MCP — Research Report

**Domain:** Microsoft Office / Office Open XML documents (DOCX, XLSX, PPTX)  
**Date:** 2026-09-09  
**Status:** Research complete. Implementation proceeds from this report.

---

## 1. Domain model

Office documents in the modern Microsoft stack are **Office Open XML (OOXML)** packages: ZIP archives of XML parts, relationships, media, and metadata. The governing specifications are ECMA-376 and ISO/IEC 29500.

| Format | Package | Main parts | Typical use |
|--------|---------|------------|-------------|
| DOCX | ZIP + `[Content_Types].xml` | `word/document.xml`, styles, numbering, headers, comments, media | Narrative documents |
| XLSX | ZIP | `xl/workbook.xml`, worksheets, sharedStrings, styles, charts, tables | Tabular data, formulas, charts |
| PPTX | ZIP | `ppt/presentation.xml`, slides, layouts, masters, notes, media | Slide decks |
| DOCM / XLSM / PPTM | Same + `vbaProject.bin` | Macro-enabled | Automation (unsafe to execute) |
| DOC / XLS / PPT | OLE Compound File (CFBF) | Binary streams | Legacy Office 97–2003 |

**Core concepts**

- **Package / part / relationship:** every image, slide, worksheet is a part; `.rels` files wire them together.
- **Styles vs direct formatting:** Word styles, Excel cell styles/named styles, PowerPoint slide layouts/masters.
- **Shared strings (Excel):** cell values often stored in a shared table, not in-cell.
- **Formulas vs cached values:** XLSX stores formula text *and* last-calculated cached values. Python libraries generally do **not** recalculate the Excel calculation engine.
- **Sections (Word):** page size, orientation, headers/footers are per-section.
- **Comments / revisions:** review artifacts live in separate XML parts.
- **Content types:** Strict vs Transitional OOXML; most real-world files are Transitional.

**Common workflows**

1. Create a professional document from structured content (markdown, JSON, tables).
2. Inspect an unknown file (structure, metadata, tables, images).
3. Extract text/tables for RAG or analysis.
4. Surgical edit (find/replace, append, patch a range).
5. Format (styles, number formats, charts).
6. Convert (markdown, CSV, HTML, PDF if a renderer exists).
7. Batch process folders.
8. Validate / diagnose corruption.
9. Compare two versions.

---

## 2. Official sources and specifications

| Source | Role |
|--------|------|
| ECMA-376 / ISO 29500 | OOXML standard |
| Microsoft Open XML SDK (`DocumentFormat.OpenXml`) | Official .NET SDK |
| [python-docx](https://python-docx.readthedocs.io/) | De-facto Python Word API |
| [openpyxl](https://openpyxl.readthedocs.io/) | De-facto Python Excel 2010+ API |
| [python-pptx](https://python-pptx.readthedocs.io/) | De-facto Python PowerPoint API |
| LibreOffice UNO / `--headless --convert-to` | High-fidelity conversion/rendering |
| Apache POI | Java reference-quality Office stack |

There is **no official Microsoft Python SDK** for local OOXML. Graph API / Office.js require a live Office host or cloud tenant and are out of scope for a standalone local MCP.

---

## 3. Existing MCP implementations (lessons)

| Project | Strength | Gap |
|---------|----------|-----|
| GongRzhe/Office-Word-MCP-Server | Focused Word tools | Word-only |
| walkingzzzy/office-mcp | Combined Word/Excel/PPT via python-docx/openpyxl/python-pptx | Documents 85% coverage; VBA/Power Query unsupported |
| ForLegalAI/mcp-ms-office-documents | Markdown → Office generation | Weak round-trip editing |
| hongkongkiwi/docx-mcp (Rust) | Sandbox flags, max-size, whitelist | Word-centric |
| criptogus/mcp-genoffice | Byte-preserving surgical OOXML edits | Incomplete XLSX |
| mhackermsft/OfficeMCP (.NET) | Unified `office_*` + format-specific tools | Requires .NET |
| Graph-based Office MCPs | Live Excel/Word in OneDrive | Account, network, not local files |

**Design takeaway:** high-value semantic tools (`inspect`, `extract`, `edit`, `analyze`, `convert`, `batch`) beat 1:1 library wrappers. Combine format-agnostic entry points with format-specific expert tools. Enforce sandbox/size limits like the Rust docx-mcp.

---

## 4. File formats and protocols

Supported as first-class:

- `.docx`, `.dotx` (templates treated as documents)
- `.xlsx`, `.xlsm` (macros detected, never executed), `.xltx`
- `.pptx`, `.potx`
- Interchange: `.csv`, `.tsv`, `.json`, `.md`, `.html`, `.txt`

Detected but not fully authored:

- `.doc`, `.xls`, `.ppt` (legacy OLE) — extract-only if a parser is present; otherwise structured error
- `.odt`, `.ods`, `.odp` — conversion only if LibreOffice is installed
- Password-encrypted OOXML (ECMA-376 encryption) — detect, do not attempt to crack
- PDF — optional export via LibreOffice; not a native authoring target of this MCP

---

## 5. Automation capabilities that are real

| Capability | Feasible locally? | How |
|------------|-------------------|-----|
| Create/edit DOCX | Yes | python-docx |
| Headers/footers, sections, tables, images, styles | Yes | python-docx |
| Comments | Yes (python-docx ≥ 1.2) | python-docx |
| TOC field update | Partial | Can insert TOC field; Word/LibreOffice must refresh |
| Tracked changes full fidelity | Limited | Better via OOXML-level patch |
| Create/edit XLSX | Yes | openpyxl |
| Formulas write | Yes | openpyxl |
| Formula *calculation* | Partial | Cached values; optional LibreOffice recalc |
| Charts, merged cells, freeze, auto-filter, data validation, conditional formatting | Yes | openpyxl |
| Pivot tables | Limited | openpyxl can create basic caches; not full Excel engine |
| VBA / Power Query / Power Pivot | No | Proprietary engines |
| Create/edit PPTX | Yes | python-pptx |
| Slide layouts, placeholders, tables, pictures, notes | Yes | python-pptx |
| SmartArt, animations, transitions fidelity | No / poor | Not in python-pptx |
| Pixel-perfect PDF/PNG render | Only with LibreOffice or MS Office | Optional adapter |
| Markdown round-trip | Practical, lossy | Custom mapper + mammoth (docx→html/md) |

---

## 6. Limitations (must be honest in the MCP)

1. **No Microsoft layout engine.** Pagination, kerning, and “what you see in Word” cannot be guaranteed.
2. **Formulas are not Excel.** Writing `=SUM(A1:A10)` stores the formula; the cached value is empty until Excel/LibreOffice calculates.
3. **Macros must never execute.** Detect `vbaProject.bin` and report it.
4. **SmartArt, ActiveX, embedded OLE objects** are opaque blobs.
5. **Password-protected files** cannot be opened without the password (and we will not brute-force).
6. **Very large XLSX** (hundreds of MB, 1M+ rows) need streaming (`read_only` / `write_only`) or pandas+openpyxl.
7. **XXE / zip bombs** are real attack surfaces on untrusted OOXML.

---

## 7. Platform behavior

| Platform | Native libs | PDF conversion |
|----------|-------------|----------------|
| Linux | python-docx / openpyxl / python-pptx work fully | LibreOffice headless |
| macOS | Same | LibreOffice or Word JXA (docx2pdf) |
| Windows | Same + optional COM (win32com) for high-fidelity | Word/Excel COM or LibreOffice |

This MCP is **cross-platform** and does **not** require Microsoft Office. COM/LibreOffice are optional fidelity upgrades.

---

## 8. Performance notes

- openpyxl default mode loads the whole workbook; use `read_only=True` for inspection of large files.
- `write_only=True` for dumping large tables.
- python-docx loads the full document XML; >50–100 MB DOCX is unusual and should be rejected or streamed at OOXML level.
- Shared-string tables dominate Excel parse time.
- Batch conversion via LibreOffice should reuse a listener if available; spawning soffice per file is slow.

**Practical limits (defaults):** 50 MB per file, 200k cells per read, 50 files per batch, 30 s conversion timeout.

---

## 9. Security findings (summary)

See `security-model.md`. Highlights: path sandbox, zip-bomb limits, defusedxml, never execute VBA, never follow remote relationships, redact password fields, refuse encrypted files without explicit password (and do not log it).

---

## 10. Implementation implication

Build a **local, dependency-light, Office-free** MCP on python-docx + openpyxl + python-pptx + lxml, with:

- OOXML package inspector (zip/xml) for diagnostics
- pandas for spreadsheet analysis
- mammoth for DOCX→HTML/Markdown
- optional LibreOffice adapter for PDF and formula recalc
- adapter layer so COM or Open XML SDK could be added later
