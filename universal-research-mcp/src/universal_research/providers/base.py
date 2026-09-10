"""Provider adapter base interface."""
from __future__ import annotations

from typing import Optional

from ..errors import NoProviderAvailableError, ProviderError
from ..models import SearchResult


class ProviderCapabilities:
    WEB = "web"
    CODE = "code"
    PAPER = "paper"
    NEWS = "news"
    COMMUNITY = "community"


class Adapter:
    """Common adapter interface. Subclasses implement ``search``."""

    # capability keys the provider can serve (subset of ProviderCapabilities)
    capabilities = frozenset()
    name = "adapter"

    def __init__(self, settings):
        self.settings = settings

    def configured(self) -> bool:
        return True

    def supports(self, capability: str) -> bool:
        return capability in self.capabilities

    def search(self, query: str, *, limit: int = 10,
               opts: Optional[dict] = None) -> list[SearchResult]:
        raise NotImplementedError

    # convenience
    def _res(self, **kw) -> SearchResult:
        base = {"provider": self.name}
        base.update(kw)
        return SearchResult(**base)


def no_results(provider: str, reason: str = "") -> list:
    return []


def empty_result(reason: str = "") -> None:
    return None
