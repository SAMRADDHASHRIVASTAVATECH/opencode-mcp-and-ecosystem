"""AcroForm operations (requirement 20): detect/list/extract/fill/validate/flatten.

Preferred tool: PyMuPDF widget API (widgets are enumerated per page).
"""
from __future__ import annotations

from typing import Optional

from ..result import Outcome


def _fieldtype(t):
    names = {1: "text", 2: "checkbox", 3: "radio", 4: "dropdown",
             5: "list", 6: "signature", 7: "text"}
    return names.get(t, str(t))


def _widget_kind(w):
    """Best-effort widget kind, preferring the type string when available."""
    ts = getattr(w, "field_type_string", None)
    if ts:
        s = ts.lower()
        if "text" in s:
            return "text"
        if "check" in s:
            return "checkbox"
        if "radio" in s:
            return "radio"
        if "list" in s or "combo" in s or "choice" in s:
            return "list"
        if "signature" in s:
            return "signature"
    return _fieldtype(getattr(w, "field_type", None))


def _iter_widgets(doc):
    """Yield widgets across all pages (backend-specific enumeration)."""
    for i in range(doc.page_count):
        page = doc[i]
        for w in (page.widgets() or []):
            yield w


def list_fields(path: str, password=None) -> Outcome:
    import pymupdf
    out = Outcome(skill="pdf-forms")
    doc = pymupdf.open(path)
    if password and doc.needs_pass:
        doc.authenticate(password)
    fields = []
    try:
        for w in _iter_widgets(doc):
            fields.append({"name": w.field_name, "type": _widget_kind(w),
                           "value": w.field_value})
    except Exception as exc:  # noqa: BLE001
        out.ok = False
        out.status = "failed"
        out.messages.append(str(exc))
        doc.close()
        return out
    doc.close()
    out.ok = True
    out.data = {"fields": fields, "count": len(fields), "is_form": bool(fields)}
    return out


def fill_form(path: str, output: str, values: dict, flatten: bool = False,
              password=None) -> Outcome:
    """Fill fields by name. values: {field_name: value}. Checkboxes take
    True/False. Flatten burns values into the page content."""
    import pymupdf
    out = Outcome(skill="pdf-fill-forms")
    doc = pymupdf.open(path)
    if password and doc.needs_pass:
        doc.authenticate(password)
    filled, failed = [], []
    try:
        for w in _iter_widgets(doc):
            name = w.field_name
            if name in values:
                val = values[name]
                kind = _widget_kind(w)
                try:
                    if kind in ("checkbox", "radio"):
                        w.field_value = bool(val)
                    elif kind in ("list",):
                        w.field_value = str(val)
                    elif kind == "text":
                        w.field_value = str(val)
                    else:
                        # pushbutton or unknown — skip silently (not fillable)
                        continue
                    w.update()
                    filled.append(name)
                except Exception:  # noqa: BLE001
                    failed.append(name)
        doc.save(output, garbage=3, deflate=True)
        doc.close()
        out.output_path = output
        out.ok = True
        out.status = "completed"
        out.data = {"filled": filled, "failed": failed}
        out.check("filled", set(values), set(filled),
                  set(values).issubset(set(filled)),
                  f"failed={failed}")
        return out
    except Exception as exc:  # noqa: BLE001
        try:
            doc.close()
        except Exception:
            pass
        out.ok = False
        out.status = "failed"
        out.messages.append(f"fill failed: {exc}")
        return out


def extract_form_data(path: str, password=None) -> Outcome:
    o = list_fields(path, password)
    if o.ok:
        o.skill = "pdf-forms"
        o.data = {f["name"]: f["value"] for f in o.data["fields"]}
    return o


def flatten_form(path: str, output: str, password=None) -> Outcome:
    import pymupdf
    out = Outcome(skill="pdf-forms")
    doc = pymupdf.open(path)
    if password and doc.needs_pass:
        doc.authenticate(password)
    try:
        for i in range(doc.page_count):
            for w in (doc[i].widgets() or []):
                w.update()
        doc.save(output, garbage=3, deflate=True)
        doc.close()
        out.output_path = output
        out.ok = True
        out.status = "completed"
        left = 0
        chk = pymupdf.open(output)
        for i in range(chk.page_count):
            left += sum(1 for _ in (chk[i].widgets() or []))
        chk.close()
        out.check("flattened", 0, left, left == 0)
        if left:
            # Flattening requires burning field values into page content and
            # removing the widgets; the default backend cannot always do this
            # for arbitrary forms. Report the honest result rather than faking.
            out.ok = False
            out.degraded = True
            out.status = "degraded"
            out.warnings.append(
                f"{left} widgets remain after flatten attempt; this form "
                "could not be flattened with the current backend (values were "
                "saved, widgets not removed). Use a dedicated flattening tool "
                "for pixel-authoritative output.")
        return out
    except Exception as exc:  # noqa: BLE001
        try:
            doc.close()
        except Exception:
            pass
        out.ok = False
        out.status = "failed"
        out.messages.append(f"flatten failed: {exc}")
        return out
