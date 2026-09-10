#!/usr/bin/env python3
"""Quick offline selfcheck that the skill is importable and coherent.

Runs deterministically against the mock transport. Exits non-zero on failure.
Run from repo root:   PYTHONPATH=src python examples/selfcheck.py
"""
import os
os.environ["AC_OFFLINE"] = "1"
import sys

import android_control as ac
from android_control.skills import ALL_SKILLS


def main():
    checks = []
    def ok(name, cond):
        checks.append((name, bool(cond)))
        print(("PASS " if cond else "FAIL ") + name)

    boot = ac.android_control(offline=True)
    ok("master READY with 4 devices",
       boot.data["state"] == "READY" and boot.data["devices_total"] == 4)

    f = ac.boot_offline()
    ok("fleet has sessions", len(f.ctrl.registry.all()) >= 4)
    ok("registry unlimited (count)", f.ctrl.registry.count() >= 4)

    prof = f.capabilities(device="device_001").devices[0]
    ok("capability profile built",
       prof.data["capabilities"].get("shell") == "READY")

    sc = f.screenshot()
    ok("broadcast screenshot all SUCCESS",
       sc.status == "SUCCESS" and len(sc.devices) >= 4)

    ui = f.ui_tree(device="device_001")
    ok("ui tree read", ui.status == "SUCCESS" and len(ui.devices[0].data) >= 1)

    la = f.app_launch("com.whatsapp", device="device_001")
    ok("app launch single device",
       la.devices[0].status == "SUCCESS")

    g = ac.run_goal("open the camera on every connected phone", offline=True)
    ok("autonomous camera goal", g.status == "SUCCESS" and len(g.devices) >= 4)

    # §5 messaging
    snd = f.send_message("hello device", device="device_001")
    ok("agent->device message sent",
       snd.devices[0].status == "SUCCESS" and
       snd.devices[0].data["kind"] == "text")
    snd2 = f.send_message("", device="device_002",
                          structured={"event": "ui.open", "target": "settings"})
    ok("structured message broadcast",
       snd2.devices[0].data["kind"] == "json")
    f.ingest_message("done", device="device_001")
    rx = f.receive_messages(device="device_001")
    ok("device->agent message received",
       any(m["payload"] == "done" for m in rx.devices[0].data))

    ok("16 individual skills present", len(ALL_SKILLS) == 16)

    # --- MCP server surface (offline) ------------------------------------
    from android_control import mcp as mcpmod
    init = mcpmod.handle_request({
        "jsonrpc": "2.0", "id": 1, "method": "initialize",
        "params": {"protocolVersion": "2024-11-05", "capabilities": {},
                   "clientInfo": {"name": "sc"}}})
    ok("mcp initialize",
       init["result"]["serverInfo"]["name"] == "android-control")
    tl = mcpmod.handle_request({"jsonrpc": "2.0", "id": 2,
                                "method": "tools/list"})
    tnames = [t["name"] for t in tl["result"]["tools"]]
    ok("mcp exposes core tools",
       {"list_devices", "tap", "type", "send_message", "receive_file",
        "remote_touchpad", "take_screenshot"}.issubset(tnames))
    call = mcpmod.handle_request({
        "jsonrpc": "2.0", "id": 3, "method": "tools/call",
        "params": {"name": "list_devices", "arguments": {}}})
    txt = call["result"]["content"][0]["text"]
    ok("mcp tools/call works", call["result"]["isError"] is False and
       "device_001" in txt)
    call2 = mcpmod.handle_request({
        "jsonrpc": "2.0", "id": 4, "method": "tools/call",
        "params": {"name": "send_message",
                   "arguments": {"message": "mcp", "device": "device_001"}}})
    ok("mcp messaging tool",
       "SUCCESS" in call2["result"]["content"][0]["text"])
    ok("remote-touchpad skill exposed",
       "android_remote_touchpad" in ALL_SKILLS)

    # Remote Touchpad companion backend: resolve/start/stop with a stub binary
    from pathlib import Path
    stub = Path("/tmp/rt_stub_selfcheck.sh")
    stub.write_text(
        "#!/bin/bash\nsecret=''\nwhile [ $# -gt 0 ]; do case \"$1\" in "
        "--bind) bind=\"$2\"; shift 2;; --secret) secret=\"$2\"; shift 2;; "
        "*) shift;; esac; done\n"
        "echo \"Using secret: $secret\"\n"
        "echo \"http://127.0.0.1:1/#stub\"\nsleep 60\n")
    stub.chmod(0o755)
    from android_control.config import Settings
    from android_control.backends.remote_touchpad import RemoteTouchpadBackend
    rs = Settings(); rs.rt_bin = str(stub); rs.rt_bind = ":1"
    rt = RemoteTouchpadBackend(rs)
    ri = rt.start(secret="s", wait_s=2.0)
    ok("remote-touchpad backend parses URL",
       ri["url"] == "http://127.0.0.1:1/#stub")
    rt.stop()

    failed = [n for n, c in checks if not c]
    print(f"\n{len(checks) - len(failed)}/{len(checks)} checks passed")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
