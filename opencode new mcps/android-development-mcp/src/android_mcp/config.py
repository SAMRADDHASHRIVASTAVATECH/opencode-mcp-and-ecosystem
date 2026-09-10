from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path


def _bool(name: str, default: bool = False) -> bool:
    raw = os.environ.get(name)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}


def _int(name: str, default: int) -> int:
    raw = os.environ.get(name)
    if not raw:
        return default
    try:
        return int(raw)
    except ValueError:
        return default


# Conservative 2026 defaults. Overridden when SDK platforms are detected.
DEFAULTS = {
    "agp": "8.7.3",
    "kotlin": "2.0.21",
    "gradle": "8.11.1",
    "compose_bom": "2025.01.01",
    "compile_sdk": 35,
    "target_sdk": 35,
    "min_sdk": 26,
    "core_ktx": "1.15.0",
    "lifecycle": "2.8.7",
    "activity_compose": "1.9.3",
    "activity": "1.9.3",
    "appcompat": "1.7.0",
    "material": "1.12.0",
    "constraintlayout": "2.2.0",
    "navigation": "2.8.5",
    "junit": "4.13.2",
    "androidx_junit": "1.2.1",
    "espresso": "3.6.1",
    "room": "2.6.1",
    "retrofit": "2.11.0",
    "okhttp": "4.12.0",
    "coroutines": "1.9.0",
    "ksp": "2.0.21-1.0.28",
}


@dataclass(frozen=True)
class Settings:
    root: Path
    read_only: bool
    timeout: int
    logcat_lines: int
    allow_sdk_install: bool
    keystore_pass_env: str
    defaults: dict[str, object] = field(default_factory=lambda: dict(DEFAULTS))

    @classmethod
    def load(cls) -> "Settings":
        return cls(
            root=Path(os.environ.get("ANDROID_MCP_ROOT") or os.getcwd()).resolve(),
            read_only=_bool("ANDROID_MCP_READ_ONLY", False),
            timeout=_int("ANDROID_MCP_TIMEOUT", 180),
            logcat_lines=_int("ANDROID_MCP_LOGCAT_LINES", 200),
            allow_sdk_install=_bool("ANDROID_MCP_ALLOW_SDK_INSTALL", False),
            keystore_pass_env="ANDROID_MCP_KEYSTORE_PASS",
        )


SETTINGS = Settings.load()
