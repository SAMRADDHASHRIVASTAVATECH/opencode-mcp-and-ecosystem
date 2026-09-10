"""Security & emergency stop (spec sections 26, 27).

* Local mode: on-host trust, optional token.
* Remote mode: require a token (constant-time compare).
* Emergency stop: stops capture/STT/TTS/generation and marks inactive; persists.
No secrets in code.
"""
from __future__ import annotations

import hmac
import threading
import time

from .config import AppConfig
from .errors import AuthRequired, EmergencyStopActive


class SecurityManager:
    def __init__(self, config: AppConfig, store=None):
        self.cfg = config
        self.store = store
        self._emergency_stop = False
        self._lock = threading.Lock()
        if store is not None and store.get_kv("emergency_stop"):
            self._emergency_stop = True

    @property
    def emergency_stop(self):
        return self._emergency_stop

    def engage_emergency_stop(self) -> dict:
        with self._lock:
            self._emergency_stop = True
        if self.store is not None:
            self.store.put_kv("emergency_stop", "1")
        return {"emergency_stop": True}

    def release_emergency_stop(self) -> dict:
        with self._lock:
            self._emergency_stop = False
        if self.store is not None:
            self.store.put_kv("emergency_stop", "")
        return {"emergency_stop": False}

    def require_active(self):
        if self._emergency_stop:
            raise EmergencyStopActive("emergency stop is active; assistant inactive")

    def authorize(self, token: str = "") -> str:
        if not self.cfg.security.remote_access:
            return "local"
        expected = self.cfg.security.mcp_token
        if not expected:
            raise AuthRequired("remote access enabled but no MCP_TOKEN configured")
        if not token:
            raise AuthRequired("remote access requires an MCP token")
        if not hmac.compare_digest(token, expected):
            raise AuthRequired("invalid MCP token")
        return "remote"
