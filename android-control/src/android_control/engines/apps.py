"""Application engine (§15): deterministic package identification, launch,
stop, force-stop, inspect, activities, install/uninstall, enable/disable,
clear data — with explicit authorization for destructive ops.
"""
from __future__ import annotations

import re
from typing import List, Optional

from .. import errors
from ..config import Settings
from .base import EngineBase

DESTRUCTIVE = {"clear", "uninstall", "disable"}


class AppsEngine(EngineBase):
    def __init__(self, transport, settings: Settings, authorizer=None):
        super().__init__(transport, settings)
        self.authorizer = authorizer  # optional callable(op)->bool

    # -- listing / identification -----------------------------------------
    def list_packages(self, serial: str,
                      include_disabled: bool = False) -> List[str]:
        args = "pm list packages"
        if include_disabled:
            args += " -d"
        out = self._shell_ok(serial, args,
                             timeout_s=self.settings.long_timeout_s)
        pkgs = []
        for line in out.lines():
            m = re.search(r"package:(.+)$", line.strip())
            if m:
                pkgs.append(m.group(1))
        return pkgs

    def running_packages(self, serial: str) -> List[str]:
        out = self._shell_ok(serial, "pm list packages",
                             timeout_s=self.settings.long_timeout_s)
        # identify foreground via dumpsys activity top in info engine; here we
        # return currently running through activity stack if quick.
        top = self._shell(serial, "dumpsys activity top | grep ACTIVITY | head -1")
        m = re.search(r"ACTIVITY\s+\S+\s+(\S+)/", top.stdout)
        return [m.group(1)] if m else []

    def is_installed(self, serial: str, package: str) -> bool:
        out = self._shell_ok(serial, f"pm path {package}")
        return bool(out.stdout.strip()) and not out.stdout.strip().startswith("Error")

    # -- launch / stop -----------------------------------------------------
    def launch(self, serial: str, package: str,
               activity: Optional[str] = None) -> str:
        """Launch the default (or explicit) activity for a package."""
        if activity:
            cmd = f"am start -n {package}/{activity}"
        else:
            # resolve the launcher activity deterministically
            cmd = f"monkey -p {package} -c android.intent.category.LAUNCHER 1"
        self._shell_ok(serial, cmd, timeout_s=self.settings.long_timeout_s)
        return package

    def stop(self, serial: str, package: str, force: bool = True) -> None:
        self._shell_ok(serial, f"am force-stop {package}")

    def launch_activity(self, serial: str, component: str) -> None:
        self._shell_ok(serial, f"am start -n {component}",
                       timeout_s=self.settings.long_timeout_s)

    # -- inspect -----------------------------------------------------------
    def inspect(self, serial: str, package: str) -> dict:
        out = self._shell_ok(serial, f"dumpsys package {package}",
                             timeout_s=self.settings.long_timeout_s)
        info = {}
        for line in out.lines():
            m = re.search(r"versionName=([^\s]+)", line)
            if m:
                info.setdefault("version_name", m.group(1))
            m = re.search(r"versionCode=([0-9]+)", line)
            if m:
                info.setdefault("version_code", int(m.group(1)))
            m = re.search(r"firstInstallTime=([^\s]+)", line)
            if m:
                info.setdefault("first_install", m.group(1))
            if "Activity Resolver Table" in line:
                break
        acts = re.findall(r"(\S+/\S+)\s+filter", out.stdout)
        info["activities"] = _dedupe_preserve(acts)[:40]
        return info

    # -- install / uninstall ----------------------------------------------
    def install(self, serial: str, apk_path: str, *,
                allow_downgrade: bool = False, grant_permissions: bool = False,
                replace: bool = True) -> None:
        """Install an APK from the host to the device (deterministic target)."""
        args = ["install"]
        if replace:
            args.append("-r")
        if allow_downgrade:
            args.append("-d")
        if grant_permissions:
            args.append("-g")
        args.append(str(apk_path))
        res = self._run_ok(serial, args, timeout_s=self.settings.long_timeout_s)
        if "Success" not in res.stdout:
            raise errors.CommandFailedError(
                f"install failed on {serial}: {res.stdout[-400:]}")

    def uninstall(self, serial: str, package: str, keep_data: bool = False):
        self._require_auth("uninstall", f"package {package} from {serial}")
        args = ["uninstall"]
        if keep_data:
            args.append("-k")
        args.append(package)
        res = self._run_ok(serial, args, timeout_s=self.settings.long_timeout_s)
        if "Success" not in res.stdout:
            raise errors.CommandFailedError(
                f"uninstall failed on {serial}: {res.stdout[-300:]}")

    def clear_data(self, serial: str, package: str):
        self._require_auth("clear", f"data of {package} on {serial}")
        self._shell_ok(serial, f"pm clear {package}",
                       timeout_s=self.settings.long_timeout_s)

    def enable(self, serial: str, package: str) -> None:
        self._shell_ok(serial, f"pm enable {package}")

    def disable(self, serial: str, package: str) -> None:
        self._require_auth("disable", f"package {package} on {serial}")
        self._shell_ok(serial, f"pm disable-user --user 0 {package}")

    # -- helpers -----------------------------------------------------------
    def _require_auth(self, op: str, detail: str):
        if self.authorizer is not None:
            ok = self.authorizer(op, detail)
            if not ok:
                raise errors.RequiresAuthorizationError(
                    f"{op} requires authorization: {detail}")
        elif self.settings.require_auth_destructive:
            # policy: destructive needs explicit approval in the API layer,
            # so raise unless the caller authorized.
            raise errors.RequiresAuthorizationError(
                f"destructive operation '{op}' requires authorization: {detail}")


def _dedupe_preserve(xs):
    out = []
    for x in xs:
        if x not in out:
            out.append(x)
    return out
