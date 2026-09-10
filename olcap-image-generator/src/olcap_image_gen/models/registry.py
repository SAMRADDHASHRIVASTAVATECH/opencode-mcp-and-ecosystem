"""Persistent model registry.

Records installed/known models, their files, verification state and
capabilities. Survives restarts (JSON under the state dir). Never treats a
partially downloaded or unverified model as installed.
"""
from __future__ import annotations

import json
import threading
import time
from pathlib import Path


class ModelRegistry:
    def __init__(self, path: str | Path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.Lock()
        self._models: dict[str, dict] = {}
        self._load()

    def _load(self):
        if self.path.exists():
            try:
                data = json.loads(self.path.read_text(encoding="utf-8"))
                self._models = data.get("models", {})
            except Exception:   # noqa: BLE001
                self._models = {}

    def _save(self):
        payload = {"models": self._models, "updated": time.time()}
        tmp = self.path.with_suffix(".tmp")
        tmp.write_text(json.dumps(payload, ensure_ascii=False, indent=2),
                       encoding="utf-8")
        tmp.replace(self.path)

    def list(self, *, installed_only: bool = False) -> list[dict]:
        with self._lock:
            out = list(self._models.values())
        if installed_only:
            out = [m for m in out if m.get("installed") and m.get("verified")]
        return sorted(out, key=lambda m: m.get("name", ""))

    def get(self, model_id: str) -> dict | None:
        with self._lock:
            m = self._models.get(model_id)
            return dict(m) if m else None

    def search(self, query: str) -> list[dict]:
        q = (query or "").lower()
        with self._lock:
            allm = list(self._models.values())
        if q:
            return [m for m in allm
                    if q in m.get("name", "").lower()
                    or q in m.get("family", "").lower()
                    or q in m.get("id", "").lower()]
        return allm

    def installed_ids(self) -> set[str]:
        return {i for i, m in self._models.items()
                if m.get("installed") and m.get("verified")}

    def register(self, entry: dict) -> dict:
        mid = entry["id"]
        with self._lock:
            prev = dict(self._models.get(mid, {}))
            merged = {**prev, **entry}
            merged["id"] = mid
            merged["registered_at"] = merged.get("registered_at",
                                                 prev.get("registered_at",
                                                          time.time()))
            self._models[mid] = merged
            self._save()
        return dict(self._models[mid])

    def mark_installed(self, model_id: str, *, verified: bool,
                       files: list[str] | None = None, meta: dict | None = None):
        with self._lock:
            m = self._models.get(model_id)
            if not m:
                raise KeyError(model_id)
            m["installed"] = True
            m["verified"] = verified
            if files is not None:
                m["files"] = files
            if meta:
                m["meta"] = {**m.get("meta", {}), **meta}
            m["updated"] = time.time()
            self._save()
        return dict(m)

    def mark_unverified(self, model_id: str, reason: str):
        with self._lock:
            m = self._models.get(model_id)
            if m:
                m["installed"] = False
                m["verified"] = False
                m["unverified_reason"] = reason
                m["updated"] = time.time()
                self._save()

    def remove(self, model_id: str) -> bool:
        with self._lock:
            if model_id in self._models:
                del self._models[model_id]
                self._save()
                return True
        return False

    def update(self, model_id: str, fields: dict) -> dict:
        with self._lock:
            m = self._models.get(model_id)
            if not m:
                raise KeyError(model_id)
            m.update(fields)
            m["updated"] = time.time()
            self._save()
        return dict(m)
