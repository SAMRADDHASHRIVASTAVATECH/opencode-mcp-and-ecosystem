"""Language catalog for software-engineering MCP.

Data source: the "Extreme Language & Project Advisor" catalog
(perfect_lanague_searching.py) — 5 tiers, 25 primary categories and 152
languages with tags, abstraction levels, guidance and utility mappings.

The catalog is injected at build/install time as package data
(se_mcp/data/language_catalog.json). Everything degrades gracefully to an
empty catalog if the data file is missing, never crashes.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

_CATALOG_PATH = Path(__file__).resolve().parent / "data" / "language_catalog.json"
_CATALOG: dict[str, Any] | None = None


def _load() -> dict[str, Any]:
    global _CATALOG
    if _CATALOG is not None:
        return _CATALOG
    try:
        _CATALOG = json.loads(_CATALOG_PATH.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        _CATALOG = {
            "primary_categories": [],
            "categorized_languages": {},
            "tag_mapping": {},
            "language_specific_tags": {},
            "abstraction_level_map": {},
            "guidance": {},
            "all_languages_details": {},
            "utility_category_mapping": {},
            "keyword_to_utility_map": {},
        }
    return _CATALOG


def reset_cache() -> None:
    """Reload the catalog from disk (used by tests)."""
    global _CATALOG
    _CATALOG = None
    _load()


def _details() -> dict[str, dict[str, Any]]:
    return _load().get("all_languages_details") or {}


def _norm(value: str) -> str:
    return " ".join(value.strip().lower().split())


def categories() -> list[dict[str, Any]]:
    """Return the 25 primary categories with the languages they group."""
    grouped = _load().get("categorized_languages") or {}
    primary = _load().get("primary_categories") or []
    if primary:
        ordered = [c for c in primary if c in grouped] + [c for c in grouped if c not in primary]
    else:
        ordered = list(grouped)
    out = []
    for name in ordered:
        langs = grouped.get(name) or []
        out.append(
            {
                "name": name,
                "languages": langs,
                "count": len(langs),
                "tags": list({t for l in langs for t in (_details().get(l, {}).get("tags") or [])}),
            }
        )
    return out


def summary() -> dict[str, Any]:
    """High-level facts about the catalog (tiers, categories, languages)."""
    details = _details()
    classified = [d for d in details.values() if d.get("categories")]
    return {
        "source": "Extreme Language & Project Advisor (perfect_lanague_searching.py)",
        "primary_categories": len(categories()),
        "category_names": [c["name"] for c in categories()],
        "languages_total": len(details),
        "languages_classified": len(classified),
        "abstraction_levels": sorted({v for v in (_load().get("abstraction_level_map") or {}).values()}),
    }


def search(query: str, limit: int = 25) -> list[dict[str, Any]]:
    """Find languages by name, tag or category keyword (case-insensitive)."""
    q = _norm(query)
    if not q:
        return []
    limit = max(1, min(int(limit), 100))
    hits: list[tuple[float, dict[str, Any]]] = []
    for name, detail in _details().items():
        cat = detail.get("categories") or []
        tags = detail.get("tags") or []
        hay_by_weight = [
            (name, 3.0),
            *((c, 1.5) for c in cat),
            *((t, 1.0) for t in tags),
        ]
        best = 0.0
        for hay, weight in hay_by_weight:
            if _norm(hay) == q:
                best = max(best, 3.0 * weight)
            elif q in _norm(hay):
                best = max(best, 1.0 * weight)
        if best:
            hits.append((best, detail))
    hits.sort(key=lambda item: (-item[0], _norm(item[1]["name"])))
    return [h[1] for h in hits[:limit]]


def get(name: str) -> dict[str, Any] | None:
    """Return the full record for one language by exact (case-insensitive) name."""
    details = _details()
    exact = details.get(name)
    if exact:
        return exact
    qn = _norm(name)
    for k, v in details.items():
        if _norm(k) == qn:
            return v
    return None


def tag_to_languages(tag: str) -> list[str]:
    """Languages carrying a given tag (case-insensitive)."""
    q = _norm(tag)
    if not q:
        return []
    mapping = _load().get("tag_mapping") or {}
    for key, langs in mapping.items():
        if _norm(key) == q:
            return sorted(set(langs)) if isinstance(langs, list) else sorted(langs)
    return []