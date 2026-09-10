"""Self-improvement engine: persistent, versioned, auditable experience memory.

Improvement happens through validated knowledge/lessons only. Two modes:

* Cloud Mode  - memory learning only (never touches any model file).
* Local Mode  - same memory learning PLUS a local-model fine-tuning mechanism
                that progressively specialises the local LLM you use for tasks.

The engine/assistant model and its safeguards are never modified; in Local mode
the improvement target is the separate local model you opt in to improving.
"""
from .config import MemoryConfig
from .store import Store
from .engine import ExperienceEngine
from . import mode

__all__ = ["MemoryConfig", "Store", "ExperienceEngine", "mode"]
__version__ = "1.0.0"
