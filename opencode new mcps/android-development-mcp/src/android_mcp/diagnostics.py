"""Analyze Gradle failures, crashes, ANRs — map to likely cause + next tool."""

from __future__ import annotations

import re
from typing import Any

RULES: list[tuple[str, str, str, list[str]]] = [
    (r"SDK location not found|sdk.dir", "Android SDK path missing (local.properties / ANDROID_HOME).", "DEPENDENCY_MISSING", ["android_detect_environment"]),
    (r"Failed to install the following Android SDK packages|Failed to accept", "SDK licenses or packages missing.", "DEPENDENCY_MISSING", ["android_sdk"]),
    (r"compileSdk.*requires.*Android Gradle plugin|We recommend using a newer Android Gradle plugin", "AGP too old for compileSdk.", "VALIDATION", ["android_manage_dependencies"]),
    (r"Android Gradle plugin requires Java 17|unrecognized.*release 17|invalid source release: 17", "JDK < 17. AGP 8 needs JDK 17+.", "DEPENDENCY_MISSING", ["android_detect_environment"]),
    (r"This version of the Android Support plugin|using an old version of the Android Gradle plugin", "Plugin/AGP mismatch.", "VALIDATION", ["android_inspect_project"]),
    (r"Compose Compiler|This version \(.*\) of the Compose Compiler is incompatible|kotlin.plugin.compose", "Compose compiler / Kotlin mismatch. Use org.jetbrains.kotlin.plugin.compose matching Kotlin.", "VALIDATION", ["android_inspect_project"]),
    (r"Unresolved reference|cannot find symbol", "Compilation: missing import, wrong package, or missing dependency.", "EXTERNAL", ["android_inspect_project"]),
    (r"Manifest merger failed", "Manifest merge conflict (exported, permissions, or library manifest).", "VALIDATION", ["android_modify_manifest", "android_security_audit"]),
    (r"Duplicate class|program type already present", "Duplicate dependency / transitive clash.", "EXTERNAL", ["android_gradle"]),
    (r"Execution failed for task ':.*:lint", "Lint failed.", "EXTERNAL", ["android_run_tests"]),
    (r"AAPT2|resource not found|No resource found that matches", "Resource / AAPT error.", "EXTERNAL", ["android_inspect_project"]),
    (r"Minification|R8|Missing class", "R8/ProGuard missing class.", "EXTERNAL", ["android_gradle"]),
    (r"INSTALL_FAILED", "APK install rejected by device.", "EXTERNAL", ["android_devices", "android_app"]),
    (r"device unauthorized|no devices/emulators found", "No authorized device.", "DEPENDENCY_MISSING", ["android_devices", "android_avd"]),
]


def analyze_build_log(log: str) -> dict[str, Any]:
    hits = []
    for pat, cause, code, next_tools in RULES:
        if re.search(pat, log, re.I):
            hits.append({"pattern": pat, "cause": cause, "code": code, "next_tools": next_tools})
    if not hits:
        hits.append(
            {
                "pattern": None,
                "cause": "Unrecognized Gradle failure. Inspect the last error line and android_inspect_project.",
                "code": "EXTERNAL",
                "next_tools": ["android_inspect_project", "android_detect_environment"],
            }
        )
    last_error = None
    for line in log.splitlines()[::-1]:
        if "error" in line.lower() or line.strip().startswith("FAILURE"):
            last_error = line.strip()[:500]
            break
    return {"matches": hits, "primary": hits[0], "last_error_line": last_error}


CRASH_PATTERNS = [
    (r"FATAL EXCEPTION:.*?(\n.*)*?Caused by: ([^\n]+)", "exception"),
    (r"AndroidRuntime:.*?(\w+(?:\.\w+)+Exception[^\n]*)", "exception"),
    (r"Process: ([^\s,]+)", "process"),
]


def analyze_crash(log: str) -> dict[str, Any]:
    fatal = "FATAL EXCEPTION" in log or "Fatal signal" in log
    anr = "ANR in" in log or "Application Not Responding" in log
    process = None
    m = re.search(r"Process:\s+([^\s,]+)", log)
    if m:
        process = m.group(1)
    exc = None
    m = re.search(r"(Caused by: )?([a-zA-Z0-9_.]+(?:Exception|Error): [^\n]+)", log)
    if m:
        exc = m.group(2)
    likely = []
    if "SecurityException" in log or "Permission Denial" in log:
        likely.append("Missing or denied permission — android_modify_manifest / pm grant")
    if "ClassNotFoundException" in log or "NoClassDefFoundError" in log:
        likely.append("Missing class / minify — check R8 and dependencies")
    if "InflateException" in log:
        likely.append("XML layout inflate failure")
    if "IllegalStateException" in log and "Fragment" in log:
        likely.append("Fragment lifecycle")
    if anr:
        likely.append("Main thread blocked — inspect android_profile dumpsys activity / cpuinfo")
    if "NetworkSecurityConfig" in log or "CLEARTEXT" in log:
        likely.append("Cleartext HTTP blocked — network security config")
    return {
        "fatal": fatal,
        "anr": anr,
        "process": process,
        "exception": exc,
        "likely_causes": likely or ["See stack trace; capture a fuller logcat with android_logcat"],
        "next_tools": ["android_logcat", "android_inspect_project", "android_security_audit"],
    }
