# Universal PDF Management & Creation Skill Repository

A **complete, interconnected PDF skill ecosystem** that covers the whole PDF
lifecycle — *create → import → inspect → read → extract → OCR → analyze →
search → understand → edit → annotate → manipulate → merge → split → reorder →
convert → optimize → compress → secure → validate → generate → export*.

This is **not** one monolithic PDF skill and **not** a loose pile of
`SKILL.md` files. It is a modular, individually-callable, and orchestratable
system backed by one shared Python engine (`universal_pdf/`) with a tool
abstraction layer, graceful degradation, provenance, external document state,
and resumable large-document processing.

---

## What it is at a glance

```
                    UNIVERSAL PDF SYSTEM
                            │
             ┌──────────────┴──────────────┐
             │                             │
        PDF MANAGEMENT                PDF CREATION
             │                             │
     ┌───────┼────────┐             ┌──────┼──────┐
     │       │        │             │      │      │
   Read   Edit     Analyze       Generate Convert Export
     │       │        │             │      │      │
    OCR    Merge    Search         Docs   Data   Images
    Tables Split    Q&A
    Forms  Rotate   Compare
    Links  Secure   Summarize
    etc.   Repair   Index
             │
             └──────────────┬──────────────┘
                            ↓
                     VALIDATION
                            ↓
                    FINAL PDF OUTPUT
```

- **INDIVIDUAL MODE** — call any one skill directly (each lives in
  `skills/<name>/SKILL.md` and maps to a real engine function).
- **SYSTEM MODE** — call the Universal PDF Orchestrator, which routes a
  request to the correct sequence of skills and validates each step.

---

## Repository layout

```text
universal-pdf-system/
├── skills/                  # individually-callable skills (47 SKILL.md docs)
│   ├── INDEX.md
│   ├── UNIVERSAL_PDF.md     # the master orchestrator skill
│   ├── pdf-create/ pdf-read/ pdf-inspect/ pdf-extract/ pdf-ocr/
│   ├── pdf-render/ pdf-vision/ pdf-tables/ pdf-search/ pdf-index/
│   ├── pdf-chunk/ pdf-summarize/ pdf-qa/ pdf-analyze/ pdf-edit/
│   ├── pdf-annotate/ pdf-merge/ pdf-split/ pdf-reorder/ pdf-rotate/
│   ├── pdf-crop/ pdf-scale/ pdf-watermark/ pdf-header-footer/
│   ├── pdf-metadata/ pdf-bookmarks/ pdf-links/ pdf-forms/ pdf-fill-forms/
│   ├── pdf-sign/ pdf-encrypt/ pdf-decrypt/ pdf-permissions/ pdf-redact/
│   ├── pdf-compress/ pdf-optimize/ pdf-repair/ pdf-convert/ pdf-export/
│   ├── pdf-compare/ pdf-diff/ pdf-images/ pdf-batch/ pdf-document-state/
│   ├── pdf-provenance/ pdf-validation/ pdf-orchestrate/
│   └── ...
├── universal_pdf/           # the shared Python engine
│   ├── core/                # 20+ operational modules (the real work)
│   ├── tools/               # tool-abstraction layer (PyMuPDF/pdfplumber/pypdf…)
│   └── orchestration/       # Universal PDF Orchestrator (SYSTEM MODE)
├── registry/                # skills.json, dependency-graph.json, config.json
├── workflows/               # reusable end-to-end workflow docs
├── templates/               # document / content templates
├── examples/                # runnable examples + scripts
├── knowledge/               # persistent per-document SQLite state (created at runtime)
├── tests/                   # pytest suite + orchestration tests
├── scripts/                 # generate_skills.py, install deps, fixtures
├── docs/                    # architecture, dependencies, limitations, install/usage
├── INDEX.md  MANIFEST.md  ARCHITECTURE.md  DEPENDENCIES.md  LIMITATIONS.md
└── README.md (this file)
```

---

## The four layers (read in order)

1. **[ARCHITECTURE.md](ARCHITECTURE.md)** — how the system is layered and how
   the lifecycle maps onto skills and engine modules.
2. **[skills/INDEX.md](skills/INDEX.md)** — every skill with one-line summary.
3. **[MANIFEST.md](MANIFEST.md)** — what is present, what is real, provenance
   of the design.
4. **[docs/INSTALL.md](docs/INSTALL.md)**, **[docs/USAGE.md](docs/USAGE.md)**,
   **[DEPENDENCIES.md](DEPENDENCIES.md)**, **[LIMITATIONS.md](LIMITATIONS.md)**.

---

## Quick start

```bash
# 1) install python deps (see DEPENDENCIES.md; minimum is pymupdf+reportlab)
pip install pymupdf reportlab pypdf pdfplumber openpyxl pillow

# 2) regenerate the skill docs / registry (optional, after edits to the model)
python scripts/generate_skills.py

# 3) run the test suite
python -m pytest tests/ -q

# 4) try the engine or the orchestrator directly
python scripts/demo.py
```

---

## Design guarantees

- **Small/local model friendly**: no document is loaded wholesale into an LLM
  context. Pages stream one at a time; chunking, external index, hierarchical
  summaries and retrieval feed only what the current step needs.
- **Huge PDFs (1–10,000+ pages)**: streaming extraction/search, persistent
  knowledge store, resumable checkpoints (`pending/processing/completed/
  failed/retry/validated`).
- **Resource-aware**: a strategy is chosen per document + host before heavy
  work (`universal_pdf/core/resource.py`).
- **Tool abstraction + graceful degradation**: if a backend or capability is
  missing, a fallback runs or a limitation is reported — success is never
  faked.
- **Provenance**: derived items cite source doc/page/section/method.
- **Validation**: every major operation attaches named checks to its
  `Outcome` (page counts, coverage, redaction leak checks, openability…).

---

## License / use

Legitimate PDF management only. Security capabilities (encryption, permissions,
redaction, signatures) must be used only on documents you own or are authorized
to process. Redaction performs **true content removal** and verifies it.
