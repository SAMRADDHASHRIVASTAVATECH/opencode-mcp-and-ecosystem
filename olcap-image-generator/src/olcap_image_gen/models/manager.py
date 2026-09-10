"""Model lifecycle manager: install / verify / update / remove.

Installing a model requires an explicit, authorized source (URL or local path)
because exact download assets are never assumed. Downloads are resumable and
sha256-verified when a hash is supplied; otherwise we verify only file presence
+ non-empty and report verification truthfully.
"""
from __future__ import annotations

import os
import shutil
import time
from pathlib import Path

from ..errors import InvalidArguments, ModelNotFound
from .downloader import download, sha256_of
from .registry import ModelRegistry

_EXT = {".safetensors", ".ckpt", ".gguf", ".bin", ".pt", ".pth", ".onnx"}


class ModelManager:
    def __init__(self, registry: ModelRegistry, models_dir: str,
                 allowed_roots: list[str] | None = None):
        self.registry = registry
        self.models_dir = Path(models_dir)
        self.models_dir.mkdir(parents=True, exist_ok=True)
        self.roots = allowed_roots or []

    def install(self, *, model_id: str = "", name: str, family: str,
                source: str, quant: str = "auto", license: str = "",
                capabilities: list | None = None,
                expected_sha256: str = "", job=None) -> dict:
        fam_dir = self.models_dir / family
        fam_dir.mkdir(parents=True, exist_ok=True)
        capabilities = capabilities or ["text_to_image"]
        mid = model_id or f"{family}-{quant}"

        is_url = source.lower().startswith(("http://", "https://"))
        if is_url:
            res = download(source, str(fam_dir), expected_sha256=expected_sha256,
                           job=job, roots=self.roots)
            final = res["path"]
            verified = res["verified"]
        else:
            local = Path(source).expanduser()
            if not local.is_file():
                raise ModelNotFound(f"source file not found: {source}")
            if local.suffix.lower() not in _EXT:
                raise InvalidArguments(
                    f"unsupported model file type '{local.suffix}' (allowed "
                    f"{sorted(_EXT)})")
            target = fam_dir / local.name
            if expected_sha256:
                actual = sha256_of(str(local))
                if actual != expected_sha256:
                    raise ModelNotFound("local file sha256 does not match")
                verified = True
            else:
                verified = None
            shutil.copyfile(local, target)
            final = str(target)

        self.registry.register({
            "id": mid, "name": name, "family": family, "quant": quant,
            "path": final, "size_bytes": Path(final).stat().st_size,
            "license": license, "capabilities": capabilities,
            "installed": True, "verified": bool(verified),
            "verification": "sha256" if verified else
            ("none" if verified is False else "size"),
            "source": source if is_url else "local",
            "registered": True})
        return self.registry.get(mid)

    def verify(self, model_id: str) -> dict:
        e = self.registry.get(model_id)
        if not e:
            raise ModelNotFound(model_id)
        path = e.get("path")
        if not path or not os.path.exists(path):
            self.registry.mark_unverified(model_id, "file missing")
            return {"model_id": model_id, "verified": False,
                    "reason": "file missing"}
        size = os.path.getsize(path)
        ok = size > 0 and (size == e.get("size_bytes") or not e.get("size_bytes"))
        self.registry.mark_installed(model_id, verified=ok)
        return {"model_id": model_id, "verified": ok, "path": path,
                "size_bytes": size}

    def update(self, model_id: str, source: str, *,
               expected_sha256: str = "", job=None) -> dict:
        e = self.registry.get(model_id)
        if not e:
            raise ModelNotFound(model_id)
        old_path = e.get("path")
        fam = e.get("family", "misc")
        fam_dir = self.models_dir / fam
        res = download(source, str(fam_dir), expected_sha256=expected_sha256,
                       job=job, roots=self.roots)
        new_path = res["path"]
        rollback = None
        if old_path and os.path.exists(old_path) and old_path != new_path:
            rollback = str(old_path) + ".rollback"
            shutil.copy2(old_path, rollback)
        self.registry.update(model_id, {
            "path": new_path, "size_bytes": Path(new_path).stat().st_size,
            "verified": bool(res["verified"]),
            "updated_at": time.time(), "rollback_path": rollback})
        return self.registry.get(model_id)

    def rollback(self, model_id: str) -> dict:
        e = self.registry.get(model_id)
        if not e:
            raise ModelNotFound(model_id)
        rb = e.get("rollback_path")
        if not rb or not os.path.exists(rb):
            raise ModelNotFound("no rollback available for model")
        self.registry.update(model_id, {"path": rb, "verified": False})
        return self.registry.get(model_id)

    def remove(self, model_id: str, *, delete_files: bool = False) -> dict:
        e = self.registry.get(model_id)
        if not e:
            raise ModelNotFound(model_id)
        path = e.get("path")
        if delete_files and path and os.path.exists(path):
            os.remove(path)
        self.registry.mark_unverified(model_id, "removed")
        return {"removed": True, "model_id": model_id,
                "files_deleted": delete_files and bool(path)}
