# Installation / import

## Import into another skill environment
The whole repository is **standalone and portable**. Copy (or git-clone) the
`universal-pdf-system/` directory anywhere. There is no global install step —
the Python engine is importable relative to the repo root:

```python
import sys
sys.path.insert(0, "/path/to/universal-pdf-system")
from universal_pdf.core import inspect          # individual engine call
from universal_pdf.orchestration import orchestrator   # SYSTEM MODE
```

For a skill/agent runtime, make each `skills/<slug>/SKILL.md` available as a
normal skill; the agent reads the `SKILL.md`, then calls the documented engine
function. The orchestrator skill (`skills/UNIVERSAL_PDF.md`) binds it all.

## Install Python dependencies
```bash
pip install pymupdf reportlab pypdf pdfplumber pillow   # core
pip install openpyxl python-docx pytest                  # optional/dev
# OCR (optional, for searchable scanned PDFs)
pip install ocrmypdf        # needs tesseract + ghostscript on PATH
```

You can also run `python scripts/install_deps.py`.

## Optional engines
`ocrmypdf`, `tesseract`, `pandoc`, `ghostscript`, `qpdf` are auto-detected. If
they are missing the affected skills degrade with an explicit message (see
`LIMITATIONS.md` and `docs/DESIGN-NOTES.md`).

## Configuration
Runtime knobs come from `registry/config.json` and/or environment variables
(`UPPDF_*`), e.g.:
```bash
export UPPDF_LLM_CONTEXT_CHARS=8000     # keep small for weak models
export UPPDF_PAGE_BATCH=15
export UPPDF_OCR=1                      # advertise OCR capability
export UPPDF_VISION=1                   # advertise a vision provider is wired
```
See `universal_pdf/config.py` for all keys.

## Regenerate skills / registry (developer only)
The 47 `SKILL.md` files, `registry/skills.json`, `registry/dependency-graph.json`
and the capability matrix are generated from one model:
```bash
python scripts/generate_skills.py
python scripts/generate_docs.py
```

## Test it
```bash
python -m pytest tests/ -q
```
