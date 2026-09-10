"""Central configuration model (spec section 43).

Secrets come only from environment variables / secure storage, never source code,
and are redacted from any output.
"""
from __future__ import annotations

import json
import os
from dataclasses import dataclass, field, asdict
from pathlib import Path

SECRET_MARK = ("key", "token", "secret", "password", "credential")


def _s(names, default=""):
    for n in names:
        v = os.environ.get(n)
        if v:
            return v
    return default


def _b(names, default=False):
    if isinstance(names, str):
        names = [names]
    for n in names:
        v = os.environ.get(n)
        if v is not None:
            return v.strip().lower() in ("1", "true", "yes", "on")
    return default


def _i(names, default):
    if isinstance(names, str):
        names = [names]
    try:
        for n in names:
            if os.environ.get(n):
                return int(os.environ.get(n))
    except (TypeError, ValueError):
        pass
    return default


@dataclass
class AudioConfig:
    device_id: int = -1          # -1 = system default
    sample_rate: int = 16000
    channels: int = 1
    vad_enabled: bool = True
    vad_threshold: float = 0.5   # energy threshold
    chunk_ms: int = 100          # buffer/chunk size
    capture_system_audio: bool = False


@dataclass
class ScreenConfig:
    monitoring: bool = False
    active_window_only: bool = True
    selected_region_only: bool = False
    capture_interval_s: float = 2.0
    change_threshold: float = 0.02
    duplicate_suppression: bool = True
    cloud_vision: bool = False
    record_screenshots: bool = False
    max_stored_frames: int = 30
    ignored_applications: list = field(default_factory=list)
    allowed_applications: list = field(default_factory=list)


@dataclass
class SttConfig:
    provider: str = "faster_whisper"   # faster_whisper | none
    model: str = "small"               # tiny/base/small/medium/large-v3
    language: str = ""                 # auto-detect if empty
    device: str = "auto"               # auto|cpu|cuda
    compute_type: str = "int8"
    vad_filter: bool = True


@dataclass
class ReasoningConfig:
    provider: str = "lmstudio"         # lmstudio | openclaw | none
    endpoint: str = "http://127.0.0.1:1234/v1"
    model: str = ""
    api_key: str = ""                  # only for cloud; secret
    timeout_s: int = 120
    context_window: int = 8192
    fallbacks: list = field(default_factory=list)   # list of provider names
    streaming: bool = True
    low_latency_model: str = ""        # e.g. a small local model
    strong_model: str = ""             # e.g. deeper local/cloud model


@dataclass
class TtsConfig:
    provider: str = "none"             # kokoro | piper | none
    voice: str = ""
    volume: float = 1.0
    rate: float = 1.0
    streaming: bool = False


@dataclass
class PrivacyConfig:
    store_transcripts: bool = True
    store_summaries: bool = True
    record_screenshots: bool = False
    cloud_processing: bool = False     # master gate for cloud (vision/reasoning)
    retention_days: int = 30


@dataclass
class SecurityConfig:
    remote_access: bool = False
    mcp_token: str = ""
    auth_enabled: bool = False


@dataclass
class AppConfig:
    device_name: str = "OLCAP Realtime"
    state_dir: str = _s(["OLCAP_STATE_DIR"], "~/.olcap-realtime")
    default_mode: str = "off"          # off | interview | workspace
    # sub-configs
    audio: AudioConfig = field(default_factory=AudioConfig)
    screen: ScreenConfig = field(default_factory=ScreenConfig)
    stt: SttConfig = field(default_factory=SttConfig)
    reasoning: ReasoningConfig = field(default_factory=ReasoningConfig)
    tts: TtsConfig = field(default_factory=TtsConfig)
    privacy: PrivacyConfig = field(default_factory=PrivacyConfig)
    security: SecurityConfig = field(default_factory=SecurityConfig)
    # integrations (names only; we add alongside, never overwrite)
    openclaw_enabled: bool = _b("OLCAP_OPENCLAW_ENABLED", True)
    opencode_mcp_name: str = "olcap-realtime-assistant-mcp"
    lmstudio_endpoint: str = _s(["LM_STUDIO_ENDPOINT", "OLCAP_LMSTUDIO_ENDPOINT"],
                                "http://127.0.0.1:1234/v1")

    def __post_init__(self):
        self.state_dir = str(Path(self.state_dir).expanduser())
        # keep defaults in sync if env explicitly set reasoning endpoint
        if os.environ.get("OLCAP_LMSTUDIO_ENDPOINT") or os.environ.get("LM_STUDIO_ENDPOINT"):
            self.reasoning.endpoint = self.lmstudio_endpoint
        if self.lmstudio_endpoint:
            self.reasoning.endpoint = self.lmstudio_endpoint

    @property
    def db_path(self) -> str:
        return str(Path(self.state_dir) / "assistant.db")

    @property
    def log_dir(self) -> str:
        return str(Path(self.state_dir) / "logs")

    @property
    def screenshot_dir(self) -> str:
        return str(Path(self.state_dir) / "screenshots")

    def redacted(self) -> dict:
        d = asdict(self)
        for sec in ("stt", "reasoning", "tts", "security"):
            sub = d.get(sec, {})
            if isinstance(sub, dict):
                for k in list(sub):
                    if any(m in k.lower() for m in SECRET_MARK) and sub[k]:
                        sub[k] = "***redacted***"
        return d

    @classmethod
    def from_json(cls, path) -> "AppConfig":
        cfg = cls()
        p = Path(path)
        if p.exists():
            data = json.loads(p.read_text())
            for top, sub in data.items():
                if hasattr(cfg, top):
                    cur = getattr(cfg, top)
                    if isinstance(cur, (AudioConfig, ScreenConfig, SttConfig,
                                        ReasoningConfig, TtsConfig, PrivacyConfig,
                                        SecurityConfig)) and isinstance(sub, dict):
                        for k, v in sub.items():
                            if hasattr(cur, k):
                                setattr(cur, k, v)
                    else:
                        setattr(cfg, top, sub)
        return cfg
