"""Exception hierarchy for the research system.

We distinguish *operational* failures (rate limit, provider down, no key,
blocked) from *security* rejections and *user* cancellations so the
orchestrator and tool layer can degrade predictably and never fabricate.
"""
from __future__ import annotations


class ResearchError(Exception):
    """Base class."""


class ProviderError(ResearchError):
    """A provider/adapter failed or returned unusable data."""


class NoProviderAvailableError(ProviderError):
    """All candidate providers failed or none matched the requirement."""


class RateLimitedError(ProviderError):
    """Transient rate limiting from a provider."""


class ConfigError(ResearchError):
    """Required configuration (e.g. API key, base URL) missing/invalid."""


class SecurityRejectionError(ResearchError):
    """A request was rejected by a security guard (SSRF, scheme, etc.)."""


class UnsafeContentError(ResearchError):
    """Content tripped a safety/size/type guard before processing."""


class CancelledError(ResearchError):
    """A running research task was cancelled by the caller."""


class BudgetExceededError(ResearchError):
    """A research budget (searches/pages/time) was exhausted."""


class NotFoundError(ResearchError):
    """A requested registry item / resource id does not exist."""
