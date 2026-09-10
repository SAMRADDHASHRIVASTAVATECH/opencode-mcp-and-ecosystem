"""Source provenance (requirement 32).

Every derived piece of information can carry a ``Provenance`` recording where
it came from: source document, page range, section/chunk id, object (table /
image / region) and how it was obtained (extraction method + confidence).
"""
from __future__ import annotations

import hashlib
import time
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Optional


def file_fingerprint(path: str) -> str:
    """Cheap stable content fingerprint (first+last 64KB + size).

    Never raises: a missing/unreadable file is fingerprinted from its path so
    documents can be registered in the knowledge store before the file exists.
    """
    h = hashlib.sha256()
    size = None
    try:
        with open(path, "rb") as fh:
            size = Path(path).stat().st_size
            head = fh.read(65536)
            fh.seek(max(0, size - 65536))
            tail = fh.read(65536)
            h.update(head)
            h.update(b"||")
            h.update(tail)
    except Exception:
        pass
    h.update((path if size is None else str(size)).encode())
    return h.hexdigest()


@dataclass
class Provenance:
    """Attribution for a derived item."""
    source_path: Optional[str] = None
    source_id: Optional[str] = None      # knowledge-base doc id
    page: Optional[int] = None           # 1-based page
    pages: Optional[list] = None         # page range when multi-page
    section: Optional[str] = None
    chunk_id: Optional[str] = None
    object_type: Optional[str] = None    # table | image | region | text | figure
    object_index: Optional[int] = None
    method: Optional[str] = None         # extraction method
    confidence: Optional[float] = None   # 0..1
    created_utc: float = field(default_factory=time.time)

    def to_dict(self) -> dict:
        return {k: v for k, v in asdict(self).items() if v is not None}


def anchor(source: str, **kw) -> Provenance:
    """Create provenance for output derived from ``source``."""
    p = Provenance(source_path=source, **kw)
    p.source_id = p.source_id or file_fingerprint(source)
    return p
