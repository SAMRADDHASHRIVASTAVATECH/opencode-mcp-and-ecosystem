"""Security guards (requirement #51-#53).

Everything fetched from the network is treated as UNTRUSTED DATA. These helpers
enforce:
  * SSRF prevention: resolve hostnames and reject non-public IPs unless the
    operator explicitly opts in to private networks.
  * Scheme allow-list.
  * Oversized-content rejection before it is parsed.
  * Prompt-injection defence markers: helper to detect instruction-like content
    so callers can quarantine it (never execute it).
  * Credential hygiene helpers.
"""
from __future__ import annotations

import ipaddress
import re
import socket
from urllib.parse import urlparse

from .config import Settings
from .errors import SecurityRejectionError, UnsafeContentError


def validate_url(url: str, settings: Settings) -> str:
    """Check a URL against scheme + SSRF guards. Returns the normalized URL.

    Raises SecurityRejectionError on violation.
    """
    if not url or len(url) > 8192:
        raise SecurityRejectionError("URL too long or empty")
    parsed = urlparse(url)
    scheme = parsed.scheme.lower()
    if scheme not in settings.allowed_schemes:
        raise SecurityRejectionError(f"scheme not allowed: {scheme!r}")
    host = parsed.hostname
    if not host:
        raise SecurityRejectionError("URL has no host")
    # Reject obvious creds-in-url leakage patterns
    if parsed.username or parsed.password:
        raise SecurityRejectionError("credentials embedded in URL are rejected")
    if not settings.allow_private_ips:
        _reject_private(host, parsed.port)
    return url


def _reject_private(host: str, port):
    try:
        infos = socket.getaddrinfo(host, port or (443 if host else 80),
                                   proto=socket.IPPROTO_TCP)
    except socket.gaierror:
        # cannot resolve -> treat as private/unsafe by default
        raise SecurityRejectionError(f"could not resolve host {host!r}")
    seen = set()
    for info in infos:
        ip = info[4][0]
        if ip in seen:
            continue
        seen.add(ip)
        addr = ipaddress.ip_address(ip)
        if (addr.is_private or addr.is_loopback or addr.is_link_local
                or addr.is_reserved or addr.is_multicast or addr.is_unspecified):
            raise SecurityRejectionError(
                f"refusing SSRF to private/loopback address {ip!r} for host "
                f"{host!r}")


# ------------------------------- content safety -----------------------------
TEXT_EXT = {".txt", ".md", ".html", ".htm", ".json", ".csv", ".xml", ".rst",
            ".log", ".css", ".js", ".yaml", ".yml"}
DOC_EXT = {".pdf", ".docx", ".doc", ".xlsx", ".xls", ".pptx", ".ppt", ".epub",
           ".odt", ".ods", ".odp"}
IMG_EXT = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg", ".bmp", ".ico"}
ARCHIVE_EXT = {".zip", ".gz", ".tar", ".rar", ".7z"}
EXE_EXT = {".exe", ".bin", ".sh", ".bat", ".msi", ".apk", ".dmg", ".deb", ".rpm"}

DANGEROUS_EXT = EXE_EXT | ARCHIVE_EXT | {".jar", ".wasm"}


def classify_url_type(url: str, content_type: str = "") -> str:
    """Best-effort source classification from url + content-type header."""
    parsed = urlparse(url)
    path = parsed.path.lower()
    if content_type:
        ct = content_type.split(";")[0].strip().lower()
        if "pdf" in ct:
            return "pdf"
        if ct in ("application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                  "application/msword", "application/vnd.oasis.opendocument.text"):
            return "doc"
        if "spreadsheet" in ct or "excel" in ct:
            return "spreadsheet"
        if "presentation" in ct or "powerpoint" in ct:
            return "presentation"
        if "json" in ct or "xml" in ct or "csv" in ct:
            return "data"
        if "html" in ct or "text/plain" in ct or "text/markdown" in ct:
            return "web"
        if "image" in ct:
            return "image"
    if path.endswith(".pdf"):
        return "pdf"
    if path.endswith((".docx", ".doc", ".odt")):
        return "doc"
    if path.endswith((".xlsx", ".xls", ".ods")):
        return "spreadsheet"
    if path.endswith((".pptx", ".ppt", ".odp")):
        return "presentation"
    if any(path.endswith(e) for e in IMG_EXT):
        return "image"
    return "web"


def is_dangerous_type(url: str, content_type: str = "") -> bool:
    parsed = urlparse(url)
    path = parsed.path.lower()
    if any(path.endswith(e) for e in DANGEROUS_EXT):
        return True
    return False


def enforce_size(size: int, limit: int):
    if size > limit:
        raise UnsafeContentError(
            f"content too large: {size} bytes > limit {limit}")


# ---------------------------- prompt injection ------------------------------
# Markers that content may try to hijack the assistant. Content bearing these
# is never treated as instructions; callers should quote it as data.
_INJECT_MARKERS = [
    "ignore previous instructions",
    "ignore all previous instructions",
    "ignore above",
    "system prompt",
    "disregard prior",
    "you are now",
    "override your instructions",
    "do not follow the instructions",
    "new instructions",
    "act as",
]


def looks_like_injection(text: str) -> bool:
    """Return True if text contains common injection / instruction markers.

    Used to *label/quarantine*, never to auto-execute.
    """
    low = text.lower()
    return any(m in low for m in _INJECT_MARKERS)


def sanitize_injection(text: str, max_len: int = 4000) -> str:
    """Quarantine untrusted text: trim and mark as data (never instructions)."""
    t = text[:max_len]
    flag = "⚠ [external content flagged as instruction-like; treated as DATA only] " \
        if looks_like_injection(t) else ""
    return flag + t


def redact_secrets(text: str) -> str:
    """Best-effort scrub of obvious secret patterns before logging/echo."""
    text = re.sub(r"(?i)(api[_-]?key|token|secret|password)\s*[=:]\s*\S+",
                  r"\1=<redacted>", text)
    text = re.sub(r"(?i)bearer\s+\S+", "bearer <redacted>", text)
    return text


def audit_url_is_safe_to_follow(url: str, settings: Settings) -> bool:
    """Wrapper for validate_url returning bool (used in crawler)."""
    try:
        validate_url(url, settings)
        return True
    except SecurityRejectionError:
        return False
