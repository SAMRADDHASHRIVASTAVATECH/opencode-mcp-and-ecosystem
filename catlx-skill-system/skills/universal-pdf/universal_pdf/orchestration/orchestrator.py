"""Universal PDF Orchestrator (requirement 29, 30).

SYSTEM MODE: route a natural-language-ish request to the correct sequence of
individual skills and execute them in order, validating each step. Every skill
remains individually callable (INDIVIDUAL MODE) — this module only *composes*
them.

Routing is deterministic and keyword/plan based so it works without an LLM.
An agent may instead read ``skills/UNIVERSAL_PDF.md`` and build a plan, then
hand it to :func:`execute_plan`.

Each step produces an Outcome with validation checks. The orchestrator never
loads a whole huge document into any LLM context.
"""
from __future__ import annotations

import os
import time
from dataclasses import dataclass, field
from typing import Optional

from ..result import Outcome
from ..core import (create, inspect, extract, manipulate, annotate, meta,
                    bookmarks, security, forms, images, compress, tables,
                    search, chunk, summarize, convert, compare, repair,
                    qa, ocr, vision, state, provenance)
from .. import config


@dataclass
class SkillSpec:
    name: str
    group: str          # "create" | "read" | "edit" | "secure" | "convert" | "analyze"
    params: dict
    describe: str = ""


# --------------------------------------------------------------------- registry
AVAILABLE_SKILLS: dict[str, SkillSpec] = {}


def _reg(name, group, params, describe):
    AVAILABLE_SKILLS[name] = SkillSpec(name, group, params, describe)


_reg("pdf-create", "create", {"output": None}, "create a new PDF")
_reg("pdf-inspect", "read", {}, "profile a document")
_reg("pdf-read", "read", {}, "extract text (streaming)")
_reg("pdf-extract", "read", {}, "structured extract")
_reg("pdf-ocr", "read", {"make_searchable": False}, "OCR scanned pages")
_reg("pdf-render", "read", {"output": None}, "pages -> images")
_reg("pdf-tables", "read", {}, "extract tables")
_reg("pdf-search", "analyze", {}, "search terms/phrases")
_reg("pdf-index", "analyze", {}, "build an index")
_reg("pdf-chunk", "analyze", {}, "chunk a document")
_reg("pdf-summarize", "analyze", {}, "summarize")
_reg("pdf-qa", "analyze", {}, "question answering")
_reg("pdf-merge", "edit", {"inputs": None, "output": None}, "merge PDFs")
_reg("pdf-split", "edit", {"output": None}, "split a PDF")
_reg("pdf-reorder", "edit", {"output": None}, "reorder pages")
_reg("pdf-edit", "edit", {"output": None}, "page insert/delete")
_reg("pdf-rotate", "edit", {"output": None}, "rotate pages")
_reg("pdf-crop", "edit", {"output": None}, "crop pages")
_reg("pdf-scale", "edit", {"output": None}, "scale pages")
_reg("pdf-watermark", "edit", {"output": None}, "watermark/stamp")
_reg("pdf-header-footer", "edit", {"output": None}, "headers/footers/numbers")
_reg("pdf-annotate", "edit", {"output": None}, "annotations")
_reg("pdf-metadata", "edit", {"output": None}, "metadata ops")
_reg("pdf-bookmarks", "edit", {"output": None}, "outline ops")
_reg("pdf-links", "edit", {"output": None}, "links ops")
_reg("pdf-forms", "read", {}, "forms inspect")
_reg("pdf-fill-forms", "edit", {"output": None}, "fill a form")
_reg("pdf-encrypt", "secure", {"output": None}, "encrypt")
_reg("pdf-decrypt", "secure", {"output": None}, "decrypt")
_reg("pdf-permissions", "secure", {}, "permission flags")
_reg("pdf-sign", "secure", {"output": None}, "signature placement/inspect")
_reg("pdf-redact", "secure", {"output": None}, "true redaction")
_reg("pdf-compress", "convert", {"output": None}, "compress")
_reg("pdf-optimize", "convert", {"output": None}, "optimize (profiles)")
_reg("pdf-repair", "convert", {"output": None}, "repair/diagnose")
_reg("pdf-convert", "convert", {"output": None}, "format conversion")
_reg("pdf-export", "convert", {"output": None}, "export content")
_reg("pdf-compare", "analyze", {}, "compare two PDFs")
_reg("pdf-diff", "analyze", {}, "readable diff")
_reg("pdf-validation", "read", {}, "validation checks")


# -------------------------------------------------------------- intent routing
# request-fragment -> pipeline builder. Lowercase keywords.
def route(request: str, files: Optional[list] = None) -> list[dict]:
    """Return a plan (list of step dicts) for a request.

    Files is a list of input paths used to fill ``inputs``/``path``.
    If routing is ambiguous it returns a minimal reasonable plan and the caller
    may inspect it before executing.
    """
    files = files or []
    r = request.lower()

    def one(path=None, **extra):
        return path

    plans = []

    def _out(name, base):
        # deterministic output path next to first input
        d = os.path.dirname(os.path.abspath(base))
        return os.path.join(d, f"{name}.pdf")

    # ---- reading / analysis -------------------------------------------------
    if "ocr" in r:
        return [{"skill": "pdf-inspect", "path": _p0(files)},
                {"skill": "pdf-ocr", "path": _p0(files), "output": _out("ocr", _p0(files))}]
    if any(w in r for w in ["read", "show me", "text of", "tell me about",
                            "what does it say"]):
        plan = [{"skill": "pdf-inspect", "path": _p0(files)}]
        if "summar" not in r:
            plan.append({"skill": "pdf-read", "path": _p0(files)})
        if "summar" in r or "main points" in r or "about" in r:
            plan.append({"skill": "pdf-summarize", "path": _p0(files)})
        return plan
    if "summar" in r:
        return [{"skill": "pdf-inspect", "path": _p0(files)},
                {"skill": "pdf-summarize", "path": _p0(files)}]
    if any(w in r for w in ["table", "excel", "spreadsheet", "xlsx", "csv"]):
        steps = [{"skill": "pdf-tables", "path": _p0(files)}]
        if "excel" in r or "xlsx" in r:
            steps.append({"skill": "pdf-tables", "path": _p0(files),
                          "export": "xlsx"})
        elif "csv" in r:
            steps.append({"skill": "pdf-tables", "path": _p0(files),
                          "export": "csv"})
        return steps
    if any(w in r for w in ["find", "mention", "occurrence", "where does",
                            "search"]):
        return [{"skill": "pdf-inspect", "path": _p0(files)},
                {"skill": "pdf-search", "path": _p0(files)}]
    if "compare" in r or "diff" in r or "version" in r:
        return [{"skill": "pdf-compare", "a": _p(files, 0), "b": _p(files, 1)}]
    if any(w in r for w in ["question", "ask", "answer", "? "]) or "?" in r:
        return [{"skill": "pdf-qa", "path_or_docid": _p0(files)}]

    # ---- editing / transform ------------------------------------------------
    if "merge" in r or "combine" in r or "join" in r:
        return [{"skill": "pdf-merge", "inputs": files, "output": _out("merged", _p0(files))}]
    if "split" in r:
        return [{"skill": "pdf-split", "path": _p0(files), "output": _out("split", _p0(files))}]
    if any(w in r for w in ["remove page", "delete page"]):
        return [{"skill": "pdf-edit", "path": _p0(files), "op": "delete",
                 "output": _out("edited", _p0(files))}]
    if "reorder" in r or "reverse" in r:
        return [{"skill": "pdf-reorder", "path": _p0(files), "output": _out("reordered", _p0(files))}]
    if "rotate" in r:
        return [{"skill": "pdf-rotate", "path": _p0(files), "output": _out("rotated", _p0(files))}]
    if "crop" in r:
        return [{"skill": "pdf-crop", "path": _p0(files), "output": _out("cropped", _p0(files))}]
    if any(w in r for w in ["watermark", "stamp"]):
        return [{"skill": "pdf-watermark", "path": _p0(files), "output": _out("wm", _p0(files))}]
    if any(w in r for w in ["header", "footer", "page number"]):
        return [{"skill": "pdf-header-footer", "path": _p0(files), "output": _out("hf", _p0(files))}]
    if "annotat" in r or "highlight" in r:
        return [{"skill": "pdf-annotate", "path": _p0(files), "output": _out("annot", _p0(files))}]
    if "metadata" in r:
        return [{"skill": "pdf-metadata", "path": _p0(files), "output": _out("meta", _p0(files))}]
    if "bookmark" in r or "outline" in r or "toc" in r:
        return [{"skill": "pdf-bookmarks", "path": _p0(files)}]
    if "form" in r:
        return [{"skill": "pdf-forms", "path": _p0(files)}]
    if any(w in r for w in ["fill", "complete the form"]):
        return [{"skill": "pdf-fill-forms", "path": _p0(files), "output": _out("filled", _p0(files))}]
    if "encrypt" in r or "password" in r:
        return [{"skill": "pdf-encrypt", "path": _p0(files), "output": _out("enc", _p0(files))}]
    if "decrypt" in r:
        return [{"skill": "pdf-decrypt", "path": _p0(files), "output": _out("dec", _p0(files))}]
    if "redact" in r:
        return [{"skill": "pdf-redact", "path": _p0(files), "output": _out("red", _p0(files))}]
    if "compress" in r or "small" in r or "size" in r:
        return [{"skill": "pdf-compress", "path": _p0(files), "output": _out("comp", _p0(files))}]
    if "optimize" in r:
        return [{"skill": "pdf-optimize", "path": _p0(files), "output": _out("opt", _p0(files))}]
    if "repair" in r or "corrupt" in r or "won't open" in r or "broken" in r:
        return [{"skill": "pdf-repair", "path": _p0(files), "output": _out("repaired", _p0(files))}]
    if any(w in r for w in ["convert", "to markdown", "to html", "to json",
                            "to text", "to docx"]):
        return [{"skill": "pdf-convert", "path": _p0(files), "output": _out("conv", _p0(files))}]
    if "sign" in r:
        return [{"skill": "pdf-sign", "path": _p0(files), "output": _out("signed", _p0(files))}]

    # ---- creation ------------------------------------------------------------
    if any(w in r for w in ["create", "generate", "make a pdf", "produce a pdf",
                            "report from", "invoice", "build"]):
        return [{"skill": "pdf-create", "output": _out("new", _p0(files) or "out")}]

    # default: inspect + read (safe universal behaviour)
    return [{"skill": "pdf-inspect", "path": _p0(files)},
            {"skill": "pdf-read", "path": _p0(files)}]


def _p0(files):
    return files[0] if files else None


def _p(files, i):
    return files[i] if files and i < len(files) else None


# ---------------------------------------------------------------- execution
def execute_step(step: dict, store: Optional[state.DocumentStore] = None,
                 reasoning=None, vision_provider=None) -> Outcome:
    """Execute a single plan step by name. Returns the Outcome."""
    s = step.get("skill")
    if s == "pdf-ocr":
        # auto: only run if needed; degrade cleanly
        return ocr.make_searchable(step.get("path"), step.get("output"))
    if s == "pdf-inspect":
        return inspect.inspect(step.get("path"))
    if s == "pdf-read":
        return extract.extract_text(step.get("path")) or _txtout(step.get("path"))
    if s == "pdf-extract":
        return extract.extract_text(step.get("path"))
    if s == "pdf-summarize":
        return summarize.summarize(step.get("path"),
                                   llm=reasoning)
    if s == "pdf-search":
        q = step.get("query") or "query"
        return search.search_document(step.get("path"), q)
    if s == "pdf-qa":
        return qa.answer(step.get("path_or_docid") or step.get("path"),
                         step.get("question") or "summarize this",
                         reasoning=reasoning, store=store)
    if s == "pdf-compare":
        return compare.compare_pdfs(step.get("a"), step.get("b"))
    if s == "pdf-merge":
        return manipulate.merge_pdfs(step.get("inputs"), step.get("output"))
    if s == "pdf-split":
        return manipulate.split_pdf(step.get("path"), step.get("output"))
    if s == "pdf-edit":
        op = step.get("op", "delete")
        if op == "delete":
            return manipulate.delete_pages(step.get("path"),
                                           step.get("pages") or [],
                                           step.get("output"))
        return manipulate.delete_pages(step.get("path"), [], step.get("output"))
    if s == "pdf-reorder":
        return manipulate.reorder_pdf(step.get("path"), step.get("order") or [],
                                      step.get("output"))
    if s == "pdf-rotate":
        return manipulate.rotate_pdf(step.get("path"), step.get("rotation", 90),
                                     step.get("output"))
    if s == "pdf-crop":
        return manipulate.crop_pdf(step.get("path"), step.get("output"),
                                   margin=step.get("margin", 0))
    if s == "pdf-scale":
        return manipulate.scale_pdf(step.get("path"), step.get("output"),
                                    scale=step.get("scale", 1.0))
    if s == "pdf-watermark":
        return annotate.add_watermark(step.get("path"), step.get("output"),
                                      text=step.get("text"))
    if s == "pdf-header-footer":
        return annotate.add_header_footer(step.get("path"), step.get("output"))
    if s == "pdf-annotate":
        return annotate.add_annotations(step.get("path"), step.get("output"),
                                        step.get("annotations") or [])
    if s == "pdf-metadata":
        return meta.set_metadata(step.get("path"), step.get("output"))
    if s == "pdf-bookmarks":
        return bookmarks.extract_bookmarks(step.get("path"))
    if s == "pdf-forms":
        return forms.list_fields(step.get("path"))
    if s == "pdf-fill-forms":
        return forms.fill_form(step.get("path"), step.get("output"),
                               step.get("values") or {})
    if s == "pdf-encrypt":
        return security.encrypt(step.get("path"), step.get("output"),
                                user_password=step.get("password", ""))
    if s == "pdf-decrypt":
        return security.decrypt(step.get("path"), step.get("output"),
                                password=step.get("password", ""))
    if s == "pdf-redact":
        return annotate.redact_text(step.get("path"), step.get("output"),
                                    terms=step.get("terms") or [])
    if s == "pdf-compress":
        return compress.compress_pdf(step.get("path"), step.get("output"),
                                     profile=step.get("profile", "balanced"))
    if s == "pdf-optimize":
        return compress.compress_pdf(step.get("path"), step.get("output"),
                                     profile=step.get("profile", "balanced"))
    if s == "pdf-repair":
        return repair.repair_pdf(step.get("path"), step.get("output"))
    if s == "pdf-sign":
        return security.sign_pdf(step.get("path"), step.get("output"))
    if s == "pdf-convert":
        return convert.convert_pdf(step.get("path"), step.get("output"),
                                   step.get("to_format", "txt"))
    if s == "pdf-create":
        # caller must provide content; else build placeholder
        return create.create_pdf(step.get("opts") or {"output": step.get("output")},
                                 step.get("content"))
    if s == "pdf-tables":
        o = tables.extract_tables(step.get("path"))
        fmt = step.get("export")
        if fmt and o.ok:
            t = o.data["tables"]
            if fmt == "xlsx":
                return tables.tables_to_xlsx(t, step.get("output"))
            if fmt == "csv":
                return tables.tables_to_csv(t, step.get("output"))
        return o
    if s == "pdf-validation":
        return _validate(step.get("path"))
    # fallback
    o = Outcome(skill=s)
    o.ok = False
    o.status = "failed"
    o.messages.append(f"no executor bound for skill '{s}'")
    return o


def _txtout(path):
    o = Outcome(skill="pdf-read")
    t = extract.extract_text(path)
    o.ok = True
    o.data = t
    return o


def _validate(path):
    from ..core import validation as V
    o = Outcome(skill="pdf-validation")
    o.add_check = None
    o.check("openable", True, V.openable(path).passed, True)
    o.ok = V.openable(path).passed
    return o


def execute_plan(plan: list[dict], store=None, reasoning=None,
                 vision_provider=None) -> list[dict]:
    """Run a plan step by step; each step's Outcome is serialised with timing."""
    results = []
    for step in plan:
        t0 = time.time()
        try:
            oc = execute_step(step, store=store, reasoning=reasoning,
                              vision_provider=vision_provider)
        except Exception as exc:  # noqa: BLE001
            oc = Outcome(skill=step.get("skill", "?"))
            oc.ok = False
            oc.status = "failed"
            oc.messages.append(f"orchestration error: {exc}")
        d = oc.to_dict()
        d["elapsed_ms"] = round((time.time() - t0) * 1000)
        results.append(d)
    return results


# --------------------------------------------------------------- public helpers
def handle_request(request: str, files=None, store=None, reasoning=None):
    """Route + execute + return structured result (SYSTEM MODE entry)."""
    plan = route(request, files)
    results = execute_plan(plan, store=store, reasoning=reasoning)
    return {"request": request, "plan": plan, "results": results,
            "success": all(r["ok"] for r in results)}


def describe_system() -> dict:
    return {"skills": sorted(AVAILABLE_SKILLS),
            "profiles": list(config.OPTIMIZE_PROFILES),
            "backend": config.default_profile().to_dict()}
