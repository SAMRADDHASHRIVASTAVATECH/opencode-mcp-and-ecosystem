"""Gradle, ADB, emulator, APK adapters."""

from __future__ import annotations

import os
import re
import time
from pathlib import Path
from typing import Any

from android_mcp.env import detect, require_adb, require_sdk_tool, which
from android_mcp.errors import DependencyMissing, ExternalError, ValidationError
from android_mcp.inspect import find_root
from android_mcp.runner import run_cmd
from android_mcp.security import check_shell

GRADLE_TASKS = {
    "assembleDebug": "assembleDebug",
    "assembleRelease": "assembleRelease",
    "bundleRelease": "bundleRelease",
    "bundleDebug": "bundleDebug",
    "test": "test",
    "lint": "lint",
    "clean": "clean",
    "dependencies": "app:dependencies",
    "signingReport": "signingReport",
    "tasks": "tasks",
}


def gradle(project: Path, task: str, extra: list[str] | None = None, timeout: int = 300) -> dict[str, Any]:
    root = find_root(project)
    envinfo = detect()
    wrapper = root / "gradlew"
    jar = root / "gradle" / "wrapper" / "gradle-wrapper.jar"
    args: list[str]
    if wrapper.exists() and os.access(wrapper, os.X_OK) and jar.exists():
        args = [str(wrapper), task]
    elif wrapper.exists() and which("gradle"):
        args = ["gradle", task]
    elif which("gradle"):
        args = ["gradle", task]
    else:
        raise DependencyMissing(
            "Cannot run Gradle: no gradle-wrapper.jar and no gradle on PATH. "
            "Install JDK 17 + Gradle or Android Studio, then `gradle wrapper` in the project.",
            {"missing": envinfo.get("missing"), "root": str(root), "wrapper_jar": jar.exists()},
        )
    if extra:
        args.extend(extra)
    if envinfo.get("sdk_root"):
        os.environ.setdefault("ANDROID_HOME", envinfo["sdk_root"])
        os.environ.setdefault("ANDROID_SDK_ROOT", envinfo["sdk_root"])
    result = run_cmd(args, cwd=str(root), timeout=timeout)
    if not result["ok"]:
        from android_mcp.diagnostics import analyze_build_log

        result["analysis"] = analyze_build_log((result["stderr"] or "") + "\n" + (result["stdout"] or ""))
    artifacts = []
    for pat in ("**/*.apk", "**/*.aab"):
        artifacts.extend(str(p) for p in root.glob(pat) if "build/outputs" in str(p))
    result["artifacts"] = artifacts[-20:]
    result["task"] = task
    result["root"] = str(root)
    return result


def adb(args: list[str], timeout: int = 60, serial: str | None = None) -> dict[str, Any]:
    bin_ = require_adb()
    cmd = [bin_]
    if serial:
        cmd += ["-s", serial]
    cmd += args
    return run_cmd(cmd, timeout=timeout)


def list_devices() -> dict[str, Any]:
    r = adb(["devices", "-l"])
    devices = []
    for line in (r["stdout"] or "").splitlines()[1:]:
        line = line.strip()
        if not line:
            continue
        parts = line.split()
        serial = parts[0]
        state = parts[1] if len(parts) > 1 else "unknown"
        kind = "emulator" if serial.startswith("emulator-") else "physical"
        devices.append({"serial": serial, "state": state, "kind": kind, "raw": line})
    return {"devices": devices, "count": len(devices), "has_ready": any(d["state"] == "device" for d in devices)}


def pick_serial(serial: str | None) -> str | None:
    if serial:
        return serial
    data = list_devices()
    ready = [d for d in data["devices"] if d["state"] == "device"]
    if not ready:
        return None
    return ready[0]["serial"]


def list_avds() -> dict[str, Any]:
    emu = which("emulator") or detect().get("emulator")
    if emu:
        r = run_cmd([str(emu), "-list-avds"], timeout=20)
        names = [ln.strip() for ln in (r["stdout"] or "").splitlines() if ln.strip()]
        return {"avds": names, "emulator": emu}
    try:
        avd = require_sdk_tool("avdmanager")
    except DependencyMissing:
        raise DependencyMissing("Neither emulator nor avdmanager found. Install Android SDK emulator package.")
    r = run_cmd([avd, "list", "avd"], timeout=20)
    names = re.findall(r"Name:\s+(\S+)", r["stdout"] or "")
    return {"avds": names, "avdmanager": avd}


def start_avd(name: str, headless: bool = True) -> dict[str, Any]:
    emu = detect().get("emulator") or which("emulator")
    if not emu:
        raise DependencyMissing("Android emulator binary not found")
    args = [emu, "-avd", name]
    if headless:
        args += ["-no-window", "-no-audio", "-gpu", "swiftshader_indirect"]
    # Don't wait forever; spawn
    import subprocess

    log = Path("/tmp") / f"avd-{name}.log"
    proc = subprocess.Popen(args, stdout=open(log, "w"), stderr=subprocess.STDOUT)
    return {"pid": proc.pid, "name": name, "log": str(log), "note": "Wait for boot then android_devices"}


def inspect_apk(path: Path) -> dict[str, Any]:
    info: dict[str, Any] = {"path": str(path), "size": path.stat().st_size if path.exists() else None}
    analyzer = detect().get("apkanalyzer")
    if analyzer:
        for sub in (["manifest", "print"], ["files", "list"], ["dex", "packages"]):
            r = run_cmd([analyzer] + sub + [str(path)], timeout=30)
            info["/".join(sub)] = (r["stdout"] or "")[:8000]
        return info
    # zip fallback
    import zipfile

    if not zipfile.is_zipfile(path):
        raise ValidationError("Not a zip/APK/AAB")
    with zipfile.ZipFile(path) as zf:
        names = zf.namelist()
        info["entries"] = len(names)
        info["has_dex"] = any(n.endswith(".dex") for n in names)
        info["has_manifest"] = "AndroidManifest.xml" in names
        info["sample"] = names[:40]
    # apksigner verify
    sdk = detect().get("sdk_root")
    if sdk:
        bt = Path(sdk) / "build-tools"
        signer = None
        if bt.exists():
            versions = sorted(bt.iterdir(), reverse=True)
            for v in versions:
                cand = v / "apksigner"
                if cand.exists():
                    signer = str(cand)
                    break
        if signer:
            r = run_cmd([signer, "verify", "--verbose", str(path)], timeout=30)
            info["signature"] = {"ok": r["ok"], "output": (r["stdout"] or r["stderr"])[:4000]}
    return info
