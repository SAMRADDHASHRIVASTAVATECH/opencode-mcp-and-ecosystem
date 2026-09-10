from __future__ import annotations

import os
import re
import subprocess
from typing import Any

from se_mcp.errors import ExternalError

_SECRET = re.compile(r"(pass(word)?|secret|token|key)=([^\s]+)", re.I)


def redact(text: str) -> str:
    return _SECRET.sub(r"\1=***", text or "")


def run_cmd(args: list[str], *, cwd: str | None = None, timeout: int = 60, env: dict[str, str] | None = None) -> dict[str, Any]:
    merged = os.environ.copy()
    if env:
        merged.update(env)
    try:
        proc = subprocess.run(args, cwd=cwd, env=merged, capture_output=True, text=True, timeout=timeout, check=False)
    except FileNotFoundError as exc:
        raise ExternalError(f"Executable not found: {args[0]}", {"args": args[:4]}) from exc
    except subprocess.TimeoutExpired as exc:
        raise ExternalError(f"Timed out: {args[0]}", {"timeout": timeout}) from exc
    return {
        "args": args,
        "returncode": proc.returncode,
        "stdout": redact(proc.stdout or "")[-60_000:],
        "stderr": redact(proc.stderr or "")[-60_000:],
        "ok": proc.returncode == 0,
        "cwd": cwd,
    }
