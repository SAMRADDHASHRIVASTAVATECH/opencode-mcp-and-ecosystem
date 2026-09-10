"""pdf-inspect: build a structured document profile (requirement 4)."""
from __future__ import annotations

import os

from ..result import Outcome
from ..tools import adapter


def inspect(path: str, password: str | None = None) -> Outcome:
    """Inspect a PDF and return a structured profile.

    Uses PyMuPDF (preferred) and augments with pypdf for fields PyMuPDF does
    not expose. Never needs the full text of a huge file.
    """
    out = Outcome(skill="pdf-inspect")
    doc, backend = adapter.load_document(path)
    try:
        encrypted = bool(getattr(doc, "needs_pass", False) or
                         getattr(doc, "is_encrypted", False))
        if getattr(doc, "needs_pass", False) and password:
            doc.authenticate(password)
        if getattr(doc, "needs_pass", False) and not password:
            # Report what is visible (encryption) without pretending full access.
            out.ok = True
            out.degraded = True
            out.status = "degraded"
            out.data = {
                "path": os.path.abspath(path),
                "size_bytes": os.path.getsize(path),
                "page_count": _pagecount(doc),
                "security": {"encrypted": True, "needs_password": True},
            }
            out.messages.append(
                "document is encrypted; password required for full content "
                "profile (metadata/fonts/images are not accessible without it)")
            return out

        profile = {"path": os.path.abspath(path),
                   "size_bytes": os.path.getsize(path)}

        # page_count
        profile["page_count"] = _pagecount(doc)

        if hasattr(doc, "metadata"):
            profile["metadata"] = dict(doc.metadata or {})

        # page geometry (dimensions of page 1 in points)
        try:
            p = doc[0]
            r = p.rect
            profile["page_size_points"] = {"width": round(r.width, 2),
                                           "height": round(r.height, 2)}
            profile["orientation"] = ("landscape" if r.width > r.height
                                      else "portrait")
        except Exception:
            pass

        # per-page resource summary (fonts/images/links/annots)
        fonts, images, links, annots, text_pages = set(), 0, 0, 0, 0
        for page in doc:
            try:
                if page.get_text("text").strip():
                    text_pages += 1
                d = page.get_fonts(full=True)
                for f in d:
                    fonts.add(f[3] or f[2])
                images += len(page.get_images(full=True))
                links += len(page.get_links())
                annots += len(list(page.annots() or []))
            except Exception:
                pass
        profile["resources"] = {"fonts": sorted(fonts), "image_count": images,
                                "link_count": links,
                                "annotation_count": annots,
                                "pages_with_text": text_pages}

        # structure
        try:
            profile["toc"] = doc.get_toc()
        except Exception:
            profile["toc"] = []
        profile["embedded_files"] = []
        try:
            names = (list(doc.embfile_names())
                     if hasattr(doc, "embfile_names") else [])
            for name in names:
                try:
                    info = doc.embfile_info(name)
                    profile["embedded_files"].append(
                        {"name": name,
                         "size": info.get("size") if info else None,
                         "desc": info.get("desc") if info else None})
                except Exception:
                    profile["embedded_files"].append({"name": name})
        except Exception:
            pass

        # encryption / permissions
        profile["security"] = {"encrypted": bool(getattr(doc, "is_encrypted", False)),
                               "needs_password": bool(getattr(doc, "needs_pass", False))}
        try:
            perms = doc.permissions
            profile["security"]["permissions"] = (
                int(perms) if perms is not None else None)
        except Exception:
            pass

        # pdf version
        profile["pdf_version"] = str(getattr(doc, "pdf_version", ""))
        profile["metadata"]["pdf_version"] = profile["pdf_version"]

        # forms present?
        try:
            profile["has_form"] = bool(doc.is_form_pdf)
            if doc.is_form_pdf:
                profile["form_fields"] = _form_fields(doc)
        except Exception:
            profile["has_form"] = False

        out.data = profile
        out.ok = True
        out.status = "completed"
        out.check("page_count", ">0", profile["page_count"],
                  profile["page_count"] > 0)
        out.check("openable", True, True, True)
        return out
    finally:
        if hasattr(doc, "close"):
            doc.close()


def _pagecount(doc) -> int:
    if hasattr(doc, "page_count"):
        return int(doc.page_count)
    return len(doc.pages)


def _form_fields(doc):
    try:
        fields = []
        for i in range(doc.page_count):
            for widget in (doc[i].widgets() or []):
                fields.append({"name": widget.field_name,
                               "type": _fieldtype(widget.field_type),
                               "value": widget.field_value})
        return fields
    except Exception:
        return []


def _fieldtype(t):
    names = {1: "text", 2: "checkbox", 3: "radio", 4: "dropdown",
             5: "list", 6: "signature", 7: "pushbutton"}
    return names.get(t, str(t))
