"""Central configuration model (spec section 27).

Secrets (API keys / tokens / passwords) are never stored in code. They come from
environment variables or from OS secure storage (Android Keystore / credential
store) referenced by key name. `redacted()` strips secrets for any output.
"""
from __future__ import annotations

import json
import os
from dataclasses import dataclass, field, asdict
from pathlib import Path

SECRET_SUFFIXES = ("token", "key", "secret", "password", "credential")


def _s(name, default=""):
    v = os.environ.get(name)
    return v if v else default


def _b(name, default=False):
    v = os.environ.get(name)
    return default if v is None else v.strip().lower() in ("1", "true", "yes", "on")


def _i(name, default):
    try:
        return int(os.environ.get(name, default))
    except (TypeError, ValueError):
        return default


@dataclass
class AppConfig:
    device_name: str = _s("OLCAP_DEVICE_NAME", "OLCAP Phone")
    mcp_enabled: bool = _b("OLCAP_MCP_ENABLED", True)
    remote_access: bool = _b("OLCAP_REMOTE_ACCESS", False)
    ai_calls_enabled: bool = _b("OLCAP_AI_CALLS_ENABLED", False)
    auto_answer_enabled: bool = _b("OLCAP_AUTO_ANSWER_ENABLED", False)
    default_voice_provider: str = _s("OLCAP_VOICE_PROVIDER", "simulated")  # openclaw|provider|voip|local|simulated|none
    default_sim: str = _s("OLCAP_DEFAULT_SIM", "system")
    max_call_duration_seconds: int = _i("OLCAP_MAX_CALL_DURATION", 900)
    record_calls: bool = _b("OLCAP_RECORD_CALLS", False)
    store_transcripts: bool = _b("OLCAP_STORE_TRANSCRIPTS", True)
    state_dir: str = _s("OLCAP_STATE_DIR", "~/.olcap")
    # allowlist/denylist (E.164, comma separated)
    destination_allowlist: str = _s("OLCAP_DEST_ALLOW", "")
    destination_denylist: str = _s("OLCAP_DEST_DENY", "")
    caller_allowlist: str = _s("OLCAP_CALLER_ALLOW", "")
    caller_denylist: str = _s("OLCAP_CALLER_DENY", "")
    # MCP auth
    mcp_token: str = _s("OLCAP_MCP_TOKEN", "")       # required in remote mode
    audit_enabled: bool = _b("OLCAP_AUDIT_ENABLED", True)
    # auto = pick best real backend at runtime (adb -> openclaw_voice -> simulated)
    # explicit: adb|simulated|android_bridge|provider_voice|openclaw_voice|voip
    backend: str = _s("OLCAP_BACKEND", "auto")
    android_bridge_url: str = _s("OLCAP_ANDROID_BRIDGE_URL", "")
    # --- host-side ADB backend (no phone app required) ---
    adb_serial: str = _s("OLCAP_ADB_SERIAL", "")              # selector pin; e.g. 947450d2
    adb_model: str = _s("OLCAP_ADB_MODEL", "")
    adb_manufacturer: str = _s("OLCAP_ADB_MANUFACTURER", "")
    adb_health_poll_s: int = _i("OLCAP_ADB_HEALTH_POLL_S", 2)
    adb_reconnect_backoff_max_s: int = _i("OLCAP_ADB_RECONNECT_BACKOFF_MAX_S", 60)
    # fallback chain used when 'auto' or the pinned backend is unreachable
    provider_fallback: str = _s("OLCAP_PROVIDER_FALLBACK", "openclaw_voice,simulated")
    country_code: str = _s("OLCAP_COUNTRY_CODE", "+91")

    # secrets referenced by env, redacted from output
    voice_api_url: str = _s("OLCAP_VOICE_API_URL", "")
    voice_api_key: str = _s("OLCAP_VOICE_API_KEY", "")
    openclaw_voice: str = _s("OLCAP_OPENCLAW_VOICE", "")

    def __post_init__(self):
        self.state_dir = str(Path(self.state_dir).expanduser())

    @property
    def db_path(self) -> str:
        return str(Path(self.state_dir) / "olcap.db")

    @property
    def allow_dest(self) -> list:
        return [x.strip() for x in self.destination_allowlist.split(",") if x.strip()]

    @property
    def deny_dest(self) -> list:
        return [x.strip() for x in self.destination_denylist.split(",") if x.strip()]

    @property
    def allow_callers(self) -> list:
        return [x.strip() for x in self.caller_allowlist.split(",") if x.strip()]

    @property
    def deny_callers(self) -> list:
        return [x.strip() for x in self.caller_denylist.split(",") if x.strip()]

    def redacted(self) -> dict:
        d = asdict(self)
        for k in list(d):
            if any(s in k.lower() for s in SECRET_SUFFIXES) and d[k]:
                d[k] = "***redacted***"
        return d

    @classmethod
    def from_json(cls, path) -> "AppConfig":
        cfg = cls()
        p = Path(path)
        if p.exists():
            data = json.loads(p.read_text())
            for k, v in data.items():
                if hasattr(cfg, k) and not isinstance(getattr(cfg, k), property):
                    setattr(cfg, k, v)
        return cfg
