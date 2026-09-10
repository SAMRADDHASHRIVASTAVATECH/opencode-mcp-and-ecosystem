"""Resource-aware execution (requirement 33).

Before an expensive operation a skill may consult :func:`estimate_strategy` to
decide page batching, whether to OCR, whether to rasterise, etc. based on the
document profile and the host profile, so we never burn resources when a
simpler method suffices.
"""
from __future__ import annotations

from dataclasses import dataclass
from .. import config


@dataclass
class DocProfile:
    """Cheap structural facts used for strategy decisions."""
    page_count: int
    path: str = ""
    approx_chars: int = 0
    has_images: bool = False
    has_text_layer: bool = True
    file_kb: int = 0

    @property
    def is_scanned(self) -> bool:
        return (not self.has_text_layer) and (self.approx_chars < self.page_count * 20)


@dataclass
class Strategy:
    """Recommended execution plan for a document+profile combination."""
    whole_in_memory: bool
    page_batch: int
    needs_ocr: bool
    needs_vision: bool
    use_index: bool
    reason: str


def strategy(doc: DocProfile,
             profile: config.RuntimeProfile | None = None) -> Strategy:
    """Pick an efficient strategy automatically (requirement 33/34)."""
    profile = profile or config.default_profile()
    n = doc.page_count
    est_mb = doc.file_kb / 1024.0
    # Memory guard: allow whole-load only if doc is comfortably small.
    can_whole = (n <= 400) and (est_mb < 512)
    batch = profile.page_batch_size
    if n <= 10:
        batch = max(batch, 1)
    elif n > 2000:
        batch = min(batch, 15)

    if n > 1500:
        can_whole = False

    # needs_ocr only if there is genuinely no usable text layer.
    needs_ocr = doc.is_scanned
    needs_vision = doc.is_scanned and not profile.ocr_available

    use_index = n > 400

    reasons = []
    reasons.append(f"{n} pages, {est_mb:.1f} MB, "
                   f"text_layer={'yes' if doc.has_text_layer else 'no'}")
    if not can_whole:
        reasons.append("streaming/batched pages required")
    if needs_ocr:
        reasons.append("no usable text layer -> OCR")
    if use_index:
        reasons.append("large doc -> external index + retrieval")
    return Strategy(whole_in_memory=can_whole, page_batch=batch,
                    needs_ocr=needs_ocr, needs_vision=needs_vision,
                    use_index=use_index, reason="; ".join(reasons))
