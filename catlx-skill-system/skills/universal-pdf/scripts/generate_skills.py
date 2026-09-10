#!/usr/bin/env python3
"""Generate the interconnected skill layer + registry + INDEX from one model.

This keeps every SKILL.md consistent and verifiable against the real Python
engine (each skill documents its actual callable). Regenerate with:
    python scripts/generate_skills.py
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILLS_DIR = ROOT / "skills"
REG = ROOT / "registry"

# --------------------------------------------------------------------------
# Each entry: slug, category, title, blurb, operations, engine(module:function),
# preferred/fallback tools, validation, when, examples(list of request texts),
# related(slugs).  ``help`` is the detailed "How" text for the SKILL.md body.
# --------------------------------------------------------------------------

CREATE = "PDF Creation"
MGT = "PDF Management"

S = []


def add(slug, category, title, operations, engine, tools, fallback,
        validation, when, examples, related, extra=""):
    S.append(dict(slug=slug, category=category, title=title, blurb=title,
                  operations=operations, engine=engine, tools=tools,
                  fallback=fallback, validation=validation, when=when,
                  examples=examples, related=related, extra=extra))


add("pdf-create", CREATE,
    "Create PDFs from documents & data",
    ["plain text", "Markdown (subset)", "HTML (subset)", "images", "structured rows",
     "reports", "invoices", "cover pages", "tables", "lists", "headings",
     "headers/footers", "page numbers", "bookmarks", "metadata", "TOC placeholder"],
    "core.create:create_pdf / create_from_markdown / create_from_text / create_from_html / create_from_images / create_report_from_rows",
    "reportlab platypus (vector, templated)", "PyMuPDF insert_text (simple docs)",
    "openable; page_count>=1; metadata valid; pages render",
    "Generate a brand new professional PDF from text, Markdown, HTML, images or tabular data.",
    ["Create a 3-page report from this JSON of quarterly sales.",
     "Turn README.md into a clean PDF.",
     "Make an invoice PDF from these line items."],
    ["pdf-read", "pdf-export", "pdf-inspect", "pdf-orchestrate"])

add("pdf-read", MGT,
    "Universal text reading",
    ["read full text", "read selected pages", "read preserving page boundaries",
     "stream huge documents page-by-page", "detect whether OCR needed"],
    "core.extract:extract_text / extract_per_page / iter_page_text / detect_text_layer",
    "PyMuPDF text layer", "pdfplumber (layout text)",
    "text_coverage; page coverage",
    "Pull readable text out of a digital PDF without loading it into the model.",
    ["Read this PDF and tell me the main points.",
     "Show me the text on pages 4 and 7."],
    ["pdf-extract", "pdf-inspect", "pdf-ocr", "pdf-search", "pdf-orchestrate"])

add("pdf-inspect", MGT,
    "Inspect a PDF into a structured profile",
    ["page count", "page size/orientation", "metadata", "fonts", "image count",
     "links", "annotations", "forms present", "encryption/permissions",
     "PDF version", "embedded files", "text layer health"],
    "core.inspect:inspect",
    "PyMuPDF", "pypdf (permission/version facts)",
    "openable; page_count>0",
    "Before operating on an unknown PDF, build a cheap structured profile.",
    ["What type of document is this? How many pages?",
     "Profile this PDF: is it scanned or text?"],
    ["pdf-read", "pdf-validation", "pdf-orchestrate", "pdf-provenance"])

add("pdf-extract", MGT,
    "Extract text/structure with provenance",
    ["extract text", "per-page blocks with bbox", "multi-column via layout",
     "preserve page/position info", "image-only pages routed to OCR"],
    "core.extract:extract_text / extract_blocks_per_page / extract_per_page",
    "PyMuPDF text (text/dict)", "pdfplumber (column layout)",
    "text_coverage; page coverage",
    "Extract structured content while keeping page & position so downstream "
    "steps can cite sources.",
    ["Extract all the body text of this report keeping page numbers."],
    ["pdf-read", "pdf-tables", "pdf-ocr", "pdf-provenance"])

add("pdf-ocr", MGT,
    "OCR scanned / image-only pages",
    ["detect when OCR needed", "make scanned pages searchable",
     "page-level recognition", "language selection", "skip already-text pages",
     "graceful degradation when no OCR engine"],
    "core.ocr:detect_ocr_need / make_searchable / ocr_page_text",
    "ocrmypdf (add searchable layer)", "pytesseract+tesseract / easyocr (page text)",
    "OCR completeness; output openable",
    "Only pages with no usable text layer are OCR'd; pages with text are skipped.",
    ["OCR this scanned book so I can search it.",
     "Make this image-only PDF selectable text."],
    ["pdf-read", "pdf-vision", "pdf-render", "pdf-inspect"])

add("pdf-render", MGT,
    "Render PDF pages to images",
    ["render page(s) to PNG/JPG", "custom DPI", "page subset",
     "single-page raster for vision/OCR pre-pass"],
    "core.images:render_pages / render_page_to_bytes",
    "PyMuPDF pixmap", "—",
    "rendered file count; each opens",
    "Produce images of pages for OCR, vision, thumbnails or preview.",
    ["Give me a PNG of page 1 at 200 dpi."],
    ["pdf-ocr", "pdf-vision", "pdf-export", "pdf-compare"])

add("pdf-vision", MGT,
    "Visual interpretation of pages/figures",
    ["describe a rendered page", "interpret charts/graphs/diagrams/forms",
     "graceful fallback to text/OCR when no vision model"],
    "core.vision:describe_page  (register a provider first)",
    "pluggable vision provider (agent/LLM)", "text/OCR extraction",
    "description returned when provider present",
    "Only invoke vision when text/OCR is insufficient to answer the request.",
    ["What does the chart on page 12 show?",
     "Describe the diagram on page 3."],
    ["pdf-ocr", "pdf-render", "pdf-extract", "pdf-orchestrate"])

add("pdf-tables", MGT,
    "Detect & extract tables as structure",
    ["extract tables", "header/rows reconstruction", "multi-page tables",
     "to CSV", "to XLSX", "to JSON", "to Markdown", "column-consistency validation"],
    "core.tables:extract_tables / tables_to_csv / tables_to_xlsx / tables_to_json / tables_to_markdown / validate_tables",
    "pdfplumber layout extraction", "PyMuPDF find_tables",
    "extracted>0; each export written; column consistency",
    "Preserve tables as rows/columns instead of flattening to text.",
    ["Extract every table and export to Excel.",
     "Turn these PDF tables into CSV."],
    ["pdf-extract", "pdf-export", "pdf-provenance", "pdf-orchestrate"])

add("pdf-search", MGT,
    "Search within a PDF",
    ["exact/phrase search", "keyword search", "regex search", "single-page search",
     "whole-document mention scan (streamed)", "source page in every result"],
    "core.search:search_document / find_mentions_all",
    "PyMuPDF text layer streaming", "persisted index (large docs)",
    "searched; hits carry page",
    "Find every mention of a term/phrase with its source page.",
    ["Find every mention of 'quantum' in this 5,000 page book.",
     "Show me where the phrase 'terms of service' appears."],
    ["pdf-index", "pdf-chunk", "pdf-read", "pdf-orchestrate"])

add("pdf-index", MGT,
    "Build a reusable search index",
    ["positional term index", "page-level inverted index", "persisted JSON",
     "reuse across queries without re-parsing"],
    "core.search:build_index",
    "positional inverted index (JSON)", "SQLite/DB backend for huge corpora",
    "indexed terms > 0",
    "For huge or repeatedly-queried documents, index once then retrieve fast.",
    ["Index this manual so I can query it repeatedly."],
    ["pdf-search", "pdf-chunk", "pdf-document-state", "pdf-orchestrate"])

add("pdf-chunk", MGT,
    "Context-safe chunking for large/small-model docs",
    ["chunk by page", "chunk by max chars w/ overlap", "persist chunks + page text",
     "only the needed chunks are ever passed to the model"],
    "core.chunk:chunk_document / chunk_text",
    "local chunker (page & word boundaries)", "—",
    "chunks>=1",
    "Prepare any document for retrieval without ever filling the context window.",
    ["Chunk this document for later Q&A."],
    ["pdf-summarize", "pdf-qa", "pdf-index", "pdf-provenance"])

add("pdf-summarize", MGT,
    "Summarize with bounded context",
    ["extractive summary", "bucket summaries for huge docs", "hierarchical summary",
     "persist to knowledge store", "optional abstractive via injected LLM"],
    "core.summarize:summarize",
    "local extractive engine", "optional injected LLM (abstractive)",
    "summarized; output within configured context size",
    "Produce a summary of any size document that fits a small model's context.",
    ["Summarize this book in one page.",
     "Give me a chapter-by-chapter summary."],
    ["pdf-chunk", "pdf-qa", "pdf-search", "pdf-orchestrate"])

add("pdf-qa", MGT,
    "Question answering over a document",
    ["locate relevant pages/chunks", "extract evidence with provenance",
     "compose an answer from context only", "no document in the model context"],
    "core.qa:answer  (uses index/chunks + an injected reasoning callable)",
    "retrieval over index/chunks", "no-model: returns retrieved evidence",
    "answer grounded in retrieved pages",
    "Answer questions against a document, giving page citations.",
    ["Which section discusses pricing?",
     "Summarize the refund policy from this 10k-page doc."],
    ["pdf-chunk", "pdf-search", "pdf-summarize", "pdf-orchestrate"])

add("pdf-analyze", MGT,
    "Analyze a document",
    ["statistical profile", "structure & resource analysis", "text-layer health",
     "routing hints (OCR? huge? tables?)"],
    "core.inspect + core.resource:strategy",
    "PyMuPDF + resource-aware strategy", "—",
    "profile produced",
    "Characterise a document before expensive operations and pick a strategy.",
    ["Analyze this PDF and decide whether it needs OCR."],
    ["pdf-inspect", "pdf-ocr", "pdf-validation", "pdf-orchestrate"])

add("pdf-edit", MGT,
    "Structural page editing",
    ["insert pages", "delete pages", "replace pages (delete+insert)",
     "add blank pages", "add images to a page"],
    "core.manipulate:insert_blank_pages / delete_pages (+ create overlay for images)",
    "PyMuPDF reconstruction", "pypdf (pure-structural)",
    "page_count matches expectation",
    "Edit the page set of a PDF. In-place content editing is limited, so safe "
    "reconstruction/overlay is used instead of pretending to edit.",
    ["Delete pages 4,7,9.",
     "Insert a blank page after page 3."],
    ["pdf-reorder", "pdf-split", "pdf-merge", "pdf-orchestrate"])

add("pdf-annotate", MGT,
    "Add annotations",
    ["highlight", "underline", "strikeout", "text note", "free text", "square/circle",
     "line/arrow", "link", "preserve existing annotations"],
    "core.annotate:add_annotations",
    "PyMuPDF annotation API", "—",
    "added>=0",
    "Annotate pages with standard markups and notes.",
    ["Highlight all occurrences of the keyword on page 2."],
    ["pdf-links", "pdf-inspect", "pdf-orchestrate"])

add("pdf-merge", MGT,
    "Merge PDFs",
    ["merge N PDFs in order", "preserve bookmarks with page offsets"],
    "core.manipulate:merge_pdfs",
    "PyMuPDF insert_pdf", "pypdf PdfWriter",
    "page_count == sum of inputs",
    "Combine multiple PDFs into one.",
    ["Merge these three PDFs into one file."],
    ["pdf-split", "pdf-reorder", "pdf-orchestrate"])

add("pdf-split", MGT,
    "Split a PDF",
    ["split every N pages", "split into ranges", "split at TOC top-level",
     "extract selected pages"],
    "core.manipulate:split_pdf / extract_pages",
    "PyMuPDF", "pypdf",
    "produced file count",
    "Break one PDF into parts.",
    ["Split this PDF every 5 pages.",
     "Extract just pages 1-3 and 8."],
    ["pdf-merge", "pdf-reorder", "pdf-orchestrate"])

add("pdf-reorder", MGT,
    "Reorder / reverse / duplicate pages",
    ["arbitrary order", "reverse", "duplicate", "subset ordering"],
    "core.manipulate:reorder_pdf",
    "PyMuPDF", "pypdf",
    "page_count == len(order)",
    "Rearrange pages into any order.",
    ["Reverse the page order.",
     "Put page 3 first, then pages 5 and 1."],
    ["pdf-edit", "pdf-split", "pdf-merge", "pdf-orchestrate"])

add("pdf-rotate", MGT, "Rotate pages",
    ["rotate 90/180/270", "selected pages", "preserve text/orientation metadata"],
    "core.manipulate:rotate_pdf", "PyMuPDF set_rotation", "pypdf",
    "page_count preserved",
    "Fix or change page orientation.",
    ["Rotate the scanned page 4 by 90 degrees."],
    ["pdf-reorder", "pdf-crop", "pdf-orchestrate"])

add("pdf-crop", MGT, "Crop pages",
    ["uniform margin crop", "asymmetric insets", "selected pages"],
    "core.manipulate:crop_pdf", "PyMuPDF set_cropbox/mediabox", "—",
    "page_count preserved",
    "Trim edges / white borders of pages.",
    ["Crop 0.5 inch margins off every page."],
    ["pdf-rotate", "pdf-scale", "pdf-orchestrate"])

add("pdf-scale", MGT, "Scale / resize pages",
    ["uniform scale factor", "set page size", "selected pages"],
    "core.manipulate:scale_pdf", "PyMuPDF page rebuild", "—",
    "page_count preserved",
    "Enlarge/shrink page content or normalise page size.",
    ["Resize all pages to A4."],
    ["pdf-crop", "pdf-orchestrate"])

add("pdf-watermark", MGT,
    "Add watermarks & stamps",
    ["diagonal text watermark (arbitrary angle)", "image watermark", "opacity",
     "page selection", "stamp overlays (APPROVED/CONFIDENTIAL)"],
    "core.annotate:add_watermark / add_stamp",
    "reportlab overlay + PyMuPDF stamping", "—",
    "page_count preserved; overlay renders",
    "Protect or mark pages with text/image watermarks and stamps.",
    ["Watermark every page with 'CONFIDENTIAL'.",
     "Stamp page 1 with APPROVED."],
    ["pdf-header-footer", "pdf-annotate", "pdf-orchestrate"])

add("pdf-header-footer", MGT,
    "Add headers, footers, page numbers",
    ["running header", "running footer", "page numbers", "skip first page",
     "start number", "page selection"],
    "core.annotate:add_header_footer",
    "PyMuPDF insert_text", "—",
    "page_count preserved",
    "Add running heads/footers and page numbers.",
    ["Add 'Quarterly Report' header and page numbers."],
    ["pdf-watermark", "pdf-annotate", "pdf-orchestrate"])

add("pdf-metadata", MGT,
    "Read / write / remove metadata",
    ["read title/author/subject/keywords/creator/producer/dates",
     "write fields", "strip all metadata", "batch update"],
    "core.meta:set_metadata / remove_metadata (+ inspect for read)",
    "PyMuPDF set_metadata", "pypdf metadata",
    "metadata round-trips (verify after write)",
    "Manage document properties.",
    ["Set author to 'Legal Dept' and add keywords."],
    ["pdf-inspect", "pdf-provenance", "pdf-orchestrate"])

add("pdf-bookmarks", MGT,
    "Bookmarks / outline / TOC",
    ["extract TOC", "set/merge/remove outline", "TOC entries link to pages"],
    "core.bookmarks:extract_bookmarks / set_bookmarks / remove_bookmarks",
    "PyMuPDF get_toc/set_toc", "pypdf outline",
    "TOC present after set",
    "Read or write the navigation outline.",
    ["Build a table-of-contents outline from the headings."],
    ["pdf-links", "pdf-provenance", "pdf-orchestrate"])

add("pdf-links", MGT,
    "Hyperlinks",
    ["extract links (URI/page/rect)", "add URI links", "inspect link targets"],
    "core.bookmarks:extract_links / add_links",
    "PyMuPDF links", "—",
    "parsed/added",
    "Manage clickable links.",
    ["List all hyperlinks in the PDF."],
    ["pdf-annotate", "pdf-bookmarks", "pdf-orchestrate"])

add("pdf-forms", MGT,
    "Forms: detect, list, extract, flatten",
    ["detect form", "list fields+types+values", "extract data",
     "flatten values into content"],
    "core.forms:list_fields / extract_form_data / flatten_form",
    "PyMuPDF widget API", "pypdf (reader fields)",
    "fields enumerated",
    "Understand PDF AcroForms.",
    ["Are there fillable fields? List them."],
    ["pdf-fill-forms", "pdf-inspect", "pdf-orchestrate"])

add("pdf-fill-forms", MGT,
    "Fill AcroForm fields",
    ["fill by field name", "text/checkbox/radio/list", "optional flatten"],
    "core.forms:fill_form",
    "PyMuPDF widget update", "pypdf update_page_form_field_values",
    "each requested field filled",
    "Populate a form programmatically.",
    ["Fill the form with these values and flatten it."],
    ["pdf-forms", "pdf-sign", "pdf-orchestrate"])

add("pdf-sign", MGT,
    "Signatures",
    ["inspect signature fields", "place a visible signature image/text"],
    "core.security:sign_pdf / inspect_signatures",
    "PyMuPDF widget/image placement", "pypdf (certificate signature infra)",
    "signature placed; clearly reported as visual unless crypto infra used",
    "Add a signature or inspect signature fields. Visual placement never claims "
    "cryptographic validity.",
    ["Place my signature image on the last page."],
    ["pdf-fill-forms", "pdf-validation", "pdf-orchestrate"])

add("pdf-encrypt", MGT, "Encrypt / password-protect",
    ["AES-128/256", "user + owner passwords", "permission flags (print/modify/copy/annotate)"],
    "core.security:encrypt",
    "PyMuPDF encryption", "pypdf writer.encrypt",
    "output is_encrypted",
    "Add password protection and set permissions.",
    ["Encrypt this PDF with password 's3cret' and disallow copying."],
    ["pdf-decrypt", "pdf-permissions", "pdf-orchestrate"])

add("pdf-decrypt", MGT, "Decrypt / remove protection",
    ["open with password", "save unencrypted copy", "legitimate access workflows"],
    "core.security:decrypt",
    "PyMuPDF", "pypdf",
    "output not encrypted (when requested)",
    "Remove encryption from a document you are authorized to open.",
    ["Remove the password so it can be printed."],
    ["pdf-encrypt", "pdf-permissions", "pdf-orchestrate"])

add("pdf-permissions", MGT,
    "Permission handling",
    ["read permission flags", "set permissions while encrypting"],
    "core.security:encrypt(permissions=...) + inspect(security)",
    "PyMuPDF permissions", "pypdf permissions_flag",
    "flags reported / applied",
    "Control and inspect DRM-style usage permissions (legitimate management).",
    ["What operations are permitted on this PDF?"],
    ["pdf-encrypt", "pdf-inspect", "pdf-orchestrate"])

add("pdf-redact", MGT,
    "True content redaction",
    ["text-term redaction", "region redaction", "page-level", "metadata cleanup",
     "post-redaction leak verification"],
    "core.annotate:redact_text",
    "PyMuPDF redact annots + apply_redactions",
    "—",
    "underlying_content_removed (leak check passes)",
    "Remove sensitive content so it cannot be copied/selected, with verification.",
    ["Redact every mention of the account number and all metadata."],
    ["pdf-validation", "pdf-metadata", "pdf-provenance", "pdf-orchestrate"])

add("pdf-compress", MGT,
    "Reduce file size",
    ["structural cleanup", "image recompression", "reported savings",
     "quality/size profiles"],
    "core.compress:compress_pdf(profile=...)",
    "PyMuPDF rewrite_images + garbage/deflate", "structural-only cleanup",
    "openable; final_size <= original",
    "Shrink a PDF for email/web while choosing a quality profile.",
    ["Compress this PDF as much as possible.",
     "Make a web-optimized copy."],
    ["pdf-optimize", "pdf-repair", "pdf-orchestrate"])

add("pdf-optimize", MGT,
    "Optimize with quality profiles",
    ["maximum_quality", "balanced", "small_size", "web_optimized",
     "archive_optimized", "never silently destroy quality"],
    "core.compress:compress_pdf(profile=...)",
    "PyMuPDF", "structural-only cleanup",
    "openable; size reported per profile",
    "Choose the right quality/size tradeoff for the destination.",
    ["Optimize for archival (maximum quality).",
     "Produce a small-size version for email."],
    ["pdf-compress", "pdf-validation", "pdf-orchestrate"])

add("pdf-repair", MGT,
    "Diagnose & repair damaged PDFs",
    ["openability probe", "page-tree health", "renderability", "rebuild xrefs",
     "per-page rescue", "report unrecovered content"],
    "core.repair:diagnose / repair_pdf",
    "PyMuPDF re-save (garbage)", "pypdf structural rebuild",
    "openable after repair; recovered page count reported",
    "Recover usable content from a malformed/corrupt PDF and say what failed.",
    ["This PDF won't open - repair it."],
    ["pdf-validation", "pdf-compress", "pdf-orchestrate"])

add("pdf-convert", MGT,
    "Convert to/from other formats",
    ["PDF->TXT", "PDF->Markdown", "PDF->HTML", "PDF->JSON", "PDF->Images",
     "PDF->CSV/XLSX (tables)", "PDF->DOCX (when pandoc present)",
     "TXT/MD/HTML/Images->PDF"],
    "core.convert:convert_pdf (and core.create for creation direction)",
    "text/tables/render engines", "pandoc for DOCX (documented limitation)",
    "output exists; renderable; sanity",
    "Move content in and out of PDF with clearly documented fidelity limits.",
    ["Turn this PDF into Markdown.",
     "Convert these images into a PDF."],
    ["pdf-create", "pdf-export", "pdf-tables", "pdf-orchestrate"])

add("pdf-export", MGT,
    "Export PDF content/data",
    ["export text file", "export per-page", "export tables (csv/xlsx/json/md)",
     "export pages as images", "export full profile JSON"],
    "core.convert:convert_pdf + core.tables exporters + core.images render",
    "multiple exporters", "—",
    "output exists",
    "Ship PDF content out in the format the downstream consumer needs.",
    ["Export this report to Excel.",
     "Save all pages as PNGs."],
    ["pdf-convert", "pdf-tables", "pdf-create", "pdf-orchestrate"])

add("pdf-compare", MGT,
    "Compare two PDFs",
    ["page-count diff", "added/removed/modified pages", "text similarity per page",
     "metadata diff", "optional visual diff", "report output"],
    "core.compare:compare_pdfs / text_report",
    "PyMuPDF text + PIL visual", "difflib text similarity",
    "compared (both pages counted)",
    "Find what changed between versions.",
    ["Compare v1 and v2 of this contract.",
     "Diff these two PDFs and show me the changes."],
    ["pdf-inspect", "pdf-validation", "pdf-orchestrate"])

add("pdf-diff", MGT,
    "Page/text diff report",
    ["revision diff", "unified text change sample", "human-readable report"],
    "core.compare:compare_pdfs + text_report",
    "difflib", "—",
    "report produced",
    "Get a readable list of added/removed/modified content between two versions.",
    ["Show a readable diff of what changed."],
    ["pdf-compare", "pdf-orchestrate"])

add("pdf-images", MGT,
    "Embedded image operations",
    ["extract images", "inspect image resolution", "render page->image",
     "optimize image quality", "image-heavy page detection"],
    "core.images:extract_images / image_metadata / render_pages",
    "PyMuPDF pixmap + PIL", "—",
    "extracted count",
    "Pull or inspect the raster images inside a PDF.",
    ["Extract all embedded images.",
     "Which pages are image-heavy (scanned)?"],
    ["pdf-render", "pdf-ocr", "pdf-orchestrate"])

add("pdf-document-state", MGT,
    "Persistent per-document knowledge state",
    ["register documents", "store pages/chunks/tables/images/sections/metadata",
     "pipeline step status", "summaries", "validation & error log",
     "provenance anchor (document_id)"],
    "core.state:DocumentStore + core.provenance",
    "SQLite knowledge store", "—",
    "state persists; resumable",
    "Keep structured knowledge per PDF so later operations never re-parse.",
    ["Cache this document's structure for reuse.",
     "Resume processing from where it stopped."],
    ["pdf-chunk", "pdf-index", "pdf-provenance", "pdf-orchestrate"])

add("pdf-provenance", MGT,
    "Track source provenance",
    ["source path + content fingerprint", "page/section/chunk/object attribution",
     "extraction method + confidence", "document_id anchors"],
    "core.provenance:Provenance / anchor",
    "content fingerprinting", "—",
    "derived items carry source",
    "Every extracted/derived item keeps where it came from for trustworthy Q&A.",
    ["Cite the page for every answer you give me."],
    ["pdf-qa", "pdf-search", "pdf-document-state", "pdf-orchestrate"])

add("pdf-batch", MGT,
    "Batch operations over many PDFs",
    ["inspect many", "classify", "rename", "metadata", "compress", "convert",
     "index", "report", "never holds every doc in context"],
    "registry/batch spec + core modules (streamed per-file)",
    "per-file engine calls + checkpointing", "—",
    "per-file success/failure tracked; aggregate report",
    "Run pipelines over folders of PDFs without loading them all at once.",
    ["Process all 100 invoices in this folder: compress, OCR, index."],
    ["pdf-orchestrate", "pdf-document-state", "pdf-validation"])

add("pdf-validation", MGT,
    "Validate PDF & operation outputs",
    ["openable", "page count", "renderability", "text coverage",
     "redaction leak check", "output sanity"],
    "core.validation + per-module Outcome.checks",
    "uniform ValidationCheck", "—",
    "named checks with pass/fail",
    "Prove an operation actually worked before trusting it.",
    ["Verify the merged PDF has 40 pages and opens."],
    ["pdf-inspect", "pdf-orchestrate", "pdf-compare"])

add("pdf-orchestrate", MGT,
    "Universal PDF Orchestrator (SYSTEM MODE)",
    ["parse a natural request into an intent", "choose and order the needed skills",
     "run individual mode or system mode", "produce a single report/artifact",
     "respect resource & capability limits"],
    "universal_pdf.orchestration:orchestrator (see ORCHESTRATION.md + dispatch registry)",
    "pluggable dispatch", "manual per-skill fallback",
    "each sub-op validated; final output openable",
    "Entry point that routes any request through the correct PDF skills.",
    ["Read this, summarize, and give citations.",
     "Merge, compress, and add a watermark."],
    ["pdf-create", "pdf-merge", "pdf-summarize", "pdf-search", "pdf-ocr", "pdf-redact"])


# -------------------------------------------------------------------------- docs
def write_skill(entry):
    d = SKILLS_DIR / entry["slug"]
    d.mkdir(parents=True, exist_ok=True)
    ops = "\n".join(f"- {o}" for o in entry["operations"])
    ex = "\n".join(f'  * "{e}"' for e in entry["examples"])
    rel = ", ".join("`" + r + "`" for r in entry["related"])
    fm = (
        f"---\n"
        f"name: {entry['slug']}\n"
        f"title: \"{entry['title']}\"\n"
        f"category: \"{entry['category']}\"\n"
        f"version: 1.0.0\n"
        f"engine: \"{entry['engine']}\"\n"
        f"preferred_tool: \"{entry['tools']}\"\n"
        f"fallback_tool: \"{entry['fallback']}\"\n"
        f"validation: \"{entry['validation']}\"\n"
        f"---\n"
    )
    body = f"""# {entry['title']}  (`{entry['slug']}`)

{entry['blurb']}

> Part of the **Universal PDF Management & Creation Skill Repository**.
> Category: **{entry['category']}**.
> Every skill is individually callable (INDIVIDUAL MODE) and may also be
> invoked automatically by the orchestrator (SYSTEM MODE).

## When to use
{entry['when']}

## Operations
{ops}

## Engine (what actually executes this)
`universal_pdf/{entry['engine']}`

All heavy lifting is done on disk / one page at a time by the shared engine —
never by loading the document into an LLM context.

## Tools & graceful degradation
- Preferred tool: **{entry['tools']}**
- Fallback: **{entry['fallback']}**

If the preferred backend is unavailable the skill transparently uses the
fallback or reports a documented limitation. It **never** reports success when
an operation did not actually happen.

## Validation (this skill attaches checks to its Outcome)
{entry['validation']}

## Related skills
{rel}

## Example requests it handles
{ex}

## Notes
{entry['extra'] or "Provenance: outputs cite their source page/section where relevant."}
"""
    (d / "SKILL.md").write_text(fm + body)


def main():
    SKILLS_DIR.mkdir(exist_ok=True)
    REG.mkdir(exist_ok=True)
    for e in S:
        write_skill(e)

    # registry JSON (machine readable)
    registry = {
        "schema": "universal-pdf-skill-registry/1.0",
        "generated": "regenerated by scripts/generate_skills.py",
        "skills": [
            {"slug": e["slug"], "title": e["title"], "category": e["category"],
             "operations": e["operations"], "engine": e["engine"],
             "preferred_tool": e["tools"], "fallback_tool": e["fallback"],
             "validation": e["validation"], "related": e["related"]}
            for e in S
        ],
    }
    (REG / "skills.json").write_text(json.dumps(registry, indent=2))

    # relationship graph
    edges = []
    for e in S:
        for r in e["related"]:
            edges.append({"from": e["slug"], "to": r})
    (REG / "dependency-graph.json").write_text(
        json.dumps({"nodes": [e["slug"] for e in S], "edges": edges}, indent=2))

    # skills INDEX.md
    cats = {}
    for e in S:
        cats.setdefault(e["category"], []).append(e)
    lines = ["# Skills Index\n",
             "The repository ships the following individually-callable skills. "
             "Each is backed by a real engine function (see its SKILL.md) and is "
             "registered with the Universal PDF Orchestrator.\n"]
    for cat in (CREATE, MGT):
        lines.append(f"\n## {cat}\n")
        for e in cats.get(cat, []):
            lines.append(f"- **`{e['slug']}`** — {e['title']}  ")
    (ROOT / "skills" / "INDEX.md").write_text("\n".join(lines))

    print(f"generated {len(S)} skills, registry, dependency graph, INDEX")


if __name__ == "__main__":
    main()
