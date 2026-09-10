# Architecture

The Universal PDF System is a three-layer design that keeps *intent* (what the
user/agent wants), *capability* (an individual skill), and *execution* (the
shared engine) decoupled yet fully connected.

```
┌────────────────────────────────────────────────────────────────────────┐
│ L1  ORCHESTRATION  (SYSTEM MODE)                                       │
│   skills/UNIVERSAL_PDF.md  +  universal_pdf/orchestration/orchestrator  │
│   route(request) -> plan(ordered steps) -> execute each -> validate     │
└───────────────┬────────────────────────────────────────────────────────┘
                │ INDIVIDUAL MODE also allowed (call one skill directly)
┌───────────────▼────────────────────────────────────────────────────────┐
│ L2  SKILL LAYER  (47 skills in skills/<slug>/SKILL.md)                 │
│   Each declares: name, category, operations, engine fn, preferred/     │
│   fallback tool, validation, related skills, example requests.         │
│   Registry: registry/skills.json · graph: registry/dependency-graph.json│
└───────────────┬────────────────────────────────────────────────────────┘
┌───────────────▼────────────────────────────────────────────────────────┐
│ L3  ENGINE  (universal_pdf/core/*) + TOOL ABSTRACTION (universal_pdf/   │
│     tools)                                                              │
│   concrete PDF libraries behind one interface; fallback on absence;     │
│   external state (knowledge store, indexes, checkpoints) for huge docs. │
└────────────────────────────────────────────────────────────────────────┘
```

## Layer 1 — Orchestration

The orchestrator (`universal_pdf/orchestration/orchestrator.py`) provides:

- `route(request, files)` → a **plan**: an ordered list of step dicts
  (`{"skill": "pdf-compress", "path": …, "output": …}`).
- `execute_plan(plan)` → executes each step, catching errors, timing it, and
  returning every step's serialized `Outcome`.
- `execute_step(step)` → the executor bound to each skill name (the individual
  skills remain callable by an agent directly — **no forced pipeline**).

The human-readable master skill is `skills/UNIVERSAL_PDF.md`. It teaches an
agent how to reason about a request, which skills to chain, and how to respect
capability limits (vision/OCR availability, model context, resource usage).

### Example routing
| Request | Plan |
|---|---|
| “Read this PDF.” | `pdf-inspect` → `pdf-read` |
| “Summarize this book.” | `pdf-inspect` → `pdf-summarize` |
| “Find every mention of X.” | `pdf-inspect` → `pdf-search` |
| “Turn this PDF into Excel.” | `pdf-tables` → export xlsx |
| “Merge these PDFs.” | `pdf-merge` |
| “Remove pages 4,7,9.” | `pdf-edit` (delete) |
| “Compress this PDF.” | `pdf-compress` |
| “OCR this scanned doc.” | `pdf-inspect` → `pdf-ocr` |
| “Compare these two PDFs.” | `pdf-compare` |
| “Redact these details.” | `pdf-redact` |

## Layer 2 — Skills

Every skill is documented under `skills/` and is:

- **Meaningful** — backed by at least one real engine function (never a stub).
- **Individually callable** — an agent can invoke exactly the capability needed.
- **Interconnected** — `related` lists point to the skills a request commonly
  composes.

### Skill grouping by lifecycle
- **Create**: `pdf-create`
- **Consume / inspect / understand**: `pdf-read`, `pdf-inspect`, `pdf-extract`,
  `pdf-ocr`, `pdf-render`, `pdf-vision`, `pdf-tables`, `pdf-search`,
  `pdf-index`, `pdf-chunk`, `pdf-summarize`, `pdf-qa`, `pdf-analyze`
- **Manipulate**: `pdf-edit`, `pdf-annotate`, `pdf-merge`, `pdf-split`,
  `pdf-reorder`, `pdf-rotate`, `pdf-crop`, `pdf-scale`, `pdf-watermark`,
  `pdf-header-footer`, `pdf-images`
- **Structure/metadata**: `pdf-metadata`, `pdf-bookmarks`, `pdf-links`,
  `pdf-forms`, `pdf-fill-forms`
- **Secure**: `pdf-encrypt`, `pdf-decrypt`, `pdf-permissions`, `pdf-sign`,
  `pdf-redact`
- **Optimize/repair**: `pdf-compress`, `pdf-optimize`, `pdf-repair`
- **Convert/export**: `pdf-convert`, `pdf-export`
- **Compare/validate**: `pdf-compare`, `pdf-diff`, `pdf-validation`
- **State/provenance**: `pdf-document-state`, `pdf-provenance`
- **Batch/orchestrate**: `pdf-batch`, `pdf-orchestrate`

## Layer 3 — Engine and tool abstraction

`universal_pdf/core/` contains the real code behind the skills:

| Module | Provides |
|---|---|
| `create.py` | PDF generation (text/MD/HTML/images/data/reports/invoices/templates) |
| `inspect.py`, `extract.py` | structured profile & universal text extraction (streaming) |
| `ocr.py` | OCR need-detection, searchable layers, graceful degradation |
| `render.py→images.py` | page rasterisation, embedded-image ops |
| `tables.py` | table detect/extract + CSV/XLSX/JSON/Markdown export |
| `search.py`, `chunk.py`, `index` | search, chunking, external index |
| `summarize.py`, `qa.py` | context-safe summaries & retrieval-grounded Q&A |
| `manipulate.py` | merge/split/reorder/rotate/crop/scale/insert/delete |
| `annotate.py` | watermark/stamp/header/footer/annotations/**true redaction** |
| `meta.py`, `bookmarks.py` | metadata + outline/hyperlinks |
| `forms.py` | AcroForm detect/fill/extract/flatten |
| `security.py` | encrypt/decrypt/permissions/signature |
| `compress.py` | optimization profiles |
| `repair.py` | diagnose & best-effort repair |
| `convert.py` | PDF → TXT/MD/HTML/JSON/Images/CSV/XLSX/DOCX |
| `compare.py` | comparison & diff reports |
| `state.py` | persistent per-document knowledge store (SQLite) |
| `provenance.py` | source attribution + content fingerprints |
| `checkpoint.py` | resumable multi-unit processing |
| `resource.py`, `validation.py`, `config.py` | strategy, checks, profiles |

`universal_pdf/tools/` is the abstraction seam: it probes available libraries
(PyMuPDF preferred; pdfplumber for layout; pypdf for pure-structural/crypto;
reportlab for creation) and selects a fallback automatically.

## Dependency graph (high level)

```
PDF Ingestion / open  ───────────────────────────►  Tool abstraction (tools/)
      │
      ▼
PDF Inspection (inspect) ──► Extraction ─┬─► OCR (ocr)      ◄── degradation
      │                                  ├─► Vision (vision) ◄── degradation
      │                                  └─► Tables (tables)
      │                                        │
      ▼                                        ▼
   Normalization ──► Chunking ──► Indexing ──► Retrieval ──► Reasoning / Q&A
      │                                                      │
      ▼                                                      ▼
   External state (state.py, knowledge/)      Output / Creation / Transformation
   + checkpoints for huge docs                (create, convert, manipulate…)
                                                    │
                                                    ▼
                                               Validation
```

Machine-readable edges live in `registry/dependency-graph.json`.

## How the design meets the hard requirements
- **Huge & weak-model**: streaming extractors, chunk budgets, external index,
  hierarchical summaries, retrieval-grounded QA → only needed context enters a
  prompt (see `docs/DESIGN-NOTES.md`).
- **Graceful degradation**: every capability gap is translated into a
  `degraded`/`failed` Outcome with a message — never a fabricated success.
- **Validation**: each engine call appends named `ValidationCheck`s to its
  `Outcome`; orchestrator surfaces them per step.
