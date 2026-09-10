"""Master prompt build: `android-control` skill.

Environment-driven configuration for the Universal Android Control system.

All settings are read from ``AC_``-prefixed environment variables (or a local
``.env``) and never require a human to hand-type a single ADB command.
"""
from __future__ import annotations

import os
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import List, Optional


def _s(name: str, default: str = "") -> str:
    return os.environ.get("AC_" + name, default)


def _b(name: str, default: bool) -> bool:
    v = os.environ.get("AC_" + name)
    if v is None:
        return default
    return v.strip().lower() in {"1", "true", "yes", "on"}


def _i(name: str, default: int) -> int:
    try:
        return int(os.environ.get("AC_" + name, default))
    except (TypeError, ValueError):
        return default


def _f(name: str, default: float) -> float:
    try:
        return float(os.environ.get("AC_" + name, default))
    except (TypeError, ValueError):
        return default


@dataclass
class HostTool:
    """A host-side dependency the skill can detect / install."""
    name: str
    exe_names: List[str] = field(default_factory=list)
    verify_args: List[str] = field(default_factory=list)  # e.g. ["version"]
    min_version: str = ""
    install_cmd: List[str] = field(default_factory=list)
    source: str = ""          # official/trustworthy distribution source
    installed: bool = False
    version: str = ""
    exe_path: str = ""


@dataclass
class Settings:
    """Master settings. Nothing here requires manual translation to ADB."""
    # tool discovery / auto-install
    auto_install: bool = _b("AUTO_INSTALL", True)
    allow_auto_install: bool = _b("ALLOW_AUTO_INSTALL", True)
    platform_tools_dir: str = _s("PLATFORM_TOOLS_DIR", "")  # explicit ADB root
    adb_path: str = _s("ADB_PATH", "")                      # explicit adb exe
    scrcpy_path: str = _s("SCRCPY_PATH", "")
    install_dir: str = _s("INSTALL_DIR", os.path.join(
        os.path.expanduser("~"), ".android_control", "tools"))

    # device connection
    wireless: bool = _b("WIRELESS", True)       # prefer wireless debugging
    adb_tcp_port: int = _i("ADB_TCP_PORT", 5555)
    adb_connect_timeout_s: int = _i("CONNECT_TIMEOUT", 15)
    default_pair_port: int = _i("PAIR_PORT", 37000)
    auto_reconnect: bool = _b("AUTO_RECONNECT", True)
    recover_on_offline: bool = _b("RECOVER_ON_OFFLINE", True)

    # command safety
    default_timeout_s: int = _i("CMD_TIMEOUT", 30)
    long_timeout_s: int = _i("LONG_CMD_TIMEOUT", 120)
    require_auth_destructive: bool = _b("REQUIRE_AUTH_DESTRUCTIVE", True)

    # multi-device execution
    max_parallel: int = _i("MAX_PARALLEL", 0)   # 0 => auto by core count
    poll_interval_s: float = _f("POLL_INTERVAL", 0.5)

    # observation / vision fallback
    screenshot_dir: str = _s("SCREENSHOT_DIR", os.path.join(
        os.path.expanduser("~"), ".android_control", "media"))
    uiauto_timeout_ms: int = _i("UIAUTO_TIMEOUT", 6000)
    enable_vision_fallback: bool = _b("VISION_FALLBACK", True)
    vision_model_cmd: List[str] = field(default_factory=list)  # optional external
    vision_backend: str = _s("VISION_BACKEND", "offline")      # offline|external

    # offline / mock (deterministic, no hardware)
    offline: bool = _b("OFFLINE", False)
    mock_devices: List[str] = field(default_factory=lambda: _mock_list())

    # ---- Remote Touchpad companion backend (phone-as-PC-touchpad) ---------
    # This is the GPLv3 Unrud/remote-touchpad host (see third_party/). It runs
    # on the Windows PC and lets an authorized phone control the PC's pointer
    # and keyboard. It is a separate direction from the ADB Android-control
    # engine and is disabled unless AC_RT_ENABLED=true.
    rt_enabled: bool = _b("RT_ENABLED", False)
    rt_bin: str = _s("RT_BIN", "")          # path to remote-touchpad exe
    rt_autodownload: bool = _b("RT_AUTODOWNLOAD", True)
    rt_port: int = _i("RT_PORT", 0)          # 0 => ephemeral (default :0)
    rt_bind: str = _s("RT_BIND", ":0")
    rt_secret: str = _s("RT_SECRET", "")     # empty => random challenge each run
    rt_release: str = _s("RT_RELEASE", "v1.5.4")

    # logging
    log_dir: str = _s("LOG_DIR", os.path.join(
        os.path.expanduser("~"), ".android_control", "logs"))
    debug: bool = _b("DEBUG", False)
    redact_secrets: bool = _b("REDACT_SECRETS", True)

    def to_dict(self, redact: bool = True) -> dict:
        d = asdict(self)
        if redact:
            for k in ("adb_path", "scrcpy_path", "install_dir",
                      "screenshot_dir", "log_dir"):
                pass
        return d


def _mock_list() -> List[str]:
    raw = _s("MOCK_DEVICES", "")
    if raw:
        return [x.strip() for x in raw.split(",") if x.strip()]
    # A small deterministic fleet used by --offline and selfchecks.
    return ["1A7F20090001_Pixel8_mock", "2B3G30080002_Samsung_mock",
            "3C4H40070003_Pixel9_mock", "4D5J50060004_OnePlus_mock"]


def _package_env_path() -> Optional[Path]:
    here = Path(__file__).resolve().parent
    for cand in (Path.cwd() / ".env", here.parent.parent.parent / ".env"):
        if cand.exists():
            return cand
    return None


def _load_dotenv(path: Path):
    if not path:
        return
    try:
        for line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            k, v = k.strip(), v.strip().strip('"').strip("'")
            if k and k not in os.environ:
                os.environ.setdefault(k, v)
    except Exception:
        pass


def load_settings() -> Settings:
    envp = _package_env_path()
    if envp:
        _load_dotenv(envp)
    return Settings()


def save_env_example() -> str:
    lines = [
        "# Universal Android Control - environment (all optional)",
        "# Force deterministic offline/mock mode (no real hardware):",
        "AC_OFFLINE=false",
        "# Explicit paths to host tools (discovered automatically if unset):",
        "AC_ADB_PATH=",
        "AC_SCRCPY_PATH=",
        "AC_PLATFORM_TOOLS_DIR=",
        "# Device connection",
        "AC_WIRELESS=true",
        "AC_ADB_TCP_PORT=5555",
        "AC_AUTO_RECONNECT=true",
        "AC_RECOVER_ON_OFFLINE=true",
        "# Host tooling auto-install",
        "AC_AUTO_INSTALL=true",
        "AC_INSTALL_DIR=%USERPROFILE%\\.android_control\\tools",
        "# Multi-device execution (0 = auto)",
        "AC_MAX_PARALLEL=0",
        "# Observation / vision fallback",
        "AC_SCREENSHOT_DIR=%USERPROFILE%\\.android_control\\media",
        "AC_VISION_BACKEND=offline",
        "# Safety",
        "AC_REQUIRE_AUTH_DESTRUCTIVE=true",
        "AC_DEFAULT_TIMEOUT=30",
        "AC_DEBUG=false",
        "# Mock device fleet (used with AC_OFFLINE=true)",
        "AC_MOCK_DEVICES=",
        "# Remote Touchpad companion (GPLv3, vendored in third_party/).",
        "# Runs on this PC; lets an authorized phone act as a wireless touchpad",
        "# + keyboard for the PC. This is the reverse direction (phone->PC).",
        "AC_RT_ENABLED=false",
        "AC_RT_BIN=",
        "AC_RT_AUTODOWNLOAD=true",
        "AC_RT_PORT=0",
        "AC_RT_BIND=:0",
        "AC_RT_RELEASE=v1.5.4",
    ]
    return "\n".join(lines) + "\n"
