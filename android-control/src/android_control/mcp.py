"""MCP (Model Context Protocol) server for the unified Android Control system.

Exposes the whole agent surface — the ADB Android-control engine (screen,
touch/keyboard, files, messaging, multi-device) AND the Remote Touchpad
companion — as MCP **tools / resources / prompts** over stdio, so any MCP
client / agent host can drive it. The same package remains importable as a
normal Python library (this module is only needed to serve MCP).

Transport: newline-delimited JSON-RPC 2.0 over stdio (SDK-independent — no MCP
SDK dependency). Every request goes through ``_safe_handle`` so a bad request
never kills the loop.
"""
from __future__ import annotations

import json
import sys
from typing import Any, Dict, List, Optional

from .errors import AndroidControlError
from .result import ActionResult

PROTOCOL_VERSION = "2024-11-05"
SERVER_NAME = "android-control"
SERVER_VERSION = "1.0.0"

# ---------------------------------------------------------------------------
# Tool catalogue (name -> binder). Each binder takes (facade, args) -> dict
# ---------------------------------------------------------------------------
# device is an optional string: None/omitted => all connected; or an id/serial/
# model token, or a group name.


def _sessions_arg(args: Dict[str, Any]) -> Optional[str]:
    d = args.get("device")
    return d if d not in (None, "", "all") else None


class _B:
    """Tool binder: (callable, input_schema, description)."""

    def __init__(self, fn, schema: dict, description: str):
        self.fn = fn
        self.schema = schema
        self.description = description

    def run(self, facade, args) -> ActionResult:
        return self.fn(facade, args)


def _d(*, device=None, **rest) -> Dict[str, Any]:
    schema: Dict[str, Any] = {
        "type": "object",
        "properties": {"device": {
            "type": "string",
            "description": ("Target: omit or 'all' for every connected device; "
                            "or a device id/serial/model, or a group name.")}},
    }
    if device:
        schema["properties"].update(device)
    if rest:
        schema["properties"].update(rest)
    schema["required"] = []
    return schema


def _pr(props: Dict[str, dict], required: Optional[List[str]] = None):
    s = {"type": "object", "properties": props,
         "required": required or list(props)}
    return s


# ---------------------------------------------------------------------------
# Tool registry
# ---------------------------------------------------------------------------
def build_tools() -> Dict[str, _B]:
    """Return name -> binder for every MCP tool."""

    tools: Dict[str, _B] = {}

    # -- discovery / connection --------------------------------------------
    tools["list_devices"] = _B(
        lambda f, a: f.devices(),
        _pr({"include_all": {"type": "boolean",
                             "description": "include offline sessions"}}),
        "List every discovered Android device with its profile.")
    tools["discover"] = _B(
        lambda f, a: f.discover(),
        _pr({}),
        "Discover/register currently attached Android devices.")
    tools["status"] = _B(
        lambda f, a: f.status(device=_sessions_arg(a)),
        _d(), "Get device status/profile (default: all connected).")
    tools["connect"] = _B(
        lambda f, a: f.connect(a["device"]),
        _pr({"device": {"type": "string"}}),
        "Reconnect/connect a single device by id/serial.")
    tools["disconnect"] = _B(
        lambda f, a: f.disconnect(a["device"]),
        _pr({"device": {"type": "string"}}),
        "Disconnect a single device by id/serial.")
    tools["reconnect"] = _B(
        lambda f, a: f.reconnect(device=_sessions_arg(a)),
        _d(), "Recover/reconnect device(s).")

    # -- screen ------------------------------------------------------------
    tools["take_screenshot"] = _B(
        lambda f, a: f.screenshot(device=_sessions_arg(a)),
        _d(), "Capture a screenshot of device(s).")
    tools["screen_record"] = _B(
        lambda f, a: f.screenrecord(seconds=float(a.get("seconds", 8)),
                                    device=_sessions_arg(a)),
        _d(**{"seconds": {"type": "number", "default": 8}}),
        "Record the screen of device(s) and pull the mp4.")
    tools["screen_info"] = _B(
        lambda f, a: f.info(device=_sessions_arg(a)),
        _d(), "Display/resolution/orientation info for device(s).")

    # -- touch / mouse -----------------------------------------------------
    tools["tap"] = _B(
        lambda f, a: f.tap(int(a["x"]), int(a["y"]), device=_sessions_arg(a)),
        _pr({"x": {"type": "integer"}, "y": {"type": "integer"}}) | _d_props(),
        "Tap/click at x,y on device(s).")
    tools["long_press"] = _B(
        lambda f, a: f.long_press(int(a["x"]), int(a["y"]),
                                  duration_ms=int(a.get("duration_ms", 600)),
                                  device=_sessions_arg(a)),
        _pr({"x": {"type": "integer"}, "y": {"type": "integer"}}) | _d_props(),
        "Long-press at x,y on device(s).")
    tools["swipe"] = _B(
        lambda f, a: f.swipe(int(a["x1"]), int(a["y1"]), int(a["x2"]),
                             int(a["y2"]), int(a.get("duration_ms", 300)),
                             device=_sessions_arg(a)),
        _pr({"x1": {"type": "integer"}, "y1": {"type": "integer"},
             "x2": {"type": "integer"}, "y2": {"type": "integer"}}) | _d_props(),
        "Swipe/drag from (x1,y1) to (x2,y2) on device(s).")
    tools["scroll"] = _B(
        lambda f, a: f.scroll(direction=str(a.get("direction", "down")),
                              steps=int(a.get("steps", 4)),
                              device=_sessions_arg(a)),
        _d(**{"direction": {"type": "string", "enum": ["up", "down", "left",
                                                       "right"]},
              "steps": {"type": "integer"}}),
        "Scroll in a direction on device(s).")

    # -- keyboard ----------------------------------------------------------
    tools["type"] = _B(
        lambda f, a: f.type(a["text"], device=_sessions_arg(a)),
        _pr({"text": {"type": "string"}}) | _d_props(),
        "Type text into the currently focused field on device(s).")
    tools["key"] = _B(
        lambda f, a: f.key(a["keycode"], device=_sessions_arg(a)),
        _pr({"keycode": {"type": "string"}}) | _d_props(),
        "Send a key press (e.g. home, back, enter, volume_up) to device(s).")
    tools["back"] = _B(lambda f, a: f.back(device=_sessions_arg(a)),
                       _d(), "Press Back on device(s).")
    tools["home"] = _B(lambda f, a: f.home(device=_sessions_arg(a)),
                       _d(), "Press Home on device(s).")
    tools["recents"] = _B(lambda f, a: f.recents(device=_sessions_arg(a)),
                          _d(), "Open Recents on device(s).")

    # -- UI / semantic -----------------------------------------------------
    tools["ui_tree"] = _B(lambda f, a: f.ui_tree(device=_sessions_arg(a)),
                          _d(), "Dump the semantic UI hierarchy of device(s).")
    tools["ui_find"] = _B(lambda f, a: f.ui_find(device=_sessions_arg(a),
                                                 **{k: a[k] for k in
                                                    ("text", "text_contains",
                                                     "resource_id",
                                                     "content_desc", "cls")
                                                    if k in a}),
                          _d(**{"text": {"type": "string"},
                                "text_contains": {"type": "string"},
                                "resource_id": {"type": "string"},
                                "content_desc": {"type": "string"},
                                "cls": {"type": "string"}}),
                          "Find UI nodes matching semantic criteria.")
    tools["ui_click"] = _B(lambda f, a: f.ui_click(device=_sessions_arg(a),
                                                   **{k: a[k] for k in
                                                      ("text", "text_contains",
                                                       "resource_id",
                                                       "content_desc", "cls")
                                                      if k in a}),
                           _d(**{"text": {"type": "string"},
                                 "text_contains": {"type": "string"},
                                 "resource_id": {"type": "string"},
                                 "content_desc": {"type": "string"},
                                 "cls": {"type": "string"}}),
                           "Click the first UI node matching criteria.")
    tools["ui_type"] = _B(lambda f, a: f.ui_type(a.get("text", ""),
                                                 device=_sessions_arg(a),
                                                 **{k: a[k] for k in
                                                    ("text_contains",
                                                     "resource_id",
                                                     "content_desc", "cls")
                                                    if k in a}),
                          _d(**{"text": {"type": "string"},
                                "text_contains": {"type": "string"},
                                "resource_id": {"type": "string"}}),
                          "Type into a matched editable UI field.")
    tools["ui_read"] = _B(lambda f, a: f.ui_read(device=_sessions_arg(a)),
                          _d(), "Read all visible text of the current screen.")

    # -- apps / intents ----------------------------------------------------
    tools["apps_list"] = _B(lambda f, a: f.apps_list(device=_sessions_arg(a)),
                            _d(), "List installed packages on device(s).")
    tools["app_launch"] = _B(
        lambda f, a: f.app_launch(a["package"], device=_sessions_arg(a)),
        _pr({"package": {"type": "string"}}) | _d_props(),
        "Launch an app by package on device(s).")
    tools["app_stop"] = _B(
        lambda f, a: f.app_stop(a["package"], device=_sessions_arg(a)),
        _pr({"package": {"type": "string"}}) | _d_props(),
        "Force-stop an app by package on device(s).")
    tools["open_url"] = _B(
        lambda f, a: f.open_url(a["url"], device=_sessions_arg(a)),
        _pr({"url": {"type": "string"}}) | _d_props(),
        "Open a URL via intent on device(s).")
    tools["open_settings"] = _B(
        lambda f, a: f.open_settings(a.get("panel", ""), device=_sessions_arg(a)),
        _d(**{"panel": {"type": "string", "description": "optional settings panel"}}),
        "Open Android Settings (optionally a named panel) on device(s).")

    # -- files -------------------------------------------------------------
    tools["files_list"] = _B(
        lambda f, a: f.files_list(a.get("path", "/sdcard/"),
                                  device=_sessions_arg(a)),
        _d(**{"path": {"type": "string", "default": "/sdcard/"}}),
        "List files/folders in a directory on device(s).")
    tools["send_file"] = _B(
        lambda f, a: f.file_push(a["local_path"], a["remote_path"],
                                 device=_sessions_arg(a)),
        _pr({"local_path": {"type": "string"},
             "remote_path": {"type": "string"}}) | _d_props(),
        "Send a file Windows -> Android device(s).")
    tools["receive_file"] = _B(
        lambda f, a: f.file_pull(a["remote_path"], a["local_path"],
                                 device=_sessions_arg(a)),
        _pr({"remote_path": {"type": "string"},
             "local_path": {"type": "string"}}) | _d_props(),
        "Receive a file Android -> Windows from device(s).")

    # -- messaging ---------------------------------------------------------
    tools["send_message"] = _B(
        lambda f, a: f.send_message(a.get("message", ""),
                                    device=_sessions_arg(a),
                                    structured=a.get("structured")),
        _d(**{"message": {"type": "string"},
              "structured": {"type": "object"}}),
        "Send a text/structured message agent -> device(s).")
    tools["receive_messages"] = _B(
        lambda f, a: f.receive_messages(device=_sessions_arg(a)),
        _d(), "Receive messages device(s) -> agent since last read.")

    # -- shell / info ------------------------------------------------------
    tools["shell"] = _B(
        lambda f, a: f.shell(a["command"], device=_sessions_arg(a)),
        _pr({"command": {"type": "string"}}) | _d_props(),
        "Run a checked shell command on device(s).")
    tools["device_info"] = _B(lambda f, a: f.info(device=_sessions_arg(a)),
                              _d(), "Full machine-readable device profile.")
    tools["verify"] = _B(lambda f, a: f.verify(device=_sessions_arg(a)),
                         _d(), "Health-check device(s).")

    # -- Remote Touchpad companion (phone -> PC) ---------------------------
    tools["remote_touchpad"] = _B(
        lambda f, a: f.remote_touchpad(a.get("action", "status"),
                                       bind=a.get("bind"),
                                       secret=a.get("secret")),
        _pr({"action": {"type": "string",
                        "enum": ["status", "start", "stop", "resolve"]},
             "bind": {"type": "string"},
             "secret": {"type": "string"}}),
        "Manage the Remote-Touchpad companion (authorized phone acts as a "
        "wireless touchpad/keyboard for this PC).")

    # -- autonomy ----------------------------------------------------------
    tools["run_goal"] = _B(
        lambda f, a: _run_goal(a["goal"]),
        _pr({"goal": {"type": "string"}}),
        "Execute a natural-language goal across the fleet (see autonomous engine).")
    return tools


def _d_props():
    return {"device": {"type": "string"}}


def _run_goal(goal: str) -> ActionResult:
    from .orchestration.autonomous import Autonomous
    return Autonomous(_get_facade()).run(goal)


# ---------------------------------------------------------------------------
# Facade lifecycle (reused across calls; rebuilt on AC_OFFLINE changes)
# ---------------------------------------------------------------------------
_facade = None
_facade_offline = None


def _get_facade():
    global _facade, _facade_offline
    import os
    from .controller import AndroidControl
    from .high import AndroidFacade
    offline = os.environ.get("AC_OFFLINE", "0").lower() in {"1", "true", "yes"}
    if _facade is None or _facade_offline != offline:
        ctrl = AndroidControl(offline=offline)
        _facade = AndroidFacade(ctrl, autorun=False)
        try:
            ctrl.discover()
        except AndroidControlError:
            pass
        _facade_offline = offline
    return _facade


# ---------------------------------------------------------------------------
# MCP methods
# ---------------------------------------------------------------------------
def _resp(id, result):
    return {"jsonrpc": "2.0", "id": id, "result": result}


def _err(id, code, message):
    return {"jsonrpc": "2.0", "id": id, "error": {"code": code, "message": message}}


def handle_request(msg: dict) -> Optional[dict]:
    method = msg.get("method")
    mid = msg.get("id")
    params = msg.get("params") or {}
    if method == "initialize":
        return _resp(mid, {"protocolVersion": PROTOCOL_VERSION,
                           "capabilities": {"tools": {"listChanged": True}},
                           "serverInfo": {"name": SERVER_NAME,
                                          "version": SERVER_VERSION}})
    if method == "notifications/initialized":
        return None
    if method == "ping":
        return _resp(mid, {})
    if method == "tools/list":
        tools = build_tools()
        items = []
        for name, b in tools.items():
            items.append({"name": name, "description": b.description,
                          "inputSchema": b.schema})
        return _resp(mid, {"tools": items})
    if method == "tools/call":
        name = params.get("name")
        args = params.get("arguments") or {}
        tools = build_tools()
        if name not in tools:
            return _err(mid, -32602, f"unknown tool: {name}")
        try:
            result = tools[name].run(_get_facade(), _coerce(args))
            payload = result.to_dict() if hasattr(result, "to_dict") else result
            return _resp(mid, {"content": [{"type": "text",
                                            "text": json.dumps(payload,
                                                               indent=2)}],
                               "isError": False})
        except Exception as e:  # noqa: BLE001
            return _err(mid, -32000, f"{type(e).__name__}: {e}")
    if method == "resources/list":
        uris = [{"uri": "android://registry", "name": "device registry"},
                {"uri": "android://skills", "name": "skill catalogue"},
                {"uri": "android://capabilities", "name": "capability vocabulary"}]
        return _resp(mid, {"resources": uris})
    if method == "resources/read":
        uri = params.get("uri")
        if uri == "android://registry":
            return _resp(mid, {"contents": [{
                "uri": uri,
                "mimeType": "application/json",
                "text": json.dumps([s for s in _fleet_plain()], indent=2)}]})
        if uri == "android://skills":
            return _resp(mid, {"contents": [{
                "uri": uri, "mimeType": "text/plain",
                "text": _skill_catalogue()}]})
        return _err(mid, -32002, f"unknown resource: {uri}")
    if method == "prompts/list":
        return _resp(mid, {"prompts": [
            {"name": "control_device",
             "description": "Operate a specific Android device",
             "arguments": [{"name": "device", "required": True}]},
            {"name": "phone_touchpad",
             "description": "Use an authorized phone as a touchpad/keyboard for this PC",
             "arguments": []},
        ]})
    if method == "prompts/get":
        name = params.get("name")
        a = params.get("arguments") or {}
        if name == "control_device":
            return _resp(mid, {"description": "Operate a device",
                               "messages": [{"role": "user", "content": [{
                                   "type": "text",
                                   "text": f"Take control of Android device {a.get('device')}. "
                                           "Discover/status it, then use tools to drive it."}]}]})
        if name == "phone_touchpad":
            return _resp(mid, {"description": "Phone as PC touchpad",
                               "messages": [{"role": "user", "content": [{
                                   "type": "text",
                                   "text": "Start the Remote Touchpad companion and report the connect URL."}]}]})
        return _err(mid, -32002, f"unknown prompt: {name}")
    if mid is None:
        return None
    return _err(mid, -32601, f"method not found: {method}")


def _safe_handle(msg: dict) -> Optional[dict]:
    try:
        return handle_request(msg)
    except AndroidControlError as e:
        return _err(msg.get("id"), -32000, str(e))
    except Exception as e:  # noqa: BLE001
        return _err(msg.get("id"), -32603, f"{type(e).__name__}: {e}")


def _coerce(args: dict) -> dict:
    return args or {}


def _fleet_plain() -> List[dict]:
    try:
        f = _get_facade()
        return [s.profile() for s in f.ctrl.registry.all()]
    except Exception:
        return []


def _skill_catalogue() -> str:
    from .skills import ALL_SKILLS
    return "\n".join(sorted(ALL_SKILLS))


# ---------------------------------------------------------------------------
# stdio framing (newline-delimited JSON)
# ---------------------------------------------------------------------------
def serve_stdio():
    for raw in sys.stdin.buffer:
        line = raw.decode("utf-8", "replace").strip()
        if not line:
            continue
        try:
            msg = json.loads(line)
        except json.JSONDecodeError:
            continue
        if msg.get("method") == "notifications/initialized":
            continue
        result = _safe_handle(msg)
        if result is not None:
            sys.stdout.write(json.dumps(result) + "\n")
            sys.stdout.flush()


def main(argv=None):
    """Console entry point for the MCP server (see mcp_server.py)."""
    import argparse
    import os as _os
    p = argparse.ArgumentParser(prog="android-control-mcp")
    p.add_argument("--offline", action="store_true")
    p.add_argument("--version", action="version",
                   version="android-control-mcp 1.0.0")
    a = p.parse_args(argv)
    if a.offline:
        _os.environ["AC_OFFLINE"] = "1"
    serve_stdio()
    return 0
