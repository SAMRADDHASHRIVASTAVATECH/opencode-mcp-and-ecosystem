"""Environment-driven configuration for the unified operator.

All secrets come from environment variables or files referenced by env vars.
No secret is ever hard-coded or echoed back through MCP responses.
"""
from __future__ import annotations

import os
from dataclasses import dataclass, asdict, field
from pathlib import Path


def _s(names, default=""):
    for n in names:
        v = os.environ.get(n)
        if v:
            return v
    return default


def _b(name, default=False):
    v = os.environ.get(name)
    return default if v is None else v.strip().lower() in {"1", "true", "yes", "on"}


def _i(name, default):
    try:
        return int(os.environ.get(name, default))
    except (TypeError, ValueError):
        return default


def state_dir() -> Path:
    return Path(_s(["UNIFIED_STATE_DIR"], default="~/.unified-operator")).expanduser()


@dataclass
class Settings:
    # ---- runtime --------------------------------------------------- #
    offline: bool = _b("UNIFIED_OFFLINE", False)
    state_dir: str = field(default_factory=lambda: str(state_dir()))
    log_dir: str = _s(["UNIFIED_LOG_DIR"], default="")
    timezone: str = _s(["UNIFIED_TZ"], default="Asia/Kolkata")

    # ---- Google Workspace ------------------------------------------ #
    # Either a service-account JSON path or OAuth client secrets + token path.
    google_creds_path: str = _s(["GOOGLE_APPLICATION_CREDENTIALS", "GOOGLE_CREDS_FILE"])
    google_client_secrets: str = _s(["GOOGLE_CLIENT_SECRETS"])
    google_token_path: str = _s(["GOOGLE_TOKEN_PATH"], default="~/.unified-operator/google_token.json")
    google_account: str = _s(["GOOGLE_ACCOUNT"], default="default")
    google_scopes: str = _s(["GOOGLE_SCOPES"], default="")

    # ---- Discord ---------------------------------------------------- #
    discord_token: str = _s(["DISCORD_TOKEN"])
    discord_account: str = _s(["DISCORD_ACCOUNT"], default="primary")
    discord_prefix: str = _s(["DISCORD_PREFIX"], default="!")

    # ---- Voice provider --------------------------------------------- #
    voice_provider: str = _s(["VOICE_PROVIDER"], default="openclaw")  # openclaw|generic
    # Generic provider endpoint creds (e.g. an HTTPS gateway the operator dials).
    voice_api_url: str = _s(["VOICE_API_URL"])
    voice_api_key: str = _s(["VOICE_API_KEY"])
    voice_agent_id: str = _s(["VOICE_AGENT_ID"])
    voice_default_phone: str = _s(["VOICE_DEFAULT_PHONE"])

    # ---- OpenClaw ----------------------------------------------------- #
    openclaw_bin: str = _s(["OPENCLAW_BIN"])
    openclaw_gateway_url: str = _s(["OPENCLAW_GATEWAY_URL"], default="ws://127.0.0.1:18789")
    openclaw_gateway_port: int = _i("OPENCLAW_GATEWAY_PORT", 18789)
    openclaw_gateway_token: str = _s(["OPENCLAW_GATEWAY_TOKEN", "OPENCLAW_GATEWAY_PASSWORD"])

    # ---- Permissions (default policy per action class) --------------- #
    perm_default: str = _s(["UNIFIED_PERM_DEFAULT"], default="automatic")  # automatic|confirm|blocked
    perm_confirm_patterns: str = _s(["UNIFIED_PERM_CONFIRM"], default="")   # comma list e.g. email:send,call:external
    perm_blocked_patterns: str = _s(["UNIFIED_PERM_BLOCK"], default="")

    # ---- Workflow / call engines -------------------------------------- #
    call_max_attempts: int = _i("UNIFIED_CALL_MAX_ATTEMPTS", 3)
    call_retry_delay_s: int = _i("UNIFIED_CALL_RETRY_DELAY_S", 300)
    allow_concurrent_calls: bool = _b("UNIFIED_ALLOW_CONCURRENT_CALLS", False)

    def __post_init__(self):
        if not self.log_dir:
            self.log_dir = str(Path(self.state_dir) / "logs")

    @property
    def db_path(self) -> str:
        return str(Path(self.state_dir) / "operator.db")

    @property
    def creds_dir(self) -> str:
        return str(Path(self.state_dir))

    def to_dict(self) -> dict:
        # Redact secrets for any status/observability output.
        d = asdict(self)
        for k in list(d):
            if any(s in k for s in ("token", "secret", "password", "key", "scopes")):
                if isinstance(d[k], str) and d[k]:
                    d[k] = "***redacted***"
        return d
