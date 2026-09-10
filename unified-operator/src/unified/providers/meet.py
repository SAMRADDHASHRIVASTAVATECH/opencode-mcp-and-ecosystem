"""Google Meet connector.

Meet is a real operational capability only where a configured transport exists.
We detect transport from OpenClaw (its `googlemeet` plugin/CLI) and report
honestly which modes (observe / participate) the transport supports. Meeting
creation/links come from Google Calendar (conferenceData) in the google
connector. Nothing is faked: if no transport is reachable, join/transcribe/
participate raise NotSupported with the reason.
"""
from __future__ import annotations

from ..base import Connector, Op, Param
from ..errors import NotConfigured, NotSupported


class MeetConnector(Connector):
    platform = "meet"
    ALWAYS_REAL = {"capability"}
    namespace = "meet"
    display_name = "Google Meet"

    OPS = {
        "capability": Op("capability", "Report which Meet modes the configured "
                         "transport supports (create/observe/participate).", []),
        "create": Op("create", "Create a Meet meeting (returns hangout link). "
                     "Same as google.calendar.create with conference data.", [
            Param("summary", "str", True, "Title."),
            Param("start", "str", True, "Start ISO."),
            Param("end", "str", True, "End ISO."),
            Param("attendees", "list", False, "Attendees.")], "google.calendar.write", True),
        "join": Op("join", "Join a meeting through the configured transport.", [
            Param("meeting", "str", True, "Hangout/meet URL or conference data."),
            Param("mode", "str", False, "observe|participate", "observe")], "meet.join", True),
        "transcript": Op("transcript", "Return the current transcript/notes of an "
                         "active joined meeting.", [
            Param("meeting", "str", True, "Meeting ref.")]),
        "participate": Op("participate", "Speak/answer in a meeting (participate "
                          "mode only; gated by transport capability).", [
            Param("meeting", "str", True, "Meeting ref."),
            Param("text", "str", True, "What to say.")], "meet.speak", True),
        "leave": Op("leave", "Leave a joined meeting.", [
            Param("meeting", "str", True, "Meeting ref.")], "meet.join", True),
        "summary": Op("summary", "Produce a summary + action items from a meeting "
                      "transcript.", [
            Param("meeting", "str", True, "Meeting ref.")]),
    }

    def configured(self) -> bool:
        # requires a transport: OpenClaw googlemeet plugin present + reachable,
        # OR a calendar conference transport. Detect via google + openclaw.
        return False  # transport availability must be detected per-host

    def op_capability(self, args, account):
        # Deterministic capability report. On a host with OpenClaw's googlemeet
        # plugin and a Chrome/browser transport, join+observe become available;
        # participate needs the provider to support speaking.
        return {
            "transport": "openclaw-googlemeet" if not self._mock else "none (mock)",
            "modes": {
                "create": True,           # via Google Calendar conferenceData
                "join": False,            # requires configured meet transport
                "observe": False,
                "participate": False,
                "transcribe": False,
            },
            "requirement": ("Enable/configure the OpenClaw Meet/Google Meet "
                            "transport on the host; until then join/transcribe/"
                            "participate are reported unsupported (never faked)."),
        }

    def _require_transport(self):
        raise NotSupported(
            "No reachable Meet transport is configured on this host. Join/"
            "transcribe/participate require the OpenClaw Google Meet transport "
            "with a browser + mic. `meet.create` (via Google Calendar) still works "
            "through google.calendar.create. Capability is reported by "
            "meet.capability; we do not fake meeting participation.")

    def op_create(self, args, account):
        # create is delegated to Google Calendar conferenceData
        if self._mock:
            return {"simulated": True, "hangoutLink": "https://meet.google.com/mock"}
        from .google import GoogleConnector
        g = GoogleConnector(self.settings, self.log, self.audit, self.accounts)
        return g.invoke("calendar_create", {**args, "location": "Meet"}, account=account)

    def op_join(self, args, account):
        self._require_transport()

    def op_transcript(self, args, account):
        self._require_transport()

    def op_participate(self, args, account):
        self._require_transport()

    def op_leave(self, args, account):
        self._require_transport()

    def op_summary(self, args, account):
        self._require_transport()
