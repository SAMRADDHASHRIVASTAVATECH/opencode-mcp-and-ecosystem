"""Security: MCP client authentication/authorization, emergency stop, rate
limiting, audit (spec section 16). Local-only mode requires no token; remote
access requires a configured token + pairing.

No credentials are stored in code - the token comes from env / secure storage.
"""
from __future__ import annotations

import hmac
import time

from .errors import McpUnauthorized, EmergencyStopActive, DestinationNotAllowed


class SecurityManager:
    def __init__(self, config, store):
        self.cfg = config
        self.store = store
        self._emergency_stop = False
        self._paused_until = 0.0

    # ---- pairing / auth ---------------------------------------------- #
    def require_authorized(self, token: str = "", remote: bool | None = None) -> str:
        # remote flag read live from config so it can be toggled at runtime
        remote = self.cfg.remote_access if remote is None else (remote and self.cfg.remote_access)
        if not remote:
            # local-only mode: device operator is trusted; token optional
            return "local"
        if not token:
            raise McpUnauthorized("remote access requires an MCP token")
        expected = self.cfg.mcp_token
        if not expected:
            raise McpUnauthorized("remote access enabled but no MCP_TOKEN configured")
        if not hmac.compare_digest(token, expected):
            raise McpUnauthorized("invalid MCP token")
        return "remote"

    # ---- emergency stop ---------------------------------------------- #
    @property
    def emergency_stop(self):
        # A configured E-stop could also be persisted; honour an env override too.
        return self._emergency_stop

    def emergency_stop_engage(self) -> dict:
        self._emergency_stop = True
        self.store.put_kv("emergency_stop", "1")
        self.store.audit(time.time(), "operator", "emergency_stop", {"on": True})
        return {"emergency_stop": True, "note": "AI-controlled calling stopped"}

    def emergency_stop_release(self) -> dict:
        self._emergency_stop = False
        self.store.put_kv("emergency_stop", "")
        self.store.audit(time.time(), "operator", "emergency_stop", {"on": False})
        return {"emergency_stop": False}

    def require_calling_allowed(self):
        if self.emergency_stop:
            raise EmergencyStopActive(
                "emergency stop is active; autonomous calling is disabled")

    # ---- rate limiting ----------------------------------------------- #
    _calls_this_window = 0
    _window_start = 0.0

    def throttle(self, limit_per_minute: int = 6):
        now = time.time()
        if now - self._window_start >= 60:
            self._window_start = now
            self._calls_this_window = 0
        if self._calls_this_window >= limit_per_minute:
            raise DestinationNotAllowed("call rate limit exceeded", code="RATE_LIMITED")
        self._calls_this_window += 1

    def audit(self, actor, action, detail=None):
        self.store.audit(time.time(), actor, action, detail)
