"""Resumable, verifiable file downloader (model files).

- streaming to a temp file
- resume from an interrupted download when the server supports Range
- optional sha256 verification (never *claims* verification without a hash)
- disk check delegated to storage helpers
- atomic finalize (rename only after success)
No secrets logged. Uses the allowed model_download_roots when configured.
"""
from __future__ import annotations

import hashlib
import os
from pathlib import Path
from urllib.parse import urlparse

from ..errors import ModelDownloadFailed, NotAuthorized
from ..storage import disk_free_gb


def _allowed(url: str, roots: list[str]) -> None:
    if not roots:
        return
    host = urlparse(url).netloc.lower()
    for r in roots:
        if r and (host == r.lower() or host.endswith("." + r.lower())):
            return
    raise NotAuthorized(f"download host '{host}' not in allowed model_download_roots")


def sha256_of(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def download(url: str, dest_dir: str, *, expected_sha256: str = "",
             resume: bool = True, job=None, roots: list[str] | None = None,
             timeout: float = 60.0) -> dict:
    _allowed(url, roots or [])
    import requests
    dest = Path(dest_dir)
    dest.mkdir(parents=True, exist_ok=True)
    filename = Path(urlparse(url).path).name or "download.bin"
    tmp_path = dest / (".part-" + filename)
    final = dest / filename

    # already present and matches hash -> done
    if final.exists():
        if expected_sha256:
            if sha256_of(str(final)) == expected_sha256:
                return {"path": str(final), "bytes": final.stat().st_size,
                        "verified": True, "fresh": False}
            final.unlink()
        else:
            return {"path": str(final), "bytes": final.stat().st_size,
                    "verified": None, "fresh": False}

    free = disk_free_gb(dest)
    if job:
        job.append_log(f"downloading {filename} (free disk ~{free}GB)")

    headers = {}
    if resume and tmp_path.exists():
        headers["Range"] = "bytes=%d-" % tmp_path.stat().st_size
    if job:
        job.append_log("starting/resuming download")
    try:
        with requests.get(url, stream=True, headers=headers, timeout=timeout) as r:
            if r.status_code == 416:
                r.close()
            elif r.status_code in (200, 206):
                mode = "ab" if (r.status_code == 206 and resume) else "wb"
                total = int(r.headers.get("Content-Length", 0))
                done = tmp_path.stat().st_size if mode == "ab" else 0
                with open(tmp_path, mode) as f:
                    for chunk in r.iter_content(1 << 20):
                        if not chunk:
                            continue
                        f.write(chunk)
                        done += len(chunk)
                        if job and total:
                            job.progress_percent = round(100.0 * done /
                                                         max(total, 1), 1)
                hash_val = sha256_of(str(tmp_path))
                if expected_sha256 and hash_val != expected_sha256:
                    tmp_path.unlink(missing_ok=True)
                    raise ModelDownloadFailed(
                        f"sha256 mismatch for {filename}")
                os.replace(tmp_path, final)
                return {"path": str(final), "bytes": final.stat().st_size,
                        "verified": bool(expected_sha256), "fresh": True,
                        "hash": hash_val if expected_sha256 else None}
            else:
                raise ModelDownloadFailed(f"HTTP {r.status_code} downloading {url}")
    except requests.RequestException as e:
        raise ModelDownloadFailed(f"download error: {e}") from None
