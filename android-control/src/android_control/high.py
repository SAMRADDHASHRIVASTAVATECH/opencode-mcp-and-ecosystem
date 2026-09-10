"""High-level agent-facing facade (the §29 API).

Methods are thin, safe, multi-device capable wrappers over the engines. Each
returns an :class:`ActionResult` with per-device outcomes for multi-device
operations, and never collapses them into one ambiguous status.

All methods accept either an explicit ``device`` selector (None => all
connected) so the agent can drive one phone, an explicit list, a group, or the
whole fleet without translating anything to ADB.
"""
from __future__ import annotations

import re
from typing import Callable, List, Optional

from . import errors
from .controller import AndroidControl
from .devices.registry import DeviceSession
from .orchestration.multi import DeviceGroups, MultiRunner
from .result import ActionResult, ResultBuilder, SUCCESS


class AndroidFacade:
    def __init__(self, ctrl: AndroidControl, *, autorun: bool = True):
        self.ctrl = ctrl
        self.groups = DeviceGroups(ctrl.registry)
        self.runner = MultiRunner
        if autorun and not ctrl.offline:
            ctrl.discover()

    # ------------------------------------------------------------------ #
    # device selection resolution
    # ------------------------------------------------------------------ #
    def _sessions(self, device: Optional[str]) -> List[DeviceSession]:
        if device is None:
            return self.ctrl.registry.connected()
        if device in self.groups.names():
            return self.groups.members(device)
        return self.ctrl.registry.select(device)

    def _run(self, op: str, fn: Callable[[DeviceSession], dict],
             device: Optional[str], parallel: bool = True) -> ActionResult:
        sessions = self._sessions(device)
        if not sessions:
            return ResultBuilder(op).single("FAILED",
                                            error="no connected devices matched")
        return MultiRunner(op).run(sessions, fn, parallel=parallel)

    def _one(self, device: str) -> DeviceSession:
        s = self._sessions(device)
        if len(s) != 1:
            raise errors.AmbiguousDeviceError(f"expected one device, got {len(s)}")
        return s[0]

    # ------------------------------------------------------------------ #
    # §29 core API
    # ------------------------------------------------------------------ #
    def discover(self) -> ActionResult:
        return ResultBuilder("discover").single(
            data=self.ctrl.discover())

    def devices(self) -> ActionResult:
        return ResultBuilder("devices").single(data=self.ctrl.devices())

    def status(self, device: str = None) -> ActionResult:
        return self._run("status", lambda s: {"data": s.profile()}, device)

    def capabilities(self, device: str = None) -> ActionResult:
        def f(s):
            cap = self.ctrl.capability_scan(s.device_id)
            return {"data": cap}
        return self._run("capabilities", f, device)

    def connect(self, device: str) -> ActionResult:
        try:
            s = self.ctrl._by_id_or_serial(device)
            st = self.ctrl.reconnect(s.device_id)
            return ResultBuilder("connect").single(data=st)
        except errors.AndroidControlError as e:
            return ResultBuilder("connect").single("FAILED", error=str(e))

    def disconnect(self, device: str) -> ActionResult:
        """Disconnect a single device from the registry/adb."""
        try:
            s = self.ctrl._by_id_or_serial(device)
            self.ctrl.disconnect(s.device_id)
            return ResultBuilder("disconnect").single(
                data=self.ctrl.status(s.device_id))
        except errors.AndroidControlError as e:
            return ResultBuilder("disconnect").single("FAILED", error=str(e))

    def reconnect(self, device: str = None) -> ActionResult:
        def f(s):
            st = self.ctrl.reconnect(s.device_id)
            return {"data": st}
        return self._run("reconnect", f, device)

    def shell(self, command: str, device: str = None) -> ActionResult:
        def f(s):
            out = self.ctrl.shell.shell(s.serial, command)
            return {"data": out}
        return self._run("shell", f, device)

    def screenshot(self, device: str = None, dest: str = None) -> ActionResult:
        def f(s):
            p = self.ctrl.screen.screenshot(s.serial, dest=dest)
            return {"data": p}
        return self._run("screenshot", f, device)

    def screenrecord(self, seconds: float = 8.0, device: str = None) -> ActionResult:
        def f(s):
            p = self.ctrl.screen.screenrecord(s.serial, seconds=seconds)
            return {"data": p}
        return self._run("screenrecord", f, device)

    def ui_tree(self, device: str = None) -> ActionResult:
        def f(s):
            return {"data": self.ctrl.ui.tree(s.serial)}
        return self._run("ui_tree", f, device)

    def ui_find(self, device: str = None, **kw) -> ActionResult:
        def f(s):
            return {"data": [n.to_dict() for n in
                             self.ctrl.ui.find(s.serial, **kw)]}
        return self._run("ui_find", f, device)

    def ui_click(self, device: str = None, **kw) -> ActionResult:
        def f(s):
            self.ctrl.ui.click_element(s.serial, **kw)
            return {"status": SUCCESS, "verification": "clicked matched element"}
        return self._run("ui_click", f, device)

    def ui_type(self, text: str, device: str = None, **kw) -> ActionResult:
        def f(s):
            self.ctrl.ui.type_into(s.serial, text, **kw)
            return {"status": SUCCESS, "verification": "typed into field"}
        return self._run("ui_type", f, device)

    def ui_read(self, device: str = None) -> ActionResult:
        def f(s):
            return {"data": self.ctrl.ui.read_text(s.serial)}
        return self._run("ui_read", f, device)

    # input primitives
    def tap(self, x: int, y: int, device: str = None) -> ActionResult:
        def f(s):
            self.ctrl.input.tap(s.serial, x, y)
            return {"status": SUCCESS}
        return self._run("tap", f, device)

    def long_press(self, x: int, y: int, duration_ms: int = 600,
                   device: str = None) -> ActionResult:
        def f(s):
            self.ctrl.input.long_press(s.serial, x, y, duration_ms)
            return {"status": SUCCESS}
        return self._run("long_press", f, device)

    def scroll(self, direction: str = "down", steps: int = 4,
               device: str = None) -> ActionResult:
        def f(s):
            self.ctrl.input.scroll(s.serial, direction, steps)
            return {"status": SUCCESS}
        return self._run("scroll", f, device)

    def swipe(self, x1, y1, x2, y2, dur: int = 300,
              device: str = None) -> ActionResult:
        def f(s):
            self.ctrl.input.swipe(s.serial, x1, y1, x2, y2, dur)
            return {"status": SUCCESS}
        return self._run("swipe", f, device)

    def key(self, keycode: str, device: str = None) -> ActionResult:
        def f(s):
            self.ctrl.input.key(s.serial, keycode)
            return {"status": SUCCESS}
        return self._run("key", f, device)

    def type(self, text: str, device: str = None) -> ActionResult:
        def f(s):
            self.ctrl.input.text(s.serial, text)
            return {"status": SUCCESS}
        return self._run("type", f, device)

    def back(self, device: str = None) -> ActionResult:
        return self.key("back", device)

    def home(self, device: str = None) -> ActionResult:
        return self.key("home", device)

    def recents(self, device: str = None) -> ActionResult:
        return self.key("recents", device)

    # apps
    def apps_list(self, device: str = None) -> ActionResult:
        def f(s):
            return {"data": self.ctrl.apps.list_packages(s.serial)}
        return self._run("apps_list", f, device)

    def app_launch(self, package: str, device: str = None) -> ActionResult:
        def f(s):
            self.ctrl.apps.launch(s.serial, package)
            return {"status": SUCCESS, "verification": "activity/package launched"}
        return self._run("app_launch", f, device)

    def app_stop(self, package: str, device: str = None) -> ActionResult:
        def f(s):
            self.ctrl.apps.stop(s.serial, package)
            return {"status": SUCCESS}
        return self._run("app_stop", f, device)

    # intents
    def open_url(self, url: str, device: str = None) -> ActionResult:
        def f(s):
            self.ctrl.intents.open_url(s.serial, url)
            return {"status": SUCCESS}
        return self._run("open_url", f, device)

    def open_settings(self, panel: str = "", device: str = None) -> ActionResult:
        def f(s):
            self.ctrl.intents.open_settings(s.serial, panel)
            return {"status": SUCCESS}
        return self._run("open_settings", f, device)

    # files
    def files_list(self, path: str = "/sdcard/", device: str = None) -> ActionResult:
        def f(s):
            return {"data": self.ctrl.files.list(s.serial, path)}
        return self._run("files_list", f, device)

    def file_push(self, src: str, dst: str, device: str = None) -> ActionResult:
        def f(s):
            self.ctrl.files.push(src, dst, s.serial)
            return {"status": SUCCESS, "verification": "file verified on device"}
        return self._run("file_push", f, device)

    def file_pull(self, src: str, dst: str, device: str = None) -> ActionResult:
        def f(s):
            p = self.ctrl.files.pull(src, dst, s.serial)
            return {"data": p}
        return self._run("file_pull", f, device)

    # info / logs / dumpsys
    def info(self, device: str = None) -> ActionResult:
        def f(s):
            return {"data": self.ctrl.info.profile(s.serial)}
        return self._run("info", f, device)

    def dumpsys(self, service: str, device: str = None) -> ActionResult:
        def f(s):
            return {"data": self.ctrl.shell.dumpsys(s.serial, service)}
        return self._run("dumpsys", f, device)

    def logs(self, device: str = None, lines: int = 200) -> ActionResult:
        def f(s):
            return {"data": self.ctrl.shell.logcat(s.serial, lines=lines)}
        return self._run("logs", f, device)

    def verify(self, device: str = None) -> ActionResult:
        def f(s):
            st = self.ctrl.health_check(s.device_id)
            return {"data": st}
        return self._run("verify", f, device)

    # ================================================================== #
    # §5 messaging (agent <-> device application channel)
    # ================================================================== #
    def send_message(self, message: str, device: str = None,
                     structured: dict = None) -> ActionResult:
        """Send a text/structured message from the agent to device(s)."""
        def f(s):
            msg = self.ctrl.message.send(s.serial, text=message, data=structured)
            return {"data": msg}
        return self._run("send_message", f, device)

    def receive_messages(self, device: str = None) -> ActionResult:
        """Receive messages sent by device(s) to the agent since last read."""
        def f(s):
            msgs = self.ctrl.message.receive(s.serial)
            return {"data": msgs}
        return self._run("receive_messages", f, device)

    def ingest_message(self, message: str, device: str = "all",
                       structured: dict = None) -> ActionResult:
        """Simulate/route an inbound (device->agent) message for testing or when
        the companion reports it out-of-band."""
        def f(s):
            self.ctrl.message.ingest(s.serial, text=message, data=structured)
            return {"status": SUCCESS}
        return self._run("ingest_message", f, device)

    # ================================================================== #
    # Remote Touchpad companion backend (phone controls this PC)
    # ================================================================== #
    def remote_touchpad(self, action: str = "status", *,
                        bind: str = None, secret: str = None) -> ActionResult:
        """Manage the vendored remote-touchpad host on this PC.

        actions:
          status      - current running state + connect URL
          start       - start the host (returns URL for a phone browser)
          stop        - stop the host
          resolve     - report the resolved binary path (install check)
        """
        rt = self.ctrl.remote_touchpad
        try:
            if action == "start":
                info = rt.start(bind=bind, secret=secret)
                return ResultBuilder("remote_touchpad.start").single(
                    data=info)
            if action == "stop":
                return ResultBuilder("remote_touchpad.stop").single(
                    data=rt.stop())
            if action == "resolve":
                return ResultBuilder("remote_touchpad.resolve").single(
                    data={"binary": rt.resolve_binary()})
            # status default
            return ResultBuilder("remote_touchpad.status").single(
                data=rt.status())
        except errors.AndroidControlError as e:
            return ResultBuilder("remote_touchpad." + action).single(
                "FAILED", error=str(e))

    def recover(self, device: str = None) -> ActionResult:
        return self.reconnect(device)

    def restart(self, device: str) -> ActionResult:
        """Reboot a device (requires reconnect to be safe for the fleet)."""
        s = self._one(device)
        try:
            self.ctrl.shell.reboot(s.serial)
            self.ctrl.reconnect(s.device_id)
            return ResultBuilder("restart").single(
                data=self.ctrl.status(s.device_id))
        except errors.AndroidControlError as e:
            return ResultBuilder("restart").single("FAILED", error=str(e))


# singleton-ish accessor
_facade = None


def get_facade(offline: Optional[bool] = None, **kw) -> AndroidFacade:
    global _facade
    if _facade is None:
        ctrl = AndroidControl(offline=offline, **kw)
        _facade = AndroidFacade(ctrl)
    return _facade


def reset_facade():
    global _facade
    _facade = None
