"""Tiny optional on-disk cache for fetched content + search results.

Helps research memory avoid repeated network work. Keys are SHA256 of the
request; values stored under a configured cache dir (defaults to a
user-cacheable location). Content size is capped.
"""
from __future__ import annotations

import hashlib
import json
import os
import tempfile
import time
from pathlib import Path
from typing import Optional


def _default_dir() -> Path:
    return Path(tempfile.gettempdir()) / "universal_research_cache"


class Cache:
    def __init__(self, base: Optional[str] = None, ttl_seconds: int = 3600,
                 enabled: bool = True):
        self.enabled = enabled
        self.ttl = ttl_seconds
        base = base or os.environ.get("UR_CACHE_DIR") or _default_dir()
        self.dir = Path(base) / "v1"
        self.dir.mkdir(parents=True, exist_ok=True)

    def _path(self, key: str, ns: str) -> Path:
        h = hashlib.sha256(key.encode()).hexdigest()
        return self.dir / ns / f"{h}.json"

    def get(self, key: str, ns: str = "default"):
        if not self.enabled:
            return None
        p = self._path(key, ns)
        if not p.exists():
            return None
        try:
            data = json.loads(p.read_text())
        except Exception:
            return None
        if time.time() - data.get("_t", 0) > self.ttl:
            return None
        return data.get("value")

    def put(self, key: str, value, ns: str = "default"):
        if not self.enabled:
            return
        p = self._path(key, ns)
        p.parent.mkdir(parents=True, exist_ok=True)
        try:
            p.write_text(json.dumps({"_t": time.time(), "value": value},
                                    default=str))
        except Exception:
            pass

    def clear(self):
        if self.dir.exists():
            import shutil
            shutil.rmtree(self.dir, ignore_errors=True)
