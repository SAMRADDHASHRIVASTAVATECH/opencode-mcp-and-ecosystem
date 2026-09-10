"""Independently callable individual skills (§31) plus the master command.

The master orchestrates the whole lifecycle; each individual skill is also
directly callable so the agent is never locked into a monolith.
"""
from __future__ import annotations

from typing import Optional

from ..controller import AndroidControl
from ..high import AndroidFacade, get_facade, reset_facade
from ..result import ActionResult, ResultBuilder


def _f(offline: Optional[bool] = None) -> AndroidFacade:
    """Build a fresh facade/controller each call (no cross-call state leaks,
    works in both offline and live mode)."""
    from ..controller import AndroidControl
    ctrl = AndroidControl(offline=offline)
    facade = AndroidFacade(ctrl, autorun=False)
    ctrl.discover()
    return facade


# ===========================================================================
# MASTER COMMAND (§30, §44)
# ===========================================================================
def android_control(offline: Optional[bool] = None) -> ActionResult:
    """DISCOVER -> INITIALIZE -> CONNECT -> VERIFY -> CAPABILITY SCAN -> READY
    (or, with an existing session: VERIFY -> READY)."""
    reset_facade()
    ctrl = AndroidControl(offline=offline)
    facade = AndroidFacade(ctrl, autorun=False)
    discovered = ctrl.discover()
    states = []
    for d in ctrl.registry.all():
        ctrl.capability_scan(d.device_id)
        states.append(ctrl.status(d.device_id))
    all_ready = bool(states) and all(
        s["connection_state"] == "connected" for s in states)
    act = ResultBuilder("android_control").single(
        "SUCCESS" if all_ready else "PARTIAL_SUCCESS",
        data={"state": "READY" if all_ready else "PARTIAL",
              "devices_connected": len(ctrl.registry.connected()),
              "devices_total": ctrl.registry.count(),
              "log": str(ctrl.log.path),
              "sessions": states})
    return act


# ===========================================================================
# Individual skills
# ===========================================================================
def android_discovery(offline: Optional[bool] = None) -> ActionResult:
    ctrl = AndroidControl(offline=offline)
    AndroidFacade(ctrl, autorun=False)
    discovered = ctrl.discover()
    return ResultBuilder("android_discovery").single(
        data=discovered)


def android_device_info(device: str = None,
                        offline: Optional[bool] = None) -> ActionResult:
    f = _f(offline)
    f.ctrl.discover()
    return f.info(device=device)


def android_shell(command: str, device: str = None,
                  offline: Optional[bool] = None) -> ActionResult:
    f = _f(offline)
    f.ctrl.discover()
    return f.shell(command, device=device)


def android_adb(offline: Optional[bool] = None) -> ActionResult:
    ctrl = AndroidControl(offline=offline)
    adb = ctrl._eng("adb")
    return ResultBuilder("android_adb").single(data={
        "version": adb.version(),
        "transport": ctrl.transport.name,
        "adb_exe": ctrl.adb_exe,
    })


def android_input(device: str = None, *, tap: tuple = None,
                  swipe: tuple = None, key: str = None, text: str = None,
                  offline: Optional[bool] = None) -> ActionResult:
    f = _f(offline)
    f.ctrl.discover()
    if tap:
        return f.tap(*tap, device=device)
    if swipe:
        return f.swipe(*swipe, device=device)
    if key:
        return f.key(key, device=device)
    if text is not None:
        return f.type(text, device=device)
    return ResultBuilder("android_input").single(
        "FAILED", error="provide one of tap/swipe/key/text")


def android_screen(device: str = None, *, screenshot: bool = False,
                   record: Optional[float] = None,
                   offline: Optional[bool] = None) -> ActionResult:
    f = _f(offline)
    f.ctrl.discover()
    if screenshot:
        return f.screenshot(device=device)
    if record:
        return f.screenrecord(seconds=record, device=device)
    return ResultBuilder("android_screen").single(
        "FAILED", error="provide screenshot=True or record=<seconds>")


def android_ui(device: str = None, *, action: str = "tree",
               query: dict = None, text: str = None,
               offline: Optional[bool] = None) -> ActionResult:
    f = _f(offline)
    f.ctrl.discover()
    if action == "tree":
        return f.ui_tree(device=device)
    if action == "find":
        return f.ui_find(device=device, **(query or {}))
    if action == "click":
        return f.ui_click(device=device, **(query or {}))
    if action == "type":
        return f.ui_type(text or "", device=device, **(query or {}))
    if action == "read":
        return f.ui_read(device=device)
    return ResultBuilder("android_ui").single(
        "FAILED", error=f"unknown action {action!r}")


def android_apps(device: str = None, *, action: str = "list",
                 package: str = "", offline: Optional[bool] = None) -> ActionResult:
    f = _f(offline)
    f.ctrl.discover()
    if action == "list":
        return f.apps_list(device=device)
    if action == "launch":
        return f.app_launch(package, device=device)
    if action == "stop":
        return f.app_stop(package, device=device)
    return ResultBuilder("android_apps").single(
        "FAILED", error=f"unknown action {action!r}")


def android_files(device: str = None, *, action: str = "list",
                  path: str = "/sdcard/", src: str = "", dst: str = "",
                  offline: Optional[bool] = None) -> ActionResult:
    f = _f(offline)
    f.ctrl.discover()
    if action == "list":
        return f.files_list(path, device=device)
    if action == "push":
        return f.file_push(src, dst, device=device)
    if action == "pull":
        return f.file_pull(src, dst, device=device)
    return ResultBuilder("android_files").single(
        "FAILED", error=f"unknown action {action!r}")


def android_intents(device: str = None, *, action: str = "open_settings",
                    url: str = "", panel: str = "",
                    offline: Optional[bool] = None) -> ActionResult:
    f = _f(offline)
    f.ctrl.discover()
    if action == "open_url":
        return f.open_url(url, device=device)
    if action == "open_settings":
        return f.open_settings(panel, device=device)
    return ResultBuilder("android_intents").single(
        "FAILED", error=f"unknown intent action {action!r}")


def android_vision(device: str = None,
                   offline: Optional[bool] = None) -> ActionResult:
    f = _f(offline)
    f.ctrl.discover()
    sessions = f._sessions(device)
    rb = ResultBuilder("android_vision")
    for s in sessions:
        obs = f.ctrl.vision.observe(s.serial)
        rb.per_device(s.device_id, serial=s.serial, status="SUCCESS",
                      data={"backend": obs["backend"],
                            "png_bytes": obs["png_bytes"],
                            "note": obs["note"]})
    return rb.build()


def android_recovery(device: str = None,
                     offline: Optional[bool] = None) -> ActionResult:
    f = _f(offline)
    f.ctrl.discover()
    return f.recover(device=device)


def android_multi_device(offline: Optional[bool] = None) -> ActionResult:
    ctrl = AndroidControl(offline=offline)
    facade = AndroidFacade(ctrl, autorun=False)
    ctrl.discover()
    return ResultBuilder("android_multi_device").single(data={
        "devices": [d.device_id for d in ctrl.registry.all()],
        "count": ctrl.registry.count(),
        "groups": facade.groups.names(),
    })


def android_remote_touchpad(*, action: str = "status", bind: str = None,
                            secret: str = None,
                            offline: Optional[bool] = None) -> ActionResult:
    """Manage the vendored remote-touchpad host (phone-as-PC-input companion).

    This is the reverse-direction capability: an authorized Android phone's
    browser controls THIS Windows PC's pointer and keyboard over the LAN.
    actions: status | start | stop | resolve. Requires AC_RT_ENABLED=true and
    a real remote-touchpad binary (see AC_RT_BIN / downloader script).
    """
    from ..high import AndroidFacade
    from ..controller import AndroidControl
    ctrl = AndroidControl(offline=offline)
    f = AndroidFacade(ctrl, autorun=False)
    if not ctrl.settings.rt_enabled and action in ("start",):
        from ..result import ResultBuilder
        return ResultBuilder("android_remote_touchpad").single(
            "FAILED", error="remote-touchpad disabled; set AC_RT_ENABLED=true")
    return f.remote_touchpad(action, bind=bind, secret=secret)


def android_messaging(device: str = None, *, action: str = "send",
                      message: str = "", structured: dict = None,
                      offline: Optional[bool] = None) -> ActionResult:
    """Agent <-> device messaging channel (§5).

    action="send": send plain `message` (and/or `structured`) agent->device(s).
    action="receive": poll device(s)->agent messages since last read.
    action="ingest": simulate an inbound (device->agent) message for testing.
    """
    f = _f(offline)
    if action == "send":
        return f.send_message(message, device=device, structured=structured)
    if action == "receive":
        return f.receive_messages(device=device)
    if action == "ingest":
        return f.ingest_message(message, device=device or "all",
                                structured=structured)
    return ResultBuilder("android_messaging").single(
        "FAILED", error=f"unknown action {action!r}")


ALL_SKILLS = {
    "android_control": android_control,
    "android_discovery": android_discovery,
    "android_adb": android_adb,
    "android_shell": android_shell,
    "android_device_info": android_device_info,
    "android_input": android_input,
    "android_screen": android_screen,
    "android_ui": android_ui,
    "android_apps": android_apps,
    "android_files": android_files,
    "android_intents": android_intents,
    "android_vision": android_vision,
    "android_recovery": android_recovery,
    "android_multi_device": android_multi_device,
    "android_messaging": android_messaging,
    "android_remote_touchpad": android_remote_touchpad,
}
