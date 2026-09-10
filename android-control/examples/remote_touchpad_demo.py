#!/usr/bin/env python3
"""Remote Touchpad companion — one interface for both directions.

Demonstrates the embedded remote-touchpad backend (phone-as-PC-input) alongside
the ADB engine. Uses a stub binary by default so it runs without the real
Windows exe; pass a real AC_RT_BIN to actually start the upstream host.

Run from repo root:   PYTHONPATH=src python examples/remote_touchpad_demo.py
"""
import os
from pathlib import Path
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from android_control.config import Settings
from android_control.backends.remote_touchpad import RemoteTouchpadBackend


def main():
    # If the real remote-touchpad binary is set, use it; else a stub.
    real = os.environ.get("AC_RT_BIN")
    if not real:
        stub = Path("/tmp/rt_demo_stub.sh")
        stub.write_text(
            "#!/bin/bash\nsecret=''\nwhile [ $# -gt 0 ]; do case \"$1\" in "
            "--bind) bind=\"$2\"; shift 2;; --secret) secret=\"$2\"; shift 2;; "
            "*) shift;; esac; done\n"
            "echo \"Using secret: $secret\"\n"
            "echo \"http://192.168.1.50:8000/#demo\"\nsleep 30\n")
        stub.chmod(0o755)
        real = str(stub)
        print("Using STUB remote-touchpad (real binary not set / not run here).")

    s = Settings(); s.rt_bin = real; s.rt_bind = ":8000"; s.rt_enabled = True
    rt = RemoteTouchpadBackend(s)

    print("binary:", rt.resolve_binary())
    info = rt.start(secret="demo")
    print("started:", info["status"])
    print("give this to the phone (or scan as QR):", info["url"])
    print("status:", rt.status())
    rt.stop()
    print("stopped.")


if __name__ == "__main__":
    main()
