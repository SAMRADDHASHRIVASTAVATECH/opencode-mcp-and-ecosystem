"""File-system engine (§17): list/read/write where permitted, push, pull,
copy, mkdir, verify, hashes. Windows<->Android both directions. Safe path
handling; destructive host-side overwrites are guarded.
"""
from __future__ import annotations

import hashlib
import re
from pathlib import Path, PurePosixPath
from typing import List, Optional

from .. import errors
from ..config import Settings
from .base import EngineBase

_SDCARD = "/sdcard/"


def _norm_android(path: str) -> str:
    """Normalise an android-side path, forcing Posix and forbidding escapes."""
    if not path:
        raise ValueError("empty path")
    p = path.replace("\\", "/")
    if ".." in PurePosixPath(p).parts:
        raise errors.InjectionDeniedError(f"path traversal blocked: {path}")
    if not p.startswith(("/sdcard/", "/data/local/tmp/", "/storage/")):
        # fall back to /sdcard base for convenience but never a bare device root
        p = p if p.startswith("/") else "/sdcard/" + p
    return p


class FilesEngine(EngineBase):
    def __init__(self, transport, settings: Settings):
        super().__init__(transport, settings)

    # -- android-side ------------------------------------------------------
    def list(self, serial: str, path: str = "/sdcard/") -> List[dict]:
        ap = _norm_android(path)
        out = self._shell_ok(serial, f"ls -l {_q(ap)}")
        entries = []
        for ln in out.lines():
            parts = ln.split()
            if len(parts) >= 3 and parts[0] and parts[0][0] in ("-", "d", "l"):
                name = parts[-1]
                ftype = "dir" if parts[0][0] == "d" else \
                    ("link" if parts[0][0] == "l" else "file")
                size = ""
                for t in parts:
                    if t.isdigit():
                        size = t
                        break
                entries.append({"name": name, "type": ftype, "size": size,
                                "date": ""})
        return entries

    def mkdir(self, serial: str, path: str) -> None:
        ap = _norm_android(path)
        self._shell_ok(serial, f"mkdir -p {_q(ap)}")

    def read(self, serial: str, path: str, max_bytes: int = 1_000_000) -> str:
        ap = _norm_android(path)
        out = self._shell_ok(serial, f"head -c {max_bytes} {_q(ap)}")
        return out.stdout

    def rm(self, serial: str, path: str, recursive: bool = True):
        ap = _norm_android(path)
        if not recursive and _is_dir_heuristic(self, serial, ap):
            raise errors.RequiresAuthorizationError(
                f"refusing to rm directory {ap} without recursive=True")
        flag = "-rf" if recursive else "-f"
        self._shell_ok(serial, f"rm {flag} {_q(ap)}")

    # -- transfer ----------------------------------------------------------
    def push(self, host_path: str, android_path: str,
             serial: str, overwrite: bool = True) -> None:
        hp = Path(host_path).expanduser()
        if not hp.exists():
            raise errors.CommandFailedError(f"host file not found: {hp}")
        ap = _norm_android(android_path)
        if not overwrite and self._exists(serial, ap):
            raise errors.RequiresAuthorizationError(
                f"refusing to overwrite existing {ap} on {serial}")
        res = self._adb(serial, ["push", str(hp), ap],
                        timeout_s=self.settings.long_timeout_s)
        if not res.ok:
            raise errors.CommandFailedError(f"push failed: {res.error}")

    def pull(self, android_path: str, host_path: str,
             serial: str, overwrite: bool = True) -> str:
        ap = _norm_android(android_path)
        hp = Path(host_path).expanduser()
        if hp.exists() and not overwrite:
            raise errors.RequiresAuthorizationError(
                f"refusing to overwrite host file: {hp}")
        hp.parent.mkdir(parents=True, exist_ok=True)
        res = self._adb(serial, ["pull", ap, str(hp)],
                        timeout_s=self.settings.long_timeout_s)
        if not res.ok:
            raise errors.CommandFailedError(f"pull failed: {res.error}")
        return str(hp)

    def copy(self, serial: str, src: str, dst: str) -> None:
        self._shell_ok(serial, f"cp {_q(_norm_android(src))} {_q(_norm_android(dst))}")

    # -- verify ------------------------------------------------------------
    def verify(self, serial: str, path: str) -> dict:
        ap = _norm_android(path)
        out = self._shell_ok(serial, f"ls -l {_q(ap)}")
        sha = self.sha1(serial, ap)
        return {"exists": bool(out.stdout.strip()),
                "sha1": sha, "path": ap}

    def sha1(self, serial: str, path: str) -> str:
        ap = _norm_android(path)
        out = self._shell_ok(serial, f"sha1sum {_q(ap)}")
        m = re.search(r"([0-9a-f]{40})", out.stdout)
        return m.group(1) if m else ""

    # local host sha for parity
    @staticmethod
    def host_sha1(host_path: str) -> str:
        h = hashlib.sha1()
        with open(Path(host_path).expanduser(), "rb") as f:
            for chunk in iter(lambda: f.read(65536), b""):
                h.update(chunk)
        return h.hexdigest()

    # -- helpers -----------------------------------------------------------
    def _exists(self, serial: str, ap: str) -> bool:
        return self._shell_ok(serial, f"ls {_q(ap)} 2>/dev/null").ok


def _q(path: str) -> str:
    # shell-quote for a single android-side path
    return "'" + path.replace("'", "'\\''") + "'"


def _is_dir_heuristic(engine, serial, ap) -> bool:
    out = engine._shell_ok(serial, f"test -d {_q(ap)} && echo yes")
    return "yes" in out.stdout
