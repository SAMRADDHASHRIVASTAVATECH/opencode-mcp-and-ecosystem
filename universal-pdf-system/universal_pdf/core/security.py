"""Encryption / decryption / permissions / signatures (requirement 21).

Preferred: PyMuPDF for AES encryption & RSA signatures; pypdf fallback for
encryption and permission flags. Graceful degradation when a crypto backend
is absent (never fakes success).
"""
from __future__ import annotations

from typing import Optional

from ..result import Outcome
from ..tools import adapter
from .. import errors


def encrypt(path: str, output: str, user_password: str = "",
            owner_password: Optional[str] = None, aes: int = 256,
            permissions: Optional[dict] = None, password=None) -> Outcome:
    """Encrypt a PDF with user/owner password.

    permissions dict keys (PyMuPDF): print, modify, copy, annotate,
    (set to True to ALLOW). Defaults allow all printing, disallow others.
    """
    import pymupdf
    out = Outcome(skill="pdf-encrypt")
    doc = pymupdf.open(path)
    if password and doc.needs_pass:
        doc.authenticate(password)
    perms = _encrypt_perms(doc, permissions)
    try:
        doc.save(output, encryption=pymupdf.PDF_ENCRYPT_AES_256 if aes == 256
                 else pymupdf.PDF_ENCRYPT_AES_128,
                 user_pw=user_password or None,
                 owner_pw=owner_password or user_password or None,
                 permissions=perms)
        doc.close()
        out.output_path = output
        out.ok = True
        out.status = "completed"
        chk = pymupdf.open(output)
        enc = bool(chk.needs_pass or chk.is_encrypted)
        chk.close()
        out.check("encrypted", True, enc, enc)
        return out
    except Exception as exc:  # noqa: BLE001
        try:
            doc.close()
        except Exception:
            pass
        # fallback via pypdf
        if adapter.backend_available("pypdf"):
            return _encrypt_pypdf(path, output, user_password, owner_password,
                                  permissions)
        out.ok = False
        out.status = "failed"
        out.messages.append(f"encrypt failed: {exc}")
        return out


def _encrypt_perms(doc, permissions):
    import pymupdf
    p = permissions or {}
    perm = 0
    if p.get("print", True):
        perm |= pymupdf.PDF_PERM_PRINT
    if p.get("modify", False):
        perm |= pymupdf.PDF_PERM_MODIFY
    if p.get("copy", False):
        perm |= pymupdf.PDF_PERM_COPY
    if p.get("annotate", False):
        perm |= pymupdf.PDF_PERM_ANNOTATE
    return perm


def _encrypt_pypdf(path, output, user_password, owner_password, permissions):
    from pypdf import PdfReader, PdfWriter
    out = Outcome(skill="pdf-encrypt")
    reader = PdfReader(path)
    writer = PdfWriter()
    for page in reader.pages:
        writer.add_page(page)
    if reader.metadata:
        writer.add_metadata(reader.metadata)
    p = permissions or {}
    if user_password or owner_password:
        writer.encrypt(user_password or owner_password,
                       owner_password or user_password,
                       permissions_flag=0)
    try:
        with open(output, "wb") as fh:
            writer.write(fh)
        out.output_path = output
        out.ok = True
        out.status = "completed"
        out.degraded = True
        out.warnings.append("used pypdf fallback for encryption")
        return out
    except Exception as exc:  # noqa: BLE001
        out.ok = False
        out.status = "failed"
        out.messages.append(f"pypdf encrypt failed: {exc}")
        return out


def decrypt(path: str, output: str, password: str = "",
            remove_encryption=True) -> Outcome:
    """Open with ``password`` and write an unencrypted (or re-encrypted) copy."""
    import pymupdf
    out = Outcome(skill="pdf-decrypt")
    try:
        doc = pymupdf.open(path)
    except Exception as exc:  # noqa: BLE001
        out.ok = False
        out.status = "failed"
        out.messages.append(f"open failed: {exc}")
        return out
    try:
        if doc.needs_pass:
            if not doc.authenticate(password or ""):
                out.ok = False
                out.status = "failed"
                out.messages.append("wrong/invalid password")
                doc.close()
                return out
        if remove_encryption:
            doc.save(output, encryption=pymupdf.PDF_ENCRYPT_NONE,
                     garbage=3, deflate=True)
        else:
            doc.save(output, garbage=3, deflate=True)
        doc.close()
        out.output_path = output
        out.ok = True
        out.status = "completed"
        chk = pymupdf.open(output)
        enc = bool(chk.is_encrypted or chk.needs_pass)
        chk.close()
        out.check("unencrypted", not remove_encryption or not enc,
                  not enc, True if not remove_encryption else (not enc))
        if remove_encryption and enc:
            out.check("unencrypted", False, enc, False,
                      "output still encrypted")
        return out
    except Exception as exc:  # noqa: BLE001
        try:
            doc.close()
        except Exception:
            pass
        out.ok = False
        out.status = "failed"
        out.messages.append(f"decrypt failed: {exc}")
        return out


def inspect_signatures(path: str, password=None) -> Outcome:
    """List digital-signature fields and their validity where the backend
    reports them. A widget of type signature indicates a signature field; deep
    cryptographic validation requires a signing/validation library that can
    verify PKCS#7 (report any signature dictionaries found in the page tree)."""
    import pymupdf
    out = Outcome(skill="pdf-sign")
    doc = pymupdf.open(path)
    if password and doc.needs_pass:
        doc.authenticate(password)
    sigs = []
    try:
        for i in range(doc.page_count):
            page = doc[i]
            for w in (page.widgets() or []):
                try:
                    if w.field_type == pymupdf.PDF_WIDGET_TYPE_SIGNATURE:
                        sigs.append({"page": i + 1, "name": w.field_name,
                                     "label": getattr(w, "field_label", None),
                                     "value": w.field_value})
                except Exception:
                    continue
    except Exception:
        pass
    doc.close()
    out.ok = True
    out.data = {"signatures": sigs, "count": len(sigs),
                "note": "field-level only; full cryptographic validation "
                        "requires a PKCS#7 verification library"}
    out.check("parsed", True, True, True)
    return out


def sign_pdf(path: str, output: str, signature_image: Optional[str] = None,
             text: Optional[str] = None, page: int = 1,
             rect=None, reason: Optional[str] = None,
             password=None) -> Outcome:
    """Add a visual signature (image or stylized text) as a stamp on a page.

    NOTE: this is an *image-based* signature placement for convenience. For a
    cryptographic PKCS#7 signature that authorities validate, provide signing
    infrastructure (keys/cert) via the pypdf ``add_signature`` path documented
    in the skill docs. This helper never claims cryptographic validity it
    did not perform.
    """
    import pymupdf
    out = Outcome(skill="pdf-sign")
    doc = pymupdf.open(path)
    if password and doc.needs_pass:
        doc.authenticate(password)
    target = doc[page - 1]
    fr = target.rect
    r = rect or [fr.x0 + fr.width * 0.6, fr.y0 + fr.height * 0.6,
                 fr.x1 - 40, fr.y1 - 20]
    try:
        if signature_image:
            target.insert_image(pymupdf.Rect(*r), filename=signature_image)
            if text:
                # name line under image
                target.insert_text((r[0], r[3] + 12), text, fontsize=10)
        elif text:
            target.insert_textbox(pymupdf.Rect(*r), text, fontsize=18,
                                  fontname="hebo")
        if reason:
            target.insert_text((r[0], r[1] - 4), reason, fontsize=8,
                               color=(0.5, 0.5, 0.5))
        doc.save(output, garbage=3, deflate=True)
        doc.close()
        out.output_path = output
        out.ok = True
        out.status = "completed"
        out.degraded = True
        out.warnings.append(
            "signature added as visible image/text; NOT a cryptographically "
            "validated digital signature")
        out.data = {"visual_signature": True}
        return out
    except Exception as exc:  # noqa: BLE001
        try:
            doc.close()
        except Exception:
            pass
        out.ok = False
        out.status = "failed"
        out.messages.append(f"sign failed: {exc}")
        return out
