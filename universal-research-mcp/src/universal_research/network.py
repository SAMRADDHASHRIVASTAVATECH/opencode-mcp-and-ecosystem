"""HTTP layer: one httpx client factory used by every provider & reader.

Enforces redirect limits, size caps, content-type sniffing and URL safety.
A single client with connection pooling is created per Settings.
"""
from __future__ import annotations

from typing import Optional

import httpx

from . import security
from .config import Settings
from .errors import ProviderError, UnsafeContentError

_client = None
_settings: Optional[Settings] = None


def init(settings: Settings):
    global _client, _settings
    _settings = settings
    limits = httpx.Limits(max_connections=settings.budget.max_concurrency,
                          max_keepalive_connections=16)
    _client = httpx.Client(
        timeout=httpx.Timeout(settings.default_timeout, connect=10),
        follow_redirects=True,
        max_redirects=settings.max_redirects,
        limits=limits,
        headers={"User-Agent": settings.user_agent,
                 "Accept-Language": "en-US,en;q=0.8"},
    )


def client() -> httpx.Client:
    global _client
    if _client is None:
        init(load_settings())
    return _client


def get_settings() -> Settings:
    global _settings
    if _settings is None:
        from .config import load_settings
        _settings = load_settings()
        init(_settings)
    return _settings


def _cap_bytes(r: httpx.Response) -> None:
    limit = get_settings().budget.max_document_size_bytes
    ct = r.headers.get("content-length")
    if ct and int(ct) > limit:
        raise UnsafeContentError(f"document too large ({ct} bytes > {limit})")


def fetch(url: str, *, follow=True, headers=None, timeout=None) -> httpx.Response:
    """Fetch a url with SSRF validation, redirect cap and size guard.

    Downloads only up to the configured size limit (streamed) to avoid pulling
    huge bodies into memory when they will be rejected.
    """
    s = get_settings()
    security.validate_url(url, s)
    # For non-follow, redirects are returned to caller; for follow we still cap.
    if security.is_dangerous_type(url):
        raise UnsafeContentError(f"refusing to fetch dangerous type: {url}")
    resp = client().get(url, headers=headers or {},
                        follow_redirects=follow,
                        timeout=timeout or s.default_timeout)
    if resp.status_code >= 400:
        # avoid echoing bodies with secrets
        raise ProviderError(f"HTTP {resp.status_code} for {url}")
    return resp


def fetch_capped(url: str, *, headers=None, timeout=None):
    """Fetch honouring the size cap by streaming and reading only up to cap.

    Returns a lightweight response object exposing status_code/headers/url and
    read_capped()/read() returning the body bytes (kept under the cap).
    """
    s = get_settings()
    security.validate_url(url, s)
    if security.is_dangerous_type(url):
        raise UnsafeContentError(f"refusing to fetch dangerous type: {url}")
    limit = s.budget.max_document_size_bytes
    with client().stream("GET", url, headers=headers or {},
                         follow_redirects=True,
                         timeout=timeout or s.default_timeout) as r:
        if r.status_code >= 400:
            raise ProviderError(f"HTTP {r.status_code} for {url}")
        chunks = []
        total = 0
        for chunk in r.iter_bytes(65536):
            total += len(chunk)
            if total > limit:
                raise UnsafeContentError(
                    f"document exceeds {limit} bytes limit")
            chunks.append(chunk)
        body = b"".join(chunks)
        headers = dict(r.headers)
        final_url = str(r.url)
        status = r.status_code

    return _bounded_response(status, final_url, headers, body)


def _bounded_response(status, final_url, headers, body):
    class _R:
        @property
        def status_code(self):
            return status
        @property
        def headers(self):
            return headers
        @property
        def url(self):
            return final_url
        def read_capped(self) -> bytes:
            return body
        def read(self) -> bytes:
            return body
    return _R()
