# Workflow: Merge → watermark → compress (delivery bundle)

**Goal:** combine several PDFs, mark them, and shrink the result for delivery.

**Skills:** `pdf-merge` → `pdf-watermark`/`pdf-header-footer` → `pdf-compress`.

## Concrete calls
```python
from universal_pdf.core import manipulate, annotate, compress, inspect

merged = "bundle.pdf"
r = manipulate.merge_pdfs(["a.pdf", "b.pdf", "c.pdf"], merged)
assert r.ok and r.checks[0].passed            # page_count == sum

r = annotate.add_watermark(merged, "bundle_wm.pdf", text="CONFIDENTIAL",
                           opacity=0.18, rotation=45)
assert r.ok

r = compress.compress_pdf("bundle_wm.pdf", "bundle_final.pdf",
                          profile="web_optimized")
print("saved %", r.data["saved_pct"])
assert inspect.inspect("bundle_final.pdf").data["page_count"] == \
       inspect.inspect(merged).data["page_count"]
```

## Tips
- Choose the compress profile by destination:
  email/web → `small_size` or `web_optimized`; archive → `archive_optimized`;
  print → `maximum_quality`/`balanced`.
- Watermark before compressing so the overlay is included in size savings.
- Validate the final page count matches the source after every step.
