"""Intent engine (§16): construct and fire Android intents as a first-class
capability (open app/url/settings/share/file, start activity, broadcast).
Prefer intents over screen clicking when reliable.
"""
from __future__ import annotations

import shlex
from typing import Optional

from ..config import Settings
from .base import EngineBase


class IntentEngine(EngineBase):
    def __init__(self, transport, settings: Settings):
        super().__init__(transport, settings)

    def _start(self, serial: str, *frag: str) -> str:
        cmd = "am start " + " ".join(frag)
        res = self._shell(serial, cmd, timeout_s=self.settings.long_timeout_s)
        if not res.ok:
            raise Exception(f"am start failed: {res.error}")
        return res.stdout

    def open_url(self, serial: str, url: str) -> None:
        """Open a URL in the default handler via ACTION_VIEW."""
        self._start(serial, "-a", "android.intent.action.VIEW",
                    "-d", _sh(url))

    def open_app(self, serial: str, package: str,
                 activity: Optional[str] = None) -> None:
        if activity:
            self._start(serial, "-n", _sh(f"{package}/{activity}"))
        else:
            self._start(serial, "-a", "android.intent.action.MAIN",
                        "-c", "android.intent.category.LAUNCHER",
                        "-p", _sh(package))

    def open_settings(self, serial: str, panel: str = "") -> None:
        """Open the main Settings or a named sub-panel where recognised."""
        maps = {
            "wifi": "android.settings.WIFI_SETTINGS",
            "bluetooth": "android.settings.BLUETOOTH_SETTINGS",
            "display": "android.settings.DISPLAY_SETTINGS",
            "sound": "android.settings.SOUND_SETTINGS",
            "apps": "android.settings.MANAGE_APPLICATIONS_SETTINGS",
            "developer": "android.settings.APPLICATION_DEVELOPMENT_SETTINGS",
            "security": "android.settings.SECURITY_SETTINGS",
            "storage": "android.settings.INTERNAL_STORAGE_SETTINGS",
            "battery": "android.settings.BATTERY_SAVER_SETTINGS",
            "date": "android.settings.DATE_SETTINGS",
        }
        action = maps.get(panel.strip().lower(), "android.settings.SETTINGS")
        self._start(serial, "-a", action)

    def share(self, serial: str, text: str, subject: str = "",
              mime: str = "text/plain") -> None:
        cmd = ["-a", "android.intent.action.SEND", "--es",
               "android.intent.extra.TEXT", _sh(text), "-t", mime]
        if subject:
            cmd += ["--es", "android.intent.extra.SUBJECT", _sh(subject)]
        cmd += ["--chooser"]
        self._start(serial, *cmd)

    def open_file(self, serial: str, uri: str, mime: str = "*/*") -> None:
        self._start(serial, "-a", "android.intent.action.VIEW",
                    "-d", _sh(uri), "-t", mime)

    def start_activity(self, serial: str, component: str,
                       extra: Optional[str] = None,
                       data_uri: Optional[str] = None) -> None:
        frag = ["-n", _sh(component)]
        if extra:
            frag += ["--es", "android.intent.extra.TEXT", _sh(extra)]
        if data_uri:
            frag += ["-d", _sh(data_uri)]
        self._start(serial, *frag)

    def broadcast(self, serial: str, action: str,
                  data_uri: Optional[str] = None,
                  extra: Optional[str] = None) -> str:
        """Send a broadcast intent. Requires appropriate permissions on device."""
        frag = ["-a", _sh(action)]
        if data_uri:
            frag += ["-d", _sh(data_uri)]
        if extra:
            frag += ["--es", "android.intent.extra.TEXT", _sh(extra)]
        res = self._shell(serial, "am broadcast " + " ".join(frag),
                          timeout_s=self.settings.long_timeout_s)
        if not res.ok:
            raise Exception(f"broadcast failed: {res.error}")
        return res.stdout


def _sh(value: str) -> str:
    """Quote a value for safe inclusion in an `am` shell argument."""
    return shlex.quote(value)
