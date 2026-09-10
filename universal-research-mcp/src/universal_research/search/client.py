"""SearchClient: unified, provider-abstracted search entry point (#7, #8).

Wraps the provider registry and router so callers only specify a query and
optional kind; the router picks which providers to query (with fallback) and
results are normalized, deduplicated and ranked. Never fabricates results: if a
provider fails it moves to the next, and if all fail it raises.
"""
from __future__ import annotations

from typing import Optional

from ..errors import NoProviderAvailableError, ProviderError
from ..models import SearchResult
from .operators import effective_query
from .ranking import deduplicate, rank_results


class SearchClient:
    def __init__(self, providers, settings=None, router=None):
        """providers: ProviderRegistry; router: ToolRouter (optional)."""
        self.providers = providers
        self.settings = settings
        self.router = router

    def search(self, query: str, *, kind: str = "web", limit: int = 10,
               providers: Optional[list] = None, require: Optional[list] = None,
               use_mock: bool = False, **ctx) -> dict:
        """Run a search. kind: web|code|paper|news|community|doc|gov.

        Returns {"results":[...], "provider_used":[...], "attempted":[...],
                 "degraded": bool, "notes":[...]}.
        """
        q = effective_query(query)
        results: list[SearchResult] = []
        used = []
        attempted = []
        notes = []

        if providers is None:
            providers = self._select_providers(kind, require=require,
                                               use_mock=use_mock)
        for prov_name in providers:
            prov = self._get_provider(prov_name)
            if prov is None or not prov.configured:
                notes.append(f"provider {prov_name}: not configured")
                continue
            attempted.append(prov_name)
            try:
                adapter = prov.adapter
                opts = {"kind": kind} if kind != "web" else {}
                r = adapter.search(q, limit=limit, opts=opts)
                for res in r:
                    res.kind = res.kind if res.kind != "web" else _map_kind(kind, res)
                results.extend(r)
                used.append(prov_name)
                if results and len(used) >= (1 if not require else len(require)):
                    # stop after enough providers succeeded
                    if not require and len(used) >= 2:
                        break
            except ProviderError as e:
                notes.append(f"provider {prov_name}: {e}")
                continue
            except Exception as e:  # noqa: BLE001
                notes.append(f"provider {prov_name}: unexpected {e!r}")
                continue

        if not results and not used:
            raise NoProviderAvailableError(
                "all providers failed or none configured: " + "; ".join(notes))

        deduped = deduplicate(results)
        ranked = rank_results(deduped, q)[:limit]
        return {"results": ranked, "provider_used": used, "attempted": attempted,
                "notes": notes, "degraded": not used or len(results) == 0}

    def search_multi(self, query: str, *, limit: int = 6) -> dict:
        """Run across the highest-priority general web providers (#8)."""
        return self.search(query, kind="web", limit=limit)

    def search_operator(self, expression: str, *, limit: int = 10,
                        kind: str = "web") -> dict:
        """Operator-aware search (#9). Passes the expression through; provider
        supports operators where it can. Returns parsed structure too."""
        from .operators import parse_query
        parsed = parse_query(expression)
        out = self.search(expression, kind=kind, limit=limit)
        out["parsed"] = parsed.to_dict()
        return out

    # -- selection ----------------------------------------------------------
    def _select_providers(self, kind, require=None, use_mock=False) -> list:
        if self.router is not None:
            return self.router.choose_providers(kind, require=require,
                                                use_mock=use_mock)
        # deterministic fallback order if no router
        cap = _kind_to_cap(kind)
        ordered = []
        for p in self.providers.configured():
            if use_mock and p.name == "mock":
                return ["mock"]
            if cap in p.capabilities:
                ordered.append(p.name)
        return ordered

    def _get_provider(self, name):
        try:
            return self.providers.get(name)
        except Exception:
            return None


def _kind_to_cap(kind: str) -> str:
    return {"web": "web", "code": "code", "paper": "paper", "news": "news",
            "community": "community", "doc": "web", "gov": "web"}.get(kind, "web")


def _map_kind(kind: str, res) -> str:
    if kind == "doc":
        return "doc"
    return kind if kind in ("code", "paper", "news", "community") else res.kind
