"""Generic registry plus the three concrete registries.

The registries are the system of record for *discoverability*: the calling
agent can list skills / tools / providers and query individual entries. They
are plain, deterministic, dependency-light structures (JSON-friendly) so
tooling and docs can be generated from them.
"""
from __future__ import annotations

import json
from typing import Any, Callable, Iterable, Optional

from ..errors import NotFoundError


class Registry:
    """A keyed, ordered collection with lookup + schema export."""

    def __init__(self, kind: str):
        self.kind = kind
        self._items: dict[str, Any] = {}

    def register(self, item: Any):
        key = getattr(item, "name", None)
        if not key:
            raise ValueError(f"{self.kind} item missing name")
        self._items[key] = item
        return item

    def register_many(self, items: Iterable[Any]):
        for it in items:
            self.register(it)
        return self

    def get(self, name: str):
        if name not in self._items:
            raise NotFoundError(f"{self.kind} not found: {name}")
        return self._items[name]

    def has(self, name: str) -> bool:
        return name in self._items

    def names(self) -> list[str]:
        return sorted(self._items)

    def all(self) -> list[Any]:
        return [self._items[k] for k in sorted(self._items)]

    def __len__(self):
        return len(self._items)


# ---------------------------------------------------------------------------
# PROVIDERS
# ---------------------------------------------------------------------------
class Provider:
    """Metadata + optional live adapter for one external service.

    A concrete adapter (a subclass instance) exposes ``search(query, **opts)``
    returning list[SearchResult]; ``configured`` reflects whether the adapter
    can actually be used (key present / endpoint reachable) so the router
    selects only usable providers. Provider *specs* (metadata only) carry
    ``adapter=None`` and are used for discovery/limitations.
    """

    def __init__(self, name: str, *, description: str = "",
                 capabilities: Optional[list] = None,
                 needs_key: bool = False, has_key: bool = False,
                 cost: str = "free", limitations: str = "",
                 security: str = "https", best_effort: bool = False,
                 llm_writes: bool = False, kind_filter: str = "web",
                 adapter: Optional[Any] = None):
        self.name = name
        self.description = description
        self.capabilities = set(capabilities or ["search"])
        self.needs_key = needs_key
        self.has_key = has_key
        self.cost = cost
        self.limitations = limitations
        self.security = security
        self.best_effort = best_effort
        self.llm_writes = llm_writes
        self.kind_filter = kind_filter
        self.adapter = adapter

    @property
    def configured(self) -> bool:
        if self.needs_key and not self.has_key:
            return False
        if self.adapter is None:
            return self.has_key if self.needs_key else True
        try:
            return self.adapter.configured()
        except Exception:
            return True

    def to_dict(self) -> dict:
        return {"name": self.name, "description": self.description,
                "capabilities": sorted(self.capabilities),
                "configured": self.configured, "needs_key": self.needs_key,
                "has_key": self.has_key, "cost": self.cost,
                "limitations": self.limitations, "security": self.security,
                "best_effort": self.best_effort, "kind_filter": self.kind_filter,
                "llm_writes": self.llm_writes}


# ---------------------------------------------------------------------------
# TOOLS
# ---------------------------------------------------------------------------
class Tool:
    """A callable MCP-ish tool bound to an implementation function."""

    def __init__(self, name: str, *, description: str, func: Callable,
                 input_schema: dict, output: str = "object",
                 skill: str = "", providers: Optional[list] = None,
                 capabilities: Optional[list] = None,
                 requirements: str = "", limitations: str = "",
                 security: str = "external content treated as data",
                 categories: Optional[list] = None):
        self.name = name
        self.description = description
        self.func = func
        self.input_schema = input_schema
        self.output = output
        self.skill = skill
        self.providers = providers or []
        self.capabilities = capabilities or []
        self.requirements = requirements
        self.limitations = limitations
        self.security = security
        self.categories = categories or []

    def invoke(self, **kwargs):
        return self.func(**kwargs)

    def to_dict(self) -> dict:
        return {"name": self.name, "description": self.description,
                "input_schema": self.input_schema, "output": self.output,
                "skill": self.skill, "providers": self.providers,
                "capabilities": self.capabilities,
                "requirements": self.requirements,
                "limitations": self.limitations, "security": self.security,
                "categories": self.categories}


class ProviderRegistry(Registry):
    def __init__(self):
        super().__init__("provider")

    def with_capability(self, cap: str) -> list[Provider]:
        return [p for p in self.all() if cap in p.capabilities]

    def configured_with(self, cap: str) -> list[Provider]:
        return [p for p in self.all() if cap in p.capabilities and p.configured]

    def configured(self) -> list[Provider]:
        return [p for p in self.all() if p.configured]


class ToolRegistry(Registry):
    def __init__(self):
        super().__init__("tool")

    def for_skill(self, skill: str) -> list[Tool]:
        return [t for t in self.all() if t.skill == skill]

    def to_schema_list(self) -> list[dict]:
        return [t.to_dict() for t in self.all()]


class SkillRegistry(Registry):
    """Skills carry full metadata; dependencies resolved by orchestrator."""

    def __init__(self):
        super().__init__("skill")

    def dependencies_of(self, name: str) -> list[str]:
        try:
            return list(self.get(name).get("dependencies", []))
        except Exception:
            return []

    def dependents(self, name: str) -> list[str]:
        return [k for k in self.names()
                if name in self.get(k).get("dependencies", [])]
