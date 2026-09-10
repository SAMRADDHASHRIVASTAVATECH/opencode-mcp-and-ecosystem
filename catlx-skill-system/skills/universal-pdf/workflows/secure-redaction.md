# Workflow: Secure redaction & safe publishing

**Goal:** remove sensitive content so it cannot be copied/selected, strip
metadata, verify, then publish a clean copy.

**Skills:** `pdf-inspect` → `pdf-search` (find all occurrences) → `pdf-redact` →
`pdf-metadata` → `pdf-validation`.

## Steps
1. Find what to remove: run `pdf-search` for each sensitive term to see page
   coverage. Also list regions to wipe (signatures, account numbers).
2. **Redact with true removal** (not a black box over text):
   - term redaction via `redact_text(terms=[...])`
   - plus region redaction `rects=[{"page":p,"rect":[...]}]`
   - `remove_metadata=True` strips document properties.
3. **Verify**: `pdf-redact` runs a leak check (the terms must no longer be
   extractable). Assert `checks[0].passed`.
4. Re-open and eyeball render; then publish.

## Concrete calls
```python
from universal_pdf.core import annotate, search

search.search_document("doc.pdf", "ACME-7788", mode="exact")  # coverage
o = annotate.redact_text("doc.pdf", "clean.pdf",
                         terms=["ACME-7788", "1234-5678", "confidential"],
                         rects=[{"page": 1, "rect": [40, 40, 300, 90]}],
                         remove_metadata=True)
assert o.ok
assert o.checks[0].passed is True, o.data["leaked_terms"]
# confirm clean copy opens and leaks nothing
from universal_pdf.core import extract
all_text = " ".join(extract.extract_per_page("clean.pdf")).lower()
assert "acme-7788" not in all_text
```

## Caution
- Redaction removes *underlying* content wherever the tooling supports true
  removal (PyMuPDF `apply_redactions`) and then verifies. Complex overlapping
  vector content is the documented edge case; trust the leak check.
- For binary-authoritative sanitisation beyond this, add a dedicated
  sanitisation pass (e.g. via ghostscript) — documented as an enhancement.
