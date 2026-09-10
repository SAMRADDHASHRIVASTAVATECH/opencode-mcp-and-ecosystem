"""Metadata & document property operations (requirement 23)."""
from __future__ import annotations

from typing import Optional

from ..result import Outcome
from ..tools import adapter


def read_metadata(path: str, password=None) -> Outcome:
    from ..core import inspect as _ins
    return _ins.inspect(path, password)


def set_metadata(path: str, output: str, title=None, author=None,
                 subject=None, keywords=None, creator=None,
                 producer=None, extra: Optional[dict] = None,
                 password=None) -> Outcome:
    """Write/update document metadata (creates a new file at ``output``)."""
    import pymupdf
    out = Outcome(skill="pdf-metadata")
    doc = pymupdf.open(path)
    if password and doc.needs_pass:
        doc.authenticate(password)
    md = dict(doc.metadata or {})
    if title is not None:
        md["title"] = title
    if author is not None:
        md["author"] = author
    if subject is not None:
        md["subject"] = subject
    if keywords is not None:
        md["keywords"] = keywords
    if creator is not None:
        md["creator"] = creator
    if producer is not None:
        md["producer"] = producer
    for k, v in (extra or {}).items():
        md[k] = v
    try:
        doc.set_metadata(md)
        doc.save(output, garbage=3, deflate=True)
        doc.close()
        out.output_path = output
        out.ok = True
        out.status = "completed"
        out.data = {"metadata": md}
        # verify
        chk = pymupdf.open(output)
        nm = dict(chk.metadata or {})
        chk.close()
        ok = (title is None or nm.get("title") == title)
        out.check("metadata_written", title, nm.get("title"), ok)
        return out
    except Exception as exc:  # noqa: BLE001
        try:
            doc.close()
        except Exception:
            pass
        out.ok = False
        out.status = "failed"
        out.messages.append(f"metadata update failed: {exc}")
        return out


def remove_metadata(path: str, output: str, password=None) -> Outcome:
    """Strip all document metadata (cleanup before publishing)."""
    return set_metadata(path, output, title="", author="", subject="",
                        keywords="", creator="", producer="",
                        extra={k: "" for k in ("creationDate",
                                               "modDate")},
                        password=password)
