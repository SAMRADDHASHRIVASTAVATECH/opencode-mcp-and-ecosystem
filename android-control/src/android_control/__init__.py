"""Universal Android Control — master skill + individual skills.

Importing the package does NOT require ADB or any device. Nothing is
initialised until you call ``android_control()`` / ``boot()`` / a skill.

Quick offline demo (no phone, deterministic):
    import android_control
    r = android_control.android_control(offline=True)
    r.to_dict()            # -> fleet session statuses

Live use (Windows host with adb):
    import android_control as ac
    f = ac.boot()                    # discover + register devices
    ac.android_control()
"""
from __future__ import annotations

from typing import Optional

from .config import Settings, load_settings, save_env_example
from .controller import AndroidControl
from .high import AndroidFacade
from .result import ActionResult, SUCCESS, FAILED, PARTIAL_SUCCESS, OFFLINE
from .skills import (
    android_control, android_discovery, android_adb, android_shell,
    android_device_info, android_input, android_screen, android_ui,
    android_apps, android_files, android_intents, android_vision,
    android_recovery, android_multi_device, android_messaging,
    android_remote_touchpad, ALL_SKILLS,
)
from . import mcp as _mcp
from .mcp import handle_request, serve_stdio, build_tools

__version__ = "1.0.0"
__all__ = [
    "android_control", "android_discovery", "android_adb", "android_shell",
    "android_device_info", "android_input", "android_screen", "android_ui",
    "android_apps", "android_files", "android_intents", "android_vision",
    "android_recovery", "android_multi_device", "android_messaging",
    "android_remote_touchpad", "ALL_SKILLS",
    "handle_request", "serve_stdio", "build_tools",
    "AndroidControl", "AndroidFacade", "Settings", "load_settings",
    "save_env_example", "boot", "boot_offline", "run_goal", "ActionResult",
    "SUCCESS", "FAILED", "PARTIAL_SUCCESS", "OFFLINE", "__version__",
]


def boot(settings: Settings = None) -> AndroidFacade:
    """Discover/connect/register real devices and return the control facade."""
    ctrl = AndroidControl(settings=settings, offline=False)
    facade = AndroidFacade(ctrl, autorun=False)
    ctrl.discover()
    return facade


def boot_offline() -> AndroidFacade:
    """Deterministic, no-hardware facade (good for demos & selfchecks)."""
    ctrl = AndroidControl(offline=True)
    facade = AndroidFacade(ctrl, autorun=False)
    ctrl.discover()
    return facade


def run_goal(goal: str, offline: Optional[bool] = None) -> ActionResult:
    """Translate a natural-language goal into an executed multi-device action."""
    from .orchestration.autonomous import Autonomous
    facade = boot_offline() if offline else boot()
    return Autonomous(facade).run(goal)


def control(settings: Settings = None) -> AndroidControl:
    """Low-level master controller for advanced use."""
    return AndroidControl(settings=settings, offline=False)
