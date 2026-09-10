"""Detect JDK, Android SDK, Gradle, devices — never assume."""

from __future__ import annotations

import os
import re
import shutil
from pathlib import Path
from typing import Any

from android_mcp.runner import run_cmd

SDK_CANDIDATES = [
    Path(os.environ["ANDROID_HOME"]) if os.environ.get("ANDROID_HOME") else None,
    Path(os.environ["ANDROID_SDK_ROOT"]) if os.environ.get("ANDROID_SDK_ROOT") else None,
    Path.home() / "Android" / "Sdk",
    Path.home() / "Library" / "Android" / "sdk",
    Path(os.environ.get("LOCALAPPDATA", "")) / "Android" / "Sdk" if os.environ.get("LOCALAPPDATA") else None,
    Path("/opt/android-sdk"),
    Path("/usr/lib/android-sdk"),
]


def which(name: str) -> str | None:
    return shutil.which(name)


def _first_existing(paths: list[Path | None]) -> Path | None:
    for p in paths:
        if p and p.exists():
            return p.resolve()
    return None


def find_sdk() -> Path | None:
    return _first_existing(SDK_CANDIDATES)


def _sdk_bin(sdk: Path, *parts: str) -> str | None:
    p = sdk.joinpath(*parts)
    if p.exists():
        return str(p)
    # Windows .bat
    bat = p.with_suffix(".bat")
    if bat.exists():
        return str(bat)
    return None


def java_info() -> dict[str, Any]:
    java = which("java")
    home = os.environ.get("JAVA_HOME")
    version = None
    major = None
    if java:
        r = run_cmd([java, "-version"], timeout=10)
        text = (r["stderr"] or r["stdout"] or "")
        m = re.search(r'version "([^"]+)"', text)
        version = m.group(1) if m else text.splitlines()[0] if text else None
        if version:
            maj = version.split(".")[0]
            if maj == "1":
                major = int(version.split(".")[1]) if "." in version else None
            else:
                try:
                    major = int(re.match(r"\d+", version).group(0))  # type: ignore
                except Exception:
                    major = None
    return {
        "java": java,
        "java_home": home,
        "version": version,
        "major": major,
        "agp8_ok": bool(major and major >= 17),
        "note": None
        if (major and major >= 17)
        else "AGP 8.x requires JDK 17+. Install Temurin 17+ and set JAVA_HOME.",
    }


def detect() -> dict[str, Any]:
    sdk = find_sdk()
    adb = which("adb") or (str(sdk / "platform-tools" / "adb") if sdk and (sdk / "platform-tools" / "adb").exists() else None)
    emulator = which("emulator") or (
        _sdk_bin(sdk, "emulator", "emulator") if sdk else None
    )
    sdkmanager = None
    avdmanager = None
    apkanalyzer = None
    if sdk:
        for ver in ("latest", "latest-2"):
            sdkmanager = sdkmanager or _sdk_bin(sdk, "cmdline-tools", ver, "bin", "sdkmanager")
            avdmanager = avdmanager or _sdk_bin(sdk, "cmdline-tools", ver, "bin", "avdmanager")
            apkanalyzer = apkanalyzer or _sdk_bin(sdk, "cmdline-tools", ver, "bin", "apkanalyzer")
        # older tools/bin
        sdkmanager = sdkmanager or _sdk_bin(sdk, "tools", "bin", "sdkmanager")
        avdmanager = avdmanager or _sdk_bin(sdk, "tools", "bin", "avdmanager")
    build_tools = []
    platforms = []
    ndk = []
    if sdk:
        bt = sdk / "build-tools"
        if bt.exists():
            build_tools = sorted([p.name for p in bt.iterdir() if p.is_dir()])
        pf = sdk / "platforms"
        if pf.exists():
            platforms = sorted([p.name for p in pf.iterdir() if p.is_dir()])
        nd = sdk / "ndk"
        if nd.exists():
            ndk = sorted([p.name for p in nd.iterdir() if p.is_dir()])
    gradle = which("gradle")
    studio = which("studio") or which("android-studio")
    missing = []
    if not java_info().get("java"):
        missing.append("JDK (java)")
    elif not java_info().get("agp8_ok"):
        missing.append("JDK 17+ (found older Java)")
    if not sdk:
        missing.append("Android SDK (ANDROID_HOME)")
    if not adb:
        missing.append("adb (platform-tools)")
    j = java_info()
    return {
        "os": os.name,
        "platform": __import__("platform").platform(),
        "java": j,
        "sdk_root": str(sdk) if sdk else None,
        "adb": adb if adb and Path(adb).exists() or which("adb") else which("adb"),
        "emulator": emulator,
        "sdkmanager": sdkmanager,
        "avdmanager": avdmanager,
        "apkanalyzer": apkanalyzer,
        "gradle": gradle,
        "android_studio": studio,
        "build_tools": build_tools,
        "platforms": platforms,
        "ndk": ndk,
        "cmake": which("cmake"),
        "kotlin_compiler": which("kotlinc"),
        "env": {
            "ANDROID_HOME": os.environ.get("ANDROID_HOME"),
            "ANDROID_SDK_ROOT": os.environ.get("ANDROID_SDK_ROOT"),
            "JAVA_HOME": os.environ.get("JAVA_HOME"),
            "ANDROID_AVD_HOME": os.environ.get("ANDROID_AVD_HOME"),
        },
        "missing": missing,
        "can_scaffold": True,
        "can_build": bool(sdk and j.get("agp8_ok")),
        "can_device": bool(which("adb") or (adb and Path(str(adb)).exists())),
        "recommended_compile_sdk": _highest_platform(platforms),
        "install_hints": _hints(missing, sdk),
    }


def _highest_platform(platforms: list[str]) -> int | None:
    nums = []
    for p in platforms:
        m = re.search(r"android-(\d+)", p)
        if m:
            nums.append(int(m.group(1)))
    return max(nums) if nums else None


def _hints(missing: list[str], sdk: Path | None) -> list[str]:
    hints = []
    if any("JDK" in m for m in missing):
        hints.append("Install JDK 17+: https://adoptium.net/ and export JAVA_HOME")
    if any("SDK" in m for m in missing):
        hints.append(
            "Install command-line tools from https://developer.android.com/studio#command-tools "
            "unpack to $ANDROID_HOME/cmdline-tools/latest then: "
            'sdkmanager "platform-tools" "platforms;android-35" "build-tools;35.0.0" "emulator"'
        )
    if any("adb" in m for m in missing):
        hints.append('sdkmanager "platform-tools"  OR  apt/brew install android-platform-tools')
    return hints


def require_adb() -> str:
    info = detect()
    adb = info.get("adb") or which("adb")
    if not adb:
        from android_mcp.errors import DependencyMissing

        raise DependencyMissing(
            "adb is not installed. Device operations need Android platform-tools.",
            {"install_hints": info.get("install_hints"), "missing": info.get("missing")},
        )
    return adb


def require_sdk_tool(name: str) -> str:
    info = detect()
    path = info.get(name)
    if not path:
        from android_mcp.errors import DependencyMissing

        raise DependencyMissing(
            f"{name} not found on this machine.",
            {"missing": info.get("missing"), "install_hints": info.get("install_hints")},
        )
    return str(path)
