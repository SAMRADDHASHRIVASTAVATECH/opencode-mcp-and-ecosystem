#!/usr/bin/env python3
"""Download the official prebuilt remote-touchpad (GPLv3) Windows binary into
this project's install dir so the embedded backend can launch it.

Source of truth: the upstream GitHub release (Unrud/remote-touchpad). We do not
download from anywhere else.

Run on the Windows host:
    python scripts/download_remote_touchpad.py [--release v1.5.4] [--dest <dir>]

Then set AC_RT_BIN (or leave default install dir) and AC_RT_ENABLED=true.
"""
import argparse
import sys
from pathlib import Path


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--release", default="v1.5.4")
    p.add_argument("--dest", default="")
    a = p.parse_args()

    # reuse the backend's resolution/download logic
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
    from android_control.config import load_settings
    from android_control.backends.remote_touchpad import (
        RemoteTouchpadBackend, ASSET, DOWNLOAD_URL)

    settings = load_settings()
    if a.dest:
        settings.install_dir = a.dest
    settings.rt_release = a.release
    settings.rt_autodownload = True
    rt = RemoteTouchpadBackend(settings)
    target = rt._download()
    if not target:
        url = DOWNLOAD_URL.format(release=a.release)
        print(f"Download failed. Fetch it manually from {url} and set "
              f"AC_RT_BIN to the .exe path.", file=sys.stderr)
        return 1
    print(f"Downloaded: {target}")
    print("Set AC_RT_BIN (if not the default install dir) and AC_RT_ENABLED=true")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
