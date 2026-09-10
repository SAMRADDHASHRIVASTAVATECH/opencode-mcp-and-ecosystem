#!/usr/bin/env python3
"""Deterministic offline tour of the Universal Android Control skill.

No phone needed. Run from the repo root:
    PYTHONPATH=src python examples/quickstart_offline.py
or once installed:    python examples/quickstart_offline.py
"""
import os
os.environ["AC_OFFLINE"] = "1"

import android_control as ac


def main():
    print("== master boot ==")
    boot = ac.android_control(offline=True)
    d = boot.data
    print(f"state={d['state']} connected={d['devices_connected']}")

    print("\n== facade over the fleet ==")
    f = ac.boot_offline()
    print("devices:", [s.device_id for s in f.ctrl.registry.all()])

    print("\n== broadcast: screenshot every phone ==")
    r = f.screenshot()
    for o in r.devices:
        print(f"  {o.device_id}: {o.status}")

    print("\n== capability profile of one device ==")
    prof = f.capabilities(device="device_001").devices[0]
    caps = {k: v for k, v in prof.data["capabilities"].items()
            if k != "extra"}
    print("  device_001 model", prof.data["model"], "caps", caps)

    print("\n== app launch + verify on one device ==")
    r = f.app_launch("com.whatsapp", device="device_001")
    o = r.devices[0]
    print(f"  {o.status}  {o.verification}")

    print("\n== groups ==")
    f.groups.create("pixels", ["device_001", "device_002"])
    print("  members of 'pixels':",
          [s.device_id for s in f.groups.members("pixels")])

    print("\n== autonomous natural-language goal ==")
    g = ac.run_goal("open the camera on every connected phone", offline=True)
    for o in g.devices:
        print(f"  {o.device_id}: {o.status} {o.data}")

    print("\n== messaging (agent <-> device) ==")
    s = f.send_message("open settings", device="device_001")
    print("  agent->device:", s.devices[0].status,
          s.devices[0].data["kind"])
    f.ingest_message("settings opened", device="device_001")
    rx = f.receive_messages(device="device_001")
    print("  device->agent:", [m["payload"] for m in rx.devices[0].data])


if __name__ == "__main__":
    main()
