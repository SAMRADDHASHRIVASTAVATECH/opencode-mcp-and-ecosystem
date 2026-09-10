"""Storage management: usage reporting and safe cleanup.

cleanup never touches user model files; it only clears caches/temp that this
system owns. Destructive cleanup is explicit and scoped.
"""
from __future__ import annotations

import shutil
import time
from pathlib import Path

from .config import Settings


def dir_size_gb(path: Path) -> float:
    total = 0
    try:
        for p in path.rglob("*"):
            if p.is_file():
                try:
                    total += p.stat().st_size
                except OSError:  # noqa: BLE001
                    pass
    except Exception:   # noqa: BLE001
        pass
    return round(total / (1024 ** 3), 3)


def disk_free_gb(path: Path) -> float:
    try:
        u = shutil.disk_usage(str(path))
        return round(u.free / (1024 ** 3), 2)
    except Exception:   # noqa: BLE001
        return 0.0


class StorageManager:
    def __init__(self, settings: Settings):
        self.s = settings

    def usage(self) -> dict:
        sections = {}
        for name, d in (("models", self.s.resolved_models_dir()),
                        ("outputs", self.s.resolved_outputs_dir()),
                        ("cache", self.s.resolved_cache_dir()),
                        ("logs", self.s.resolved_logs_dir()),
                        ("workflows", self.s.resolved_workflows_dir())):
            if d.exists():
                sections[name] = {"path": str(d),
                                  "size_gb": dir_size_gb(d)}
        root = self.s.resolved_root()
        sections["state_root"] = {"path": str(root),
                                  "free_gb": disk_free_gb(root)}
        return sections

    def cleanup_cache(self, *, older_than_days: float = 3.0) -> dict:
        cache = self.s.resolved_cache_dir()
        removed, bytes_freed = 0, 0
        if cache.exists():
            cutoff = time.time() - older_than_days * 86400
            for p in cache.rglob("*"):
                if p.is_file():
                    try:
                        if p.stat().st_mtime < cutoff:
                            bytes_freed += p.stat().st_size
                            p.unlink()
                            removed += 1
                    except OSError:  # noqa: BLE001
                        pass
        for p in sorted(cache.rglob("*"), key=lambda x: len(str(x)),
                        reverse=True):
            try:
                if p.is_dir() and not any(p.iterdir()):
                    p.rmdir()
            except Exception:  # noqa: BLE001
                pass
        return {"removed_files": removed,
                "bytes_freed": bytes_freed,
                "freed_gb": round(bytes_freed / (1024 ** 3), 3)}

    def cleanup_temp(self, *, older_than_days: float = 1.0) -> dict:
        tmp_root = self.s.resolved_cache_dir() / "tmp"
        removed = 0
        if tmp_root.exists():
            cutoff = time.time() - older_than_days * 86400
            for p in tmp_root.rglob("*"):
                if p.is_file():
                    try:
                        if p.stat().st_mtime < cutoff:
                            p.unlink()
                            removed += 1
                    except OSError:  # noqa: BLE001
                        pass
        return {"removed_temp_files": removed}
