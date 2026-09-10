"""Document research engine (#16, #17).

Parses many document types externally into clean text, chunks large documents,
indexes chunks for retrieval, and lets research pull only the needed chunk —
never the whole document into the calling model.
"""
from .engine import DocumentEngine, TextDocument

__all__ = ["DocumentEngine", "TextDocument"]
