# Workflow: Professional report creation

**Goal:** turn text + data into a clean multi-section PDF with a cover, TOC-ish
headings, tables, header/footer and metadata.

**Skills:** `pdf-create` (+ `pdf-export` to produce the input data if needed).

## Steps
1. Gather content: body text (paragraphs/headings/lists), tabular data
   (list of dicts or a JSON/CSV file), optional images.
2. Build a content-flowable list and call `create_pdf`.
3. Add metadata (title/author/keywords) so the file is self-describing.
4. Validate: openable, page_count ≥ 1, metadata present.

## Concrete calls
```python
from universal_pdf.core import create, inspect

rows = [{"Region":"North","Q1":120,"Q2":135}, {"Region":"South","Q1":90,"Q2":110}]
content = [
  {"type":"cover","title":"Quarterly Business Review","subtitle":"FY26 Q2",
   "author":"Finance","date":"2026-09-06"},
  {"type":"heading","text":"1. Overview","level":1},
  {"type":"para","text":"Quarterly performance remained strong..."},
  {"type":"heading","text":"2. Revenue by region","level":2},
  {"type":"table","rows":[["Region","Q1","Q2"]]+
   [[r["Region"],r["Q1"],r["Q2"]] for r in rows]},
  {"type":"heading","text":"3. Outlook","level":1},
  {"type":"list","items":["Expand APAC","Harden security"],"ordered":True},
]
o = create.create_pdf({"output":"report.pdf","page_size":"a4",
                       "header":"ACME · QBR","footer":"Internal",
                       "metadata":{"title":"QBR FY26 Q2","author":"Finance",
                                   "subject":"Quarterly review","keywords":"qbr,fy26"}},
                      content)
assert o.ok and o.all_checks_passed()
p = inspect.inspect("report.pdf"); print(p.data["metadata"]["title"])
```

### Variants
- `create_from_markdown("notes.md","notes.pdf")`
- `create_from_html("web.html","web.pdf")` (documented HTML subset)
- `create_from_images(["1.png","2.png"],"scan.pdf")`
- `create_report_from_rows(rows, columns, "table.pdf", title="Data")`
