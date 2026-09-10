"""OLCAP realtime multimodal assistant."""
from .config import AppConfig
from .assistant import Assistant
from .errors import AssistantError

__all__ = ["AppConfig", "Assistant", "AssistantError"]
__version__ = "1.0.0"
