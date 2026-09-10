"""Static Android security review of project sources/manifest."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from android_mcp.inspect import find_root, inspect_project

SECRET = re.compile(
    r"(api[_-]?key|secret|password|token)\s*[:=]\s*['\"][^'\"]{8,}['\"]",
    re.I,
)
IP = re.compile(r"https?://\d+\.\d+\.\d+\.\d+")


def audit(project: Path) -> dict[str, Any]:
    root = find_root(project)
    report = inspect_project(root)
    findings: list[dict[str, Any]] = []
    mpath = report.get("manifest")
    mtxt = Path(mpath).read_text(encoding="utf-8") if mpath and Path(mpath).exists() else ""

    if report.get("debuggable"):
        findings.append({"sev": "high", "id": "debuggable", "msg": "android:debuggable=true in manifest"})
    if "usesCleartextTraffic=\"true\"" in mtxt:
        findings.append({"sev": "high", "id": "cleartext", "msg": "Cleartext HTTP allowed on application"})
    if not report.get("has_network_security_config"):
        findings.append({"sev": "medium", "id": "nsc", "msg": "No networkSecurityConfig; add one to block cleartext"})
    if report.get("allow_backup"):
        findings.append({"sev": "low", "id": "backup", "msg": "allowBackup=true — exclude secrets from backup"})

    for kind, tag in (("activity", "activity"), ("service", "service"), ("receiver", "receiver"), ("provider", "provider")):
        for block in re.findall(rf"<{tag}\b[^>]*>", mtxt):
            exported = 'android:exported="true"' in block
            name = re.search(r'android:name="([^"]+)"', block)
            perm = "android:permission=" in block
            if exported and not perm and "MAIN" not in block:
                findings.append(
                    {
                        "sev": "high" if tag != "activity" else "medium",
                        "id": "exported",
                        "msg": f"Exported {tag} {(name.group(1) if name else '?')} without permission",
                    }
                )

    dangerous = [
        "READ_SMS",
        "SEND_SMS",
        "READ_CONTACTS",
        "WRITE_CONTACTS",
        "ACCESS_FINE_LOCATION",
        "CAMERA",
        "RECORD_AUDIO",
        "READ_CALL_LOG",
        "WRITE_SETTINGS",
        "SYSTEM_ALERT_WINDOW",
        "QUERY_ALL_PACKAGES",
        "MANAGE_EXTERNAL_STORAGE",
    ]
    for p in report.get("permissions") or []:
        if any(d in p for d in dangerous):
            findings.append({"sev": "medium", "id": "permission", "msg": f"Sensitive permission {p} — justify and runtime-request"})

    for src in list(root.rglob("*.kt"))[:80] + list(root.rglob("*.xml"))[:40]:
        if "build/" in str(src):
            continue
        try:
            text = src.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        if "addJavascriptInterface" in text and "setJavaScriptEnabled(true)" in text:
            findings.append({"sev": "high", "id": "webview", "msg": f"WebView JS bridge in {src.relative_to(root)}"})
        if SECRET.search(text):
            findings.append({"sev": "high", "id": "secret", "msg": f"Possible hardcoded secret in {src.relative_to(root)}"})
        if "TrustAll" in text or "X509TrustManager" in text and "checkServerTrusted" in text:
            findings.append({"sev": "high", "id": "trust", "msg": f"Custom TrustManager in {src.relative_to(root)}"})

    sev_order = {"high": 0, "medium": 1, "low": 2}
    findings.sort(key=lambda f: sev_order.get(f["sev"], 9))
    return {
        "root": str(root),
        "application_id": report.get("application_id"),
        "finding_count": len(findings),
        "high": sum(1 for f in findings if f["sev"] == "high"),
        "findings": findings,
    }
