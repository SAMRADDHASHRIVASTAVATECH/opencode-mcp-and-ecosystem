"""OLCAP Phone Call Management - unified phone-call control plane.

A host-side control plane + MCP server exposing structured phone.* tools.
Calls are placed on the phone via ADB/Wireless-ADB using the in-process
android_control library (no phone-side app required); OpenClaw voice calls
are the provider fallback. The `simulated` backend is only ever used as an
explicit fallback and is always reported honestly.
"""
__version__ = "1.1.0"

from .config import AppConfig
from .manager import PhoneManager
from .errors import OlcapError

__all__ = ["AppConfig", "PhoneManager", "OlcapError"]
