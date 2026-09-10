# Capabilities Matrix

Every skill, its category, its real engine module, preferred tool, validation and supported operations. Generated from registry/skills.json.


| Skill | Category | Engine module | Preferred tool | Validation |
|---|---|---|---|---|
| `pdf-create` | PDF Creation | core.create | reportlab platypus (vector, templated) | openable; page_count>=1; metadata valid; pages render |
| `pdf-read` | PDF Management | core.extract | PyMuPDF text layer | text_coverage; page coverage |
| `pdf-inspect` | PDF Management | core.inspect | PyMuPDF | openable; page_count>0 |
| `pdf-extract` | PDF Management | core.extract | PyMuPDF text (text/dict) | text_coverage; page coverage |
| `pdf-ocr` | PDF Management | core.ocr | ocrmypdf (add searchable layer) | OCR completeness; output openable |
| `pdf-render` | PDF Management | core.images | PyMuPDF pixmap | rendered file count; each opens |
| `pdf-vision` | PDF Management | core.vision | pluggable vision provider (agent/LLM) | description returned when provider present |
| `pdf-tables` | PDF Management | core.tables | pdfplumber layout extraction | extracted>0; each export written; column consistency |
| `pdf-search` | PDF Management | core.search | PyMuPDF text layer streaming | searched; hits carry page |
| `pdf-index` | PDF Management | core.search | positional inverted index (JSON) | indexed terms > 0 |
| `pdf-chunk` | PDF Management | core.chunk | local chunker (page & word boundaries) | chunks>=1 |
| `pdf-summarize` | PDF Management | core.summarize | local extractive engine | summarized; output within configured context size |
| `pdf-qa` | PDF Management | core.qa | retrieval over index/chunks | answer grounded in retrieved pages |
| `pdf-analyze` | PDF Management | core.inspect + core.resource | PyMuPDF + resource-aware strategy | profile produced |
| `pdf-edit` | PDF Management | core.manipulate | PyMuPDF reconstruction | page_count matches expectation |
| `pdf-annotate` | PDF Management | core.annotate | PyMuPDF annotation API | added>=0 |
| `pdf-merge` | PDF Management | core.manipulate | PyMuPDF insert_pdf | page_count == sum of inputs |
| `pdf-split` | PDF Management | core.manipulate | PyMuPDF | produced file count |
| `pdf-reorder` | PDF Management | core.manipulate | PyMuPDF | page_count == len(order) |
| `pdf-rotate` | PDF Management | core.manipulate | PyMuPDF set_rotation | page_count preserved |
| `pdf-crop` | PDF Management | core.manipulate | PyMuPDF set_cropbox/mediabox | page_count preserved |
| `pdf-scale` | PDF Management | core.manipulate | PyMuPDF page rebuild | page_count preserved |
| `pdf-watermark` | PDF Management | core.annotate | reportlab overlay + PyMuPDF stamping | page_count preserved; overlay renders |
| `pdf-header-footer` | PDF Management | core.annotate | PyMuPDF insert_text | page_count preserved |
| `pdf-metadata` | PDF Management | core.meta | PyMuPDF set_metadata | metadata round-trips (verify after write) |
| `pdf-bookmarks` | PDF Management | core.bookmarks | PyMuPDF get_toc/set_toc | TOC present after set |
| `pdf-links` | PDF Management | core.bookmarks | PyMuPDF links | parsed/added |
| `pdf-forms` | PDF Management | core.forms | PyMuPDF widget API | fields enumerated |
| `pdf-fill-forms` | PDF Management | core.forms | PyMuPDF widget update | each requested field filled |
| `pdf-sign` | PDF Management | core.security | PyMuPDF widget/image placement | signature placed; clearly reported as visual unless crypto infra used |
| `pdf-encrypt` | PDF Management | core.security | PyMuPDF encryption | output is_encrypted |
| `pdf-decrypt` | PDF Management | core.security | PyMuPDF | output not encrypted (when requested) |
| `pdf-permissions` | PDF Management | core.security | PyMuPDF permissions | flags reported / applied |
| `pdf-redact` | PDF Management | core.annotate | PyMuPDF redact annots + apply_redactions | underlying_content_removed (leak check passes) |
| `pdf-compress` | PDF Management | core.compress | PyMuPDF rewrite_images + garbage/deflate | openable; final_size <= original |
| `pdf-optimize` | PDF Management | core.compress | PyMuPDF | openable; size reported per profile |
| `pdf-repair` | PDF Management | core.repair | PyMuPDF re-save (garbage) | openable after repair; recovered page count reported |
| `pdf-convert` | PDF Management | core.convert | text/tables/render engines | output exists; renderable; sanity |
| `pdf-export` | PDF Management | core.convert | multiple exporters | output exists |
| `pdf-compare` | PDF Management | core.compare | PyMuPDF text + PIL visual | compared (both pages counted) |
| `pdf-diff` | PDF Management | core.compare | difflib | report produced |
| `pdf-images` | PDF Management | core.images | PyMuPDF pixmap + PIL | extracted count |
| `pdf-document-state` | PDF Management | core.state | SQLite knowledge store | state persists; resumable |
| `pdf-provenance` | PDF Management | core.provenance | content fingerprinting | derived items carry source |
| `pdf-batch` | PDF Management | registry/batch spec + core modules (streamed per-file) | per-file engine calls + checkpointing | per-file success/failure tracked; aggregate report |
| `pdf-validation` | PDF Management | core.validation + per-module Outcome.checks | uniform ValidationCheck | named checks with pass/fail |
| `pdf-orchestrate` | PDF Management | universal_pdf.orchestration | pluggable dispatch | each sub-op validated; final output openable |


### `pdf-create`

- plain text
- Markdown (subset)
- HTML (subset)
- images
- structured rows
- reports
- invoices
- cover pages
- tables
- lists
- headings
- headers/footers
- page numbers
- bookmarks
- metadata
- TOC placeholder

### `pdf-read`

- read full text
- read selected pages
- read preserving page boundaries
- stream huge documents page-by-page
- detect whether OCR needed

### `pdf-inspect`

- page count
- page size/orientation
- metadata
- fonts
- image count
- links
- annotations
- forms present
- encryption/permissions
- PDF version
- embedded files
- text layer health

### `pdf-extract`

- extract text
- per-page blocks with bbox
- multi-column via layout
- preserve page/position info
- image-only pages routed to OCR

### `pdf-ocr`

- detect when OCR needed
- make scanned pages searchable
- page-level recognition
- language selection
- skip already-text pages
- graceful degradation when no OCR engine

### `pdf-render`

- render page(s) to PNG/JPG
- custom DPI
- page subset
- single-page raster for vision/OCR pre-pass

### `pdf-vision`

- describe a rendered page
- interpret charts/graphs/diagrams/forms
- graceful fallback to text/OCR when no vision model

### `pdf-tables`

- extract tables
- header/rows reconstruction
- multi-page tables
- to CSV
- to XLSX
- to JSON
- to Markdown
- column-consistency validation

### `pdf-search`

- exact/phrase search
- keyword search
- regex search
- single-page search
- whole-document mention scan (streamed)
- source page in every result

### `pdf-index`

- positional term index
- page-level inverted index
- persisted JSON
- reuse across queries without re-parsing

### `pdf-chunk`

- chunk by page
- chunk by max chars w/ overlap
- persist chunks + page text
- only the needed chunks are ever passed to the model

### `pdf-summarize`

- extractive summary
- bucket summaries for huge docs
- hierarchical summary
- persist to knowledge store
- optional abstractive via injected LLM

### `pdf-qa`

- locate relevant pages/chunks
- extract evidence with provenance
- compose an answer from context only
- no document in the model context

### `pdf-analyze`

- statistical profile
- structure & resource analysis
- text-layer health
- routing hints (OCR? huge? tables?)

### `pdf-edit`

- insert pages
- delete pages
- replace pages (delete+insert)
- add blank pages
- add images to a page

### `pdf-annotate`

- highlight
- underline
- strikeout
- text note
- free text
- square/circle
- line/arrow
- link
- preserve existing annotations

### `pdf-merge`

- merge N PDFs in order
- preserve bookmarks with page offsets

### `pdf-split`

- split every N pages
- split into ranges
- split at TOC top-level
- extract selected pages

### `pdf-reorder`

- arbitrary order
- reverse
- duplicate
- subset ordering

### `pdf-rotate`

- rotate 90/180/270
- selected pages
- preserve text/orientation metadata

### `pdf-crop`

- uniform margin crop
- asymmetric insets
- selected pages

### `pdf-scale`

- uniform scale factor
- set page size
- selected pages

### `pdf-watermark`

- diagonal text watermark (arbitrary angle)
- image watermark
- opacity
- page selection
- stamp overlays (APPROVED/CONFIDENTIAL)

### `pdf-header-footer`

- running header
- running footer
- page numbers
- skip first page
- start number
- page selection

### `pdf-metadata`

- read title/author/subject/keywords/creator/producer/dates
- write fields
- strip all metadata
- batch update

### `pdf-bookmarks`

- extract TOC
- set/merge/remove outline
- TOC entries link to pages

### `pdf-links`

- extract links (URI/page/rect)
- add URI links
- inspect link targets

### `pdf-forms`

- detect form
- list fields+types+values
- extract data
- flatten values into content

### `pdf-fill-forms`

- fill by field name
- text/checkbox/radio/list
- optional flatten

### `pdf-sign`

- inspect signature fields
- place a visible signature image/text

### `pdf-encrypt`

- AES-128/256
- user + owner passwords
- permission flags (print/modify/copy/annotate)

### `pdf-decrypt`

- open with password
- save unencrypted copy
- legitimate access workflows

### `pdf-permissions`

- read permission flags
- set permissions while encrypting

### `pdf-redact`

- text-term redaction
- region redaction
- page-level
- metadata cleanup
- post-redaction leak verification

### `pdf-compress`

- structural cleanup
- image recompression
- reported savings
- quality/size profiles

### `pdf-optimize`

- maximum_quality
- balanced
- small_size
- web_optimized
- archive_optimized
- never silently destroy quality

### `pdf-repair`

- openability probe
- page-tree health
- renderability
- rebuild xrefs
- per-page rescue
- report unrecovered content

### `pdf-convert`

- PDF->TXT
- PDF->Markdown
- PDF->HTML
- PDF->JSON
- PDF->Images
- PDF->CSV/XLSX (tables)
- PDF->DOCX (when pandoc present)
- TXT/MD/HTML/Images->PDF

### `pdf-export`

- export text file
- export per-page
- export tables (csv/xlsx/json/md)
- export pages as images
- export full profile JSON

### `pdf-compare`

- page-count diff
- added/removed/modified pages
- text similarity per page
- metadata diff
- optional visual diff
- report output

### `pdf-diff`

- revision diff
- unified text change sample
- human-readable report

### `pdf-images`

- extract images
- inspect image resolution
- render page->image
- optimize image quality
- image-heavy page detection

### `pdf-document-state`

- register documents
- store pages/chunks/tables/images/sections/metadata
- pipeline step status
- summaries
- validation & error log
- provenance anchor (document_id)

### `pdf-provenance`

- source path + content fingerprint
- page/section/chunk/object attribution
- extraction method + confidence
- document_id anchors

### `pdf-batch`

- inspect many
- classify
- rename
- metadata
- compress
- convert
- index
- report
- never holds every doc in context

### `pdf-validation`

- openable
- page count
- renderability
- text coverage
- redaction leak check
- output sanity

### `pdf-orchestrate`

- parse a natural request into an intent
- choose and order the needed skills
- run individual mode or system mode
- produce a single report/artifact
- respect resource & capability limits