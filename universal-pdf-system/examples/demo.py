#!/usr/bin/env python3
"""End-to-end demonstration of the Universal PDF System.

Writes outputs to a temp dir and cleans up (add --keep to persist into
examples/output so you can inspect the generated files).

Usage:
    python examples/demo.py [--keep]
"""
import json
import os
import shutil
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from universal_pdf.core import (create, inspect, extract, manipulate, annotate,
                                compress, tables, convert, search)
from universal_pdf.orchestration import orchestrator as orch


def main():
    keep = "--keep" in sys.argv
    work = (ROOT / "examples/output") if keep else Path(tempfile.mkdtemp())
    work.mkdir(parents=True, exist_ok=True)
    line = "=" * 64

    print(line); print("1) CREATE from a report template (JSON content)"); print(line)
    content = json.loads((ROOT / "templates/report-template.json").read_text())
    o = create.create_pdf({"output": str(work / "report.pdf"), "page_size": "a4",
                           "header": "Demo", "footer": "Universal PDF System",
                           "metadata": {"title": "Demo Report"}}, content)
    print("   ok=%s checks=%s" % (o.ok, [c.passed for c in o.checks]))
    report = str(work / "report.pdf")

    print(line); print("2) CREATE an invoice from a template"); print(line)
    inv = json.loads((ROOT / "templates/invoice-template.json").read_text())
    create.create_pdf({"output": str(work / "invoice.pdf")}, inv)
    print("   made", work / "invoice.pdf")

    print(line); print("3) MARKDOWN -> PDF"); print(line)
    create.create_from_markdown(str(ROOT / "templates/content/sample.md"),
                                str(work / "from_md.pdf"))

    print(line); print("4) INSPECT the report"); print(line)
    prof = inspect.inspect(report)
    print("   pages=%s size=%sB fonts=%s" % (
        prof.data["page_count"], prof.data["size_bytes"],
        len(prof.data["resources"]["fonts"])))

    print(line); print("5) SEARCH a phrase"); print(line)
    s = search.search_document(report, "Actions", mode="exact")
    print("   hits=%s pages_total=%s" % (s.data["total"], s.data["pages_total"]))

    print(line); print("6) EXTRACT TABLES -> XLSX"); print(line)
    tb = tables.extract_tables(report)
    print("   tables=%s" % tb.data["count"])
    x = tables.tables_to_xlsx(tb.data["tables"], str(work / "tables.xlsx"))
    print("   xlsx ok=%s" % x.ok)

    print(line); print("7) MERGE + WATERMARK + COMPRESS"); print(line)
    m = manipulate.merge_pdfs([report, str(work / "invoice.pdf")],
                              str(work / "bundle.pdf"))
    print("   merge ok=%s" % m.ok)
    annotate.add_watermark(str(work / "bundle.pdf"), str(work / "bundle_wm.pdf"),
                           text="DEMO")
    c = compress.compress_pdf(str(work / "bundle_wm.pdf"),
                              str(work / "bundle_final.pdf"),
                              profile="small_size")
    print("   compress saved %s%%" % c.data["saved_pct"])

    print(line); print("8) SYSTEM MODE (orchestrator routing)"); print(line)
    plan = orch.route("Summarize this PDF", [report])
    print("   plan:", [p["skill"] for p in plan])
    res = orch.handle_request("Summarize this PDF", [report])
    print("   success=%s" % res["success"])

    print(line); print("9) PDF -> Markdown"); print(line)
    convert.convert_pdf(report, str(work / "report.md"), "markdown")

    print(line)
    print("Demo complete.")
    if keep:
        print("Outputs kept in:", work)
    else:
        print("Outputs were written to a temp dir and removed. Re-run with "
              "--keep to keep them under examples/output.")
        shutil.rmtree(work, ignore_errors=True)


if __name__ == "__main__":
    main()
