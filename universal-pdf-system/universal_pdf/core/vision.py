"""Visual PDF processing (requirement 7) with graceful degradation.

No vision model ships inside the repo. Instead this module exposes a pluggable
*provider* (a callable that returns descriptive text for an image) so an agent
with vision capability can be injected. When no provider is registered the
skill degrades gracefully to text/OCR methods and *reports* that vision was
unavailable rather than pretending to "see".
"""
from __future__ import annotations

from typing import Callable, Optional

from ..result import Outcome
from ..config import default_profile


def describe_page(path: str, page: int = 1, provider: Optional[Callable] = None,
                  dpi: int = 150, password=None) -> Outcome:
    """Return a caption/description of a rendered page using a vision provider.

    provider: callable(image_bytes, format='png') -> str description.
    If omitted, reads config/registry and, absent a vision model, degrades.
    """
    from ..core import images as im
    out = Outcome(skill="pdf-vision")
    provider = provider or _resolved_provider()
    if provider is None:
        out.ok = False
        out.degraded = True
        out.status = "degraded"
        out.messages.append(
            "No vision provider available. Falling back to text/OCR. "
            "Register a provider to enable image/chart/figure interpretation.")
        out.warnings.append("Vision unavailable -> text/OCR methods only.")
        return out
    try:
        data = im.render_page_to_bytes(path, page, dpi=dpi)
        text = provider(data)
        out.ok = True
        out.data = {"page": page, "description": text}
        out.check("described", True, bool(text), True)
        return out
    except Exception as exc:  # noqa: BLE001
        out.ok = False
        out.status = "failed"
        out.messages.append(f"vision failed: {exc}")
        return out


def _resolved_provider():
    """Look up an injected vision provider via module-level registry or config.

    The orchestration layer may set ``universal_pdf.core.vision.PROVIDER``.
    """
    return PROVIDER


# registry the orchestrator / agent can populate
PROVIDER: Optional[Callable] = None
