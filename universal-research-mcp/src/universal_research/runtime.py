"""Runtime: a shared bundle wiring settings, providers, search, web, docs,
verification, graph and orchestration. Created lazily and reused."""
from __future__ import annotations

from . import config as _config
from .cache import Cache
from .config import Settings
from .documents.engine import DocumentEngine
from .llm import ReasoningClient
from .providers import build_provider_registry
from .registry.base import ProviderRegistry
from .router import ToolRouter
from .search.client import SearchClient
from .search.query import QueryEngine
from .verify.engine import EvidenceEngine, VerificationEngine
from .verify.factcheck import FactChecker
from .web.crawler import Crawler
from .web.reader import WebReader
from .research.compare import ComparisonEngine
from .research.errorskill import ErrorInvestigator
from .research.orchestrator import ResearchOrchestrator
from .research.state import ResearchManager
from .research.planner import ResearchPlanner
from .research.graph import KnowledgeGraph


class Runtime:
    def __init__(self, settings: Settings = None, *, offline_mode: bool = False,
                 use_mock: bool = False):
        self.settings = settings or _config.load_settings()
        self.offline_mode = offline_mode or use_mock
        self.cache = Cache(enabled=not self.offline_mode)
        # providers
        self.providers: ProviderRegistry = build_provider_registry(self.settings)
        # documents
        self.documents = DocumentEngine(persist_dir=self.settings.cache_dir or None)
        # web
        self.reader = WebReader(self.settings, cache=self.cache,
                                doc_engine=self.documents,
                                offline=self.offline_mode)
        self.crawler = Crawler(self.reader, self.settings)
        # routing / search
        self.router = ToolRouter(self.providers, self.settings)
        self.router.mock_only = self.offline_mode
        self.search = SearchClient(self.providers, self.settings,
                                   router=self.router)
        self.query = QueryEngine(self.settings)
        # verification
        self.evidence = EvidenceEngine(self.search, self.reader)
        self.verification = VerificationEngine(self.evidence, self.search)
        self.factcheck = FactChecker(self.verification)
        # comparison / errors
        self.compare = ComparisonEngine(self.search,
                                        sources_analysis=_analyze_source) 
        self.errors = ErrorInvestigator(self.search, self.query)
        # LLM (optional)
        self.llm = ReasoningClient(self.settings)
        # orchestration
        self.manager = ResearchManager()
        self.planner = ResearchPlanner(self.settings, self.query, self.llm)
        self.orchestrator = ResearchOrchestrator(self, self.manager, self.planner)
        self.seed_pool = {}   # query -> [seed urls for crawling]


_runtime = None


def get_runtime(offline_mode: bool = False, use_mock: bool = False) -> Runtime:
    global _runtime
    import os as _os
    env_off = _os.environ.get("UR_OFFLINE", "").lower() in {"1", "true", "yes"}
    offline_mode = offline_mode or env_off
    use_mock = use_mock or offline_mode
    if _runtime is None or (offline_mode and not _runtime.offline_mode):
        _runtime = Runtime(offline_mode=offline_mode, use_mock=use_mock)
    return _runtime


def reset_runtime():
    global _runtime
    _runtime = None


def _analyze_source(url, title="", snippet="", **kw):
    from . import sources as S
    return S.analyze_source(url, title=title, snippet=snippet)


def import_source_analysis():
    """Late import helper to avoid cycles."""
    from . import sources as S
    return S
