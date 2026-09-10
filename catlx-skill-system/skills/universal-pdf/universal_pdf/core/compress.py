"""Compression & optimization (requirement 17) with quality/size profiles.

Approach (lossy work is opt-in per profile, never silently destructive):
  1. structural: garbage collection, deflate streams, clean unused objects;
  2. metadata cleanup if requested;
  3. embedded raster recompression via the backend's native recompression
     routine (PyMuPDF ``Document.rewrite_images``) which applies
     dpi-targeting + JPEG quality internally.

If the native image recompression is unavailable the method degrades to
structural-only cleanup and *reports* that rather than faking success.
"""
from __future__ import annotations

import os
from typing import Optional

from .. import config
from ..result import Outcome
from ..core import validation as V


def _profile(name):
    return config.OPTIMIZE_PROFILES.get(name, config.OPTIMIZE_PROFILES["balanced"])


def _has_rewrite():
    import pymupdf
    return hasattr(pymupdf.Document, "rewrite_images")


def compress_pdf(path: str, output: str, profile: str = "balanced",
                 metadata_cleanup: bool = False,
                 max_image_side: int = 0, password=None) -> Outcome:
    """Compress / optimize a PDF following an optimization profile.

    profiles: maximum_quality | balanced | small_size | web_optimized |
              archive_optimized
    """
    import pymupdf
    prof = _profile(profile)
    out = Outcome(skill="pdf-compress")
    orig_size = os.path.getsize(path)
    doc = pymupdf.open(path)
    if password and doc.needs_pass:
        doc.authenticate(password)
    image_ops = 0
    degraded = False
    try:
        if _has_rewrite() and prof.image_quality < 100:
            # dpi_target only meaningful when recompressing; we target modest
            # dpi only for the downscale-heavy profiles.
            dpi_target = prof.image_dpi if prof.image_dpi else 0
            quality = prof.image_quality
            doc.rewrite_images(dpi_threshold=None,
                               dpi_target=dpi_target,
                               quality=quality,
                               color=True, gray=True, bitonal=True,
                               lossless=True, lossy=True,
                               set_to_gray=False)
            image_ops = 1
        else:
            degraded = True
        if metadata_cleanup:
            doc.set_metadata({})
        doc.save(output, garbage=prof.use_garbage, deflate=prof.deflate,
                 clean=True)
        doc.close()
    except Exception as exc:  # noqa: BLE001
        try:
            doc.close()
        except Exception:
            pass
        out.ok = False
        out.status = "failed"
        out.messages.append(f"compress failed: {exc}")
        return out

    final_size = os.path.getsize(output)
    out.output_path = output
    out.ok = True
    out.degraded = degraded
    out.status = "completed" if not degraded else "degraded"
    if degraded:
        out.warnings.append(
            "image recompression backend unavailable; applied structural "
            "cleanup only")
    out.data = {"original_bytes": orig_size, "final_bytes": final_size,
                "saved_pct": round((1 - final_size / max(1, orig_size)) * 100, 2),
                "profile": prof.name, "image_operations": image_ops}
    out.check("openable", True, V.openable(output).passed, True)
    out.check("not_larger", "<=" + str(orig_size), final_size,
              final_size <= orig_size)
    return out
