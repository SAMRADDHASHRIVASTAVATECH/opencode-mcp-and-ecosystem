"""
Universal Web Research MCP + Skill System.

A portable, import-ready deep-research worker for MCP-compatible agent
environments. Supports TWO modes:

  * MODE A - DIRECT TOOL USE : call any single capability, e.g. ``search_web``.
  * MODE B - AUTONOMOUS RESEARCH : call ``deep_research`` and the orchestrator
    composes providers, skills, search, crawler, readers, evidence, verification
    and contradiction hunting.

Everything heavy is processed server-side; the calling agent receives compact,
structured evidence. External content is treated as untrusted data (never
instructions). See ``src/universal_research/mcp_server.py`` for the MCP wiring,
``skills/`` for the traveling skill set and ``tests/`` for the test suite.
"""

__version__ = "1.0.0"

# Public convenience namespace
from . import models  # noqa: E402
from .registry.base import SkillRegistry, ToolRegistry, ProviderRegistry  # noqa: E402

__all__ = ["models", "SkillRegistry", "ToolRegistry", "ProviderRegistry", "__version__"]
