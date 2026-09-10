from __future__ import annotations

import re
from pathlib import Path

from android_mcp.config import SETTINGS, Settings
from android_mcp.errors import NotFoundError, PolicyError, ValidationError

SHELL_ALLOW = (
    "pm ",
    "am ",
    "dumpsys ",
    "getprop",
    "settings get",
    "wm ",
    "input keyevent",
    "screencap",
    "ps ",
    "log",
    "cmd package",
    "cmd activity",
    "cmd window",
    "toybox id",
    "id",
    "echo",
    "cat /proc/meminfo",
    "cat /proc/cpuinfo",
)
SHELL_DENY = re.compile(
    r"\b(rm|reboot|su|dd|fastboot|wipe|chmod\s+777|setprop|mkfs|format|reboot\s+-p)\b",
    re.I,
)


def safe_path(path: str | Path, *, must_exist: bool = False, settings: Settings | None = None) -> Path:
    settings = settings or SETTINGS
    if not path:
        raise ValidationError("Path is required")
    raw = Path(str(path)).expanduser()
    candidate = (raw if raw.is_absolute() else settings.root / raw).resolve()
    try:
        candidate.relative_to(settings.root)
    except ValueError as exc:
        raise PolicyError(
            "Path is outside ANDROID_MCP_ROOT sandbox",
            {"path": str(path), "root": str(settings.root)},
        ) from exc
    if must_exist and not candidate.exists():
        raise NotFoundError(f"Not found: {candidate}")
    return candidate


def ensure_writable(settings: Settings | None = None) -> None:
    if (settings or SETTINGS).read_only:
        raise PolicyError("Server is read-only (ANDROID_MCP_READ_ONLY)")


def check_overwrite(path: Path, overwrite: bool) -> None:
    if path.exists() and not overwrite:
        raise ValidationError("Path exists; pass overwrite=true", {"path": str(path)})


def require_confirm(confirm: bool, action: str) -> None:
    if not confirm:
        raise PolicyError(f"{action} requires confirm=true")


def check_shell(command: str) -> str:
    cmd = command.strip()
    if not cmd:
        raise ValidationError("Empty shell command")
    if SHELL_DENY.search(cmd):
        raise PolicyError("Shell command matches deny list", {"command": cmd[:80]})
    low = cmd.lower()
    if not any(low.startswith(p) or low == p.strip() for p in SHELL_ALLOW):
        raise PolicyError(
            "adb shell is allowlisted. Use android_app / android_profile / android_logcat instead of arbitrary shell.",
            {"command": cmd[:120]},
        )
    return cmd
