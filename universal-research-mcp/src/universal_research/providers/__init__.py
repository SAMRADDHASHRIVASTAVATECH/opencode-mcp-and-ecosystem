"""Provider adapters + the provider registry.

Each adapter exposes a common ``search(query, **opts) -> list[SearchResult]``
interface and declares its capabilities (web/code/paper/news/community) and
whether it needs configuration. The registry built here drives discovery and
the tool router.
"""
from .base import Adapter, ProviderCapabilities
from .mock import MockProvider
from .web_search import (BingAdapter, DuckDuckGoAdapter, SearxAdapter,
                         BraveAdapter)
from .special import (GithubAdapter, ArxivAdapter, CrossrefAdapter,
                      GoogleNewsAdapter, HackerNewsAdapter)

from ..registry.base import Provider, ProviderRegistry
from .. import config


def build_provider_registry(settings: config.Settings = None) -> ProviderRegistry:
    settings = settings or config.load_settings()
    reg = ProviderRegistry()
    reg.register_many([
        Provider("bing", description="General web search (Bing HTML, best-effort)",
                 capabilities=["web"], best_effort=True,
                 limitations="best-effort HTML endpoint; may be blocked in some regions",
                 kind_filter="web", adapter=BingAdapter(settings)),
        Provider("duckduckgo", description="General web search (DuckDuckGo, best-effort)",
                 capabilities=["web"], best_effort=True,
                 limitations="subject to bot-check page; degrade when blocked",
                 kind_filter="web", adapter=DuckDuckGoAdapter(settings)),
        Provider("searxng", description="Self-hosted SearXNG (legitimate, requires operator endpoint)",
                 capabilities=["web"], needs_key=True, has_key=bool(settings.searxng_base_url),
                 limitations="operator must run a SearXNG instance",
                 kind_filter="web", adapter=SearxAdapter(settings)),
        Provider("brave", description="Brave Search API (requires API key)",
                 capabilities=["web"], needs_key=True, has_key=bool(settings.brave_api_key),
                 limitations="requires UR_BRAVE_API_KEY",
                 kind_filter="web", adapter=BraveAdapter(settings)),
        Provider("github", description="GitHub REST API (repos/code/issues/releases)",
                 capabilities=["code", "community"], kind_filter="code",
                 adapter=GithubAdapter(settings)),
        Provider("arxiv", description="arXiv API (preprints)",
                 capabilities=["paper"], kind_filter="paper",
                 adapter=ArxivAdapter(settings)),
        Provider("crossref", description="Crossref API (journal metadata)",
                 capabilities=["paper"], kind_filter="paper",
                 adapter=CrossrefAdapter(settings)),
        Provider("googlenews", description="Google News RSS (news headlines by query)",
                 capabilities=["news"], kind_filter="news",
                 adapter=GoogleNewsAdapter(settings)),
        Provider("hackernews", description="Hacker News Algolia API (community/tech)",
                 capabilities=["community"], kind_filter="community",
                 adapter=HackerNewsAdapter(settings)),
        Provider("mock", description="Deterministic offline provider (tests/offline)",
                 capabilities=["web", "code", "paper", "news", "community"],
                 kind_filter="web", adapter=MockProvider()),
    ])
    return reg
