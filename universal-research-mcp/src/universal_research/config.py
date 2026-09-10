"""Environment-driven configuration.

Reads ``universal_research`` package defaults, then ``.env`` in the working
directory / package root, then real environment variables. All knobs also have
``UR_`` prefixed environment variables. No secrets are hard-coded.
"""
from __future__ import annotations

import os
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Optional


def _b(name: str, default: bool) -> bool:
    v = os.environ.get("UR_" + name)
    if v is None:
        return default
    return v.strip().lower() in {"1", "true", "yes", "on"}


def _i(name: str, default: int) -> int:
    try:
        return int(os.environ.get("UR_" + name, default))
    except (TypeError, ValueError):
        return default


def _s(name: str, default: str = "") -> str:
    return os.environ.get("UR_" + name, default)


def _f(name: str, default: float) -> float:
    try:
        return float(os.environ.get("UR_" + name, default))
    except (TypeError, ValueError):
        return default


@dataclass
class ResearchBudget:
    """Hard limits for a research task (#44)."""
    max_searches: int = _i("MAX_SEARCHES", 40)
    max_pages: int = _i("MAX_PAGES", 25)
    max_crawl_depth: int = _i("MAX_CRAWL_DEPTH", 2)
    max_links: int = _i("MAX_LINKS", 200)
    max_iterations: int = _i("MAX_ITERATIONS", 12)
    max_runtime_seconds: int = _i("MAX_RUNTIME", 300)
    max_document_size_bytes: int = _i("MAX_DOCUMENT_SIZE", 4_000_000)
    max_concurrency: int = _i("MAX_CONCURRENCY", 4)
    max_context_chars: int = _i("MAX_CONTEXT", 6000)

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class Settings:
    """Top-level settings assembled from env + defaults."""
    # provider keys / endpoints (optional)
    brave_api_key: str = _s("BRAVE_API_KEY")
    searxng_base_url: str = _s("SEARXNG_BASE_URL")
    bing_enabled: bool = _b("BING_ENABLED", True)
    duckduckgo_enabled: bool = _b("DUCKDUCKGO_ENABLED", True)
    user_agent: str = _s(
        "USER_AGENT",
        "UniversalResearchMCP/1.0 (+contact: operator@example.in) "
        "respect-robots")
    default_timeout: int = _i("TIMEOUT", 20)
    respect_robots: bool = _b("RESPECT_ROBOTS", True)
    # network guards
    allow_private_ips: bool = _b("ALLOW_PRIVATE_IPS", False)
    max_redirects: int = _i("MAX_REDIRECTS", 8)
    allowed_schemes: tuple = ("http", "https")
    # local reasoning model (OpenAI compatible) - optional (#66)
    research_model_base_url: str = _s("RESEARCH_MODEL_BASE_URL")
    research_model_name: str = _s("RESEARCH_MODEL_NAME", "")
    research_model_api_key: str = _s("RESEARCH_MODEL_API_KEY", "")
    # synthesis / planner model usage toggle
    use_llm: bool = _b("USE_LLM", False)
    # cache
    cache_dir: str = _s("CACHE_DIR", "")

    budget: ResearchBudget = field(default_factory=ResearchBudget)

    def to_dict(self) -> dict:
        d = asdict(self)
        # never dump secrets
        for k in ("brave_api_key", "searxng_base_url",
                  "research_model_api_key"):
            d[k] = bool(d[k])  # indicate presence only
        return d


def _package_env_path() -> Optional[Path]:
    """Locate a .env shipped in the package, if present."""
    here = Path(__file__).resolve().parent
    for cand in (Path.cwd() / ".env", here.parent.parent / ".env"):
        if cand.exists():
            return cand
    return None


def _load_dotenv(path: Path):
    if not path:
        return
    try:
        for line in path.read_text().splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            k, v = k.strip(), v.strip().strip('"').strip("'")
            if k and k not in os.environ:  # real env wins
                os.environ.setdefault(k, v)
    except Exception:
        pass


def load_settings() -> Settings:
    envp = _package_env_path()
    if envp:
        _load_dotenv(envp)
    return Settings()


def save_env_example() -> str:
    """Emit an annotated .env.example template (used by installer)."""
    lines = [
        "# Universal Web Research MCP - environment",
        "# Optional legitimate provider credentials. All are optional.",
        "#",
        "# Brave Search API (https://brave.com/search/api/)",
        "UR_BRAVE_API_KEY=",
        "# Self-hosted SearXNG (JSON API). Example:",
        "UR_SEARXNG_BASE_URL=",
        "# Best-effort HTML providers",
        "UR_BING_ENABLED=true",
        "UR_DUCKDUCKGO_ENABLED=true",
        "# Optional OpenAI-compatible LOCAL reasoning endpoint for the",
        "# planner/synthesis LLM passes. Not required; deterministic fallbacks",
        "# are used when absent.",
        "UR_RESEARCH_MODEL_BASE_URL=",
        "UR_RESEARCH_MODEL_NAME=",
        "UR_RESEARCH_MODEL_API_KEY=",
        "UR_USE_LLM=false",
        "# Budgets",
        "UR_MAX_SEARCHES=40",
        "UR_MAX_PAGES=25",
        "UR_MAX_CRAWL_DEPTH=2",
        "UR_MAX_RUNTIME=300",
        "# Network safety",
        "UR_ALLOW_PRIVATE_IPS=false",
        "UR_MAX_DOCUMENT_SIZE=4000000",
        "# HTTP",
        "UR_USER_AGENT=UniversalResearchMCP/1.0 (respect-robots)",
        "UR_TIMEOUT=20",
    ]
    return "\n".join(lines) + "\n"
