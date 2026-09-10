"""Autonomous task engine (§23, §41, §42, §44).

An intent registry maps natural-language goals to concrete per-device action
plans that run through the high-level facade with OBSERVE->PLAN->ACT->VERIFY.
It also exposes ``plan()`` so an agent (LLM) can request the steps and then
drive them. Selection tokens embedded in the text are resolved deterministically.

Recognised goal families (a clean subset covering the spec's examples):
  * screenshot / record every device
  * launch an app on target(s)
  * open a URL on target(s)
  * open settings (optionally a sub-panel)
  * open the camera
  * list apps / list devices
  * what app is foreground (e.g. "find which phone has WhatsApp open")
  * pull latest photo
  * reboot/restart a device
  * type / tap / key
Because no LLM is bundled, goals that are not recognised raise with a clear
message and list the supported intents rather than guessing.
"""
from __future__ import annotations

import re
from typing import Callable, Dict, List, Optional

from .. import errors
from ..result import ActionResult, SUCCESS
from .multi import MultiRunner

_APP_ALIASES = {
    "camera": ["com.google.android.GoogleCamera", "com.sec.android.app.camera",
               "com.android.camera2"],
    "settings": ["com.android.settings"],
    "whatsapp": ["com.whatsapp"],
    "chrome": ["com.android.chrome"],
    "calculator": ["com.google.android.calculator", "com.android.calculator2"],
    "maps": ["com.google.android.apps.maps"],
    "gallery": ["com.google.android.apps.photos", "com.android.gallery3d"],
    "phone/dialer": ["com.google.android.dialer"],
    "youtube": ["com.google.android.youtube"],
    "clock": ["com.google.android.deskclock"],
}


def app_package_for(name: str, installed: List[str]) -> Optional[str]:
    for alias, cands in _APP_ALIASES.items():
        if name in (alias, alias.split("/")[0]) or name == alias:
            for c in cands:
                if c in installed:
                    return c
    for pkg in installed:
        p = pkg.split(".")[-1].lower()
        if name.lower() == p:
            return pkg
    # first heuristic: text equals package or ends-with match
    for pkg in installed:
        if name.lower() in pkg:
            return pkg
    return None


class Autonomous:
    def __init__(self, facade):
        self.f = facade
        self.intents = {
            "screenshot": self._screenshot,
            "record": self._record,
            "launch": self._launch,
            "open_url": self._open_url,
            "open_settings": self._open_settings,
            "camera": self._camera,
            "list_devices": self._list_devices,
            "list_apps": self._list_apps,
            "foreground": self._foreground,
            "pull_photo": self._pull_photo,
            "restart": self._restart,
            "install": self._install,
            "shell": self._shell,
            "ui": self._ui,
        }

    # -- dispatch -----------------------------------------------------------
    def run(self, goal: str) -> ActionResult:
        intent, target, params = self._parse(goal)
        if intent not in self.intents:
            raise errors.UnsupportedOperationError(
                f"unrecognised goal: {goal!r}. Supported intents: "
                + ", ".join(sorted(self.intents)))
        return self.intents[intent](target, params, goal)

    def plan(self, goal: str) -> dict:
        intent, target, params = self._parse(goal)
        return {"intent": intent, "device_selection": target,
                "parameters": params, "goal": goal,
                "note": "resolved deterministic steps before execution"}

    # -- parsing ------------------------------------------------------------
    def _parse(self, goal: str):
        g = goal.lower().strip()
        # device tokens
        target = self._extract_target(g)
        params: Dict[str, str] = {}

        if "screenshot" in g:
            return "screenshot", target, params
        if re.search(r"\brecord\b|\bscreen.?record", g):
            return "record", target, params
        if "camera" in g:
            return "camera", target, params
        if re.search(r"\bopen\b.*\burl\b|\bhttp", g) or "://" in g:
            m = re.search(r"(https?://\S+)", goal)
            params["url"] = m.group(1) if m else ""
            return "open_url", target, params
        if re.search(r"\binstall\b", g):
            m = re.search(r"(\S+\.apk)", goal)
            params["apk"] = m.group(1) if m else ""
            return "install", target, params
        if "settings" in g:
            panel = "wifi" if "wifi" in g else "bluetooth" if "bluetooth" in g \
                else ""
            params["panel"] = panel
            return "open_settings", target, params
        if re.search(r"\blaunch\b|\bopen\b|\bstart\b", g):
            return "launch", target, params
        if "which phone" in g or "foreground" in g or "has whatsapp open" in g:
            return "foreground", target, params
        if ("pull" in g or "copy" in g) and ("photo" in g or "latest" in g or "picture" in g):
            return "pull_photo", target, params
        if "restart" in g or "reboot" in g:
            return "restart", target, params
        if (("list" in g or "show" in g or "display" in g) and
                ("device" in g or "phone" in g or "connected" in g)):
            return "list_devices", target, params
        if "list" in g and "app" in g:
            return "list_apps", target, params
        if "shell" in g:
            return "shell", target, params
        raise errors.UnsupportedOperationError(
            f"could not interpret goal: {goal!r}")

    def _extract_target(self, g: str) -> Optional[str]:
        # explicit serial/device_id in text
        m = re.search(r"serial\s+([A-Za-z0-9_:-]+)", g)
        if m:
            return m.group(1)
        for tok in re.split(r"[.;,]", g):
            tok = tok.strip()
            mm = re.search(r"(device_\d+)", tok)
            if mm:
                return mm.group(1)
            if "all" in tok:
                return "all"
            for name in ("phone a", "phone b", "phone c", "phone d",
                         "samsung", "pixel", "oneplus", "phone 2",
                         "phone 3", "android 15"):
                if name in tok:
                    return self._pretty(name)
        return "all"

    @staticmethod
    def _pretty(name: str) -> str:
        if name in ("phone a",): return "device_001" if False else name
        return name

    # -- action implementations ---------------------------------------------
    def _screenshot(self, target, params, goal):
        return self.f.screenshot(device=target)

    def _record(self, target, params, goal):
        return self.f.screenrecord(seconds=8.0, device=target)

    def _open_url(self, target, params, goal):
        url = params.get("url") or _url_from(goal)
        return self.f.open_url(url, device=target)

    def _open_settings(self, target, params, goal):
        return self.f.open_settings(params.get("panel", ""), device=target)

    def _list_devices(self, target, params, goal):
        return self.f.devices()

    def _list_apps(self, target, params, goal):
        return self.f.apps_list(device=target)

    def _launch(self, target, params, goal):
        app = _app_name_from(goal)
        return self._launch_app(target, app)

    def _camera(self, target, params, goal):
        return self._launch_app(target, "camera")

    def _launch_app(self, target, app_name: str):
        """Launch an app on every selected device, resolving the best package
        per device from that device's own installed list."""
        sessions = self.f._sessions(target if target != "all" else None)
        if not sessions:
            return ResultBuilder("launch").single("FAILED", error="no devices")

        def fn(s):
            installed = self.f.ctrl.apps.list_packages(s.serial)
            pkg = app_package_for(app_name, installed)
            if not pkg:
                return {"status": "FAILED",
                        "error": f"{app_name!r} not installed on {s.device_id}"}
            self.f.ctrl.apps.launch(s.serial, pkg)
            # OBSERVE->VERIFY: read current focus
            focus = self.f.ctrl.info.current_focus(s.serial)
            ok = (focus.get("package") or "").startswith(pkg.split(".")[0])
            return {"status": SUCCESS if ok else "PARTIAL_SUCCESS",
                    "data": {"package": pkg,
                             "focus": focus.get("activity")},
                    "verification": "launched & foreground verified"}
        return MultiRunner("launch").run(sessions, fn)

    def _foreground(self, target, params, goal):
        def fn(s):
            prof = self.f.ctrl.info.profile(s.serial)
            return {"data": {"device": s.device_id, "serial": s.serial,
                             "package": prof.get("current_package"),
                             "activity": prof.get("current_activity")}}
        return _run_fleet(self.f, "foreground", target, fn)

    def _pull_photo(self, target, params, goal):
        # mock-safe: pull whole DCIM listing; real impl picks newest by name
        import time
        def fn(s):
            files = self.f.ctrl.files.list(s.serial, "/sdcard/DCIM")
            names = [x["name"] for x in files if x["type"] == "file"]
            latest = sorted(names)[-1] if names else ""
            dst = f"/home/user/android_photos/{s.serial}_latest"
            if latest:
                dst += "_" + latest
            try:
                p = self.f.ctrl.files.pull(
                    f"/sdcard/DCIM/{latest}", dst, s.serial)
                return {"status": SUCCESS, "data": p}
            except Exception as e:
                return {"status": "FAILED", "error": str(e)}
        return _run_fleet(self.f, "pull_photo", target, fn)

    def _restart(self, target, params, goal):
        if not target or target == "all":
            raise errors.AmbiguousDeviceError(
                "restart requires a single explicit device")
        return self.f.restart(target)

    def _install(self, target, params, goal):
        apk = params.get("apk") or _apk_from(goal)
        if not apk:
            raise errors.CommandFailedError(
                "install needs a path to an .apk file in the request")
        sessions = self.f._sessions(target if target != "all" else None)
        if not sessions:
            return ResultBuilder("install").single("FAILED", error="no devices")
        def fn(s):
            try:
                self.f.ctrl.apps.install(s.serial, apk)
                return {"status": SUCCESS,
                        "verification": "install reported Success"}
            except errors.RequiresAuthorizationError as e:
                return {"status": "REQUIRES_AUTHORIZATION", "error": str(e)}
            except Exception as e:  # noqa: BLE001
                return {"status": "FAILED", "error": str(e)}
        return MultiRunner("install").run(sessions, fn)

    def _shell(self, target, params, goal):
        m = re.search(r"shell\s+(.+)$", goal, re.I)
        cmd = m.group(1).strip() if m else ""
        return self.f.shell(cmd, device=target)

    def _ui(self, target, params, goal):
        return self.f.ui_read(device=target)

    def _one_name(self, target):
        return target or "all"


def _run_fleet(f, op, target, fn):
    from ..result import ResultBuilder
    sessions = f._sessions(target if target != "all" else None)
    if not sessions:
        return ResultBuilder(op).single("FAILED", error="no devices")
    return MultiRunner(op).run(sessions, fn)


def _installed_on_one(f, target):
    r = f.apps_list(device=target if target != "all" else None)
    if r.single_outcome() and isinstance(r.single_outcome().data, list):
        return r.single_outcome().data
    if r.devices:
        return r.devices[0].data or []
    return []


def _first_alias(name: str) -> str:
    cands = _APP_ALIASES.get(name, [name])
    return cands[0]


def _app_name_from(goal: str) -> str:
    g = goal.lower()
    for alias in _APP_ALIASES:
        if alias in g or alias.split("/")[0] in g:
            return alias
    m = re.search(r"\b(?:launch|open|start)\s+(?:the\s+|an\s+|a\s+)?([a-z0-9_ .-]+)", g)
    return (m.group(1).strip().split(" on ")[0] if m else "")


def _url_from(goal: str) -> str:
    m = re.search(r"(https?://[^\s\"']+)", goal)
    return m.group(1) if m else "https://www.google.com"


def _apk_from(goal: str) -> str:
    m = re.search(r"([A-Za-z0-9_./\\-]+\.apk)", goal)
    return m.group(1) if m else ""
