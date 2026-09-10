"""
Universal PDF Management & Creation Skill Repository — Python engine.

This package is the shared, tool-abstraction-backed engine behind the
interconnected skill system. Every individual skill (see ``../skills``)
and the Universal PDF Orchestrator (see ``universal_pdf/orchestration``)
dispatch to these modules.

Design principles:
  * Small/local-model friendly: no document is ever loaded wholesale into
    any LLM context. All heavy work is done here on disk / in memory as
    pages, chunks, or streams.
  * Tool abstraction: operations route through ``universal_pdf.tools`` so
    that a missing library degrades gracefully to an alternative or a
    documented limitation instead of a hard failure.
  * Provenance & state: derived output carries source (doc/page/chunk/
    method/confidence) and the document state lives in a persistent
    knowledge store, not in the model's memory.
  * Validation: every major operation is verified and reports an Outcome.
"""

__version__ = "1.0.0"
__all__ = ["engine", "core", "tools", "orchestration", "__version__"]
