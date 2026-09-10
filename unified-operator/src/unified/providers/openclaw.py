"""OpenClaw connector.

OpenClaw is the execution substrate + authenticated session owner in this
architecture. This connector drives the real ``openclaw`` CLI / Gateway to run
agent turns, list/inspect channels, and send through OpenClaw-managed channels
(including its Discord, Google Chat and other messaging channels), reusing its
auth instead of duplicating credentials. High-level orchestration is available
via ``openclaw.execute``.
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
from pathlib import Path

from ..base import Connector, Op, Param
from ..errors import ApiError, NotConfigured


class _OcwCli:
    def __init__(self, settings):
        self.s = settings

    def _bin(self):
        b = self.s.openclaw_bin
        if b and Path(b).expanduser().exists():
            return str(Path(b).expanduser())
        p = shutil.which("openclaw")
        if p:
            return p
        for cand in (Path.home()/".local"/"bin"/"openclaw",
                     Path.home()/".openclaw"/"bin"/"openclaw"):
            if cand.exists():
                return str(cand)
        return None

    def run(self, args, timeout=290):
        b = self._bin()
        if not b:
            raise NotConfigured("openclaw CLI not found on this host.")
        env = dict(os.environ)
        env.setdefault("OPENCLAW_GATEWAY_TOKEN", self.s.openclaw_gateway_token or "")
        try:
            r = subprocess.run([b]+args, capture_output=True, text=True,
                               env=env, timeout=timeout)
        except subprocess.TimeoutExpired:
            raise ApiError("openclaw command timed out")
        return {"ok": r.returncode == 0, "exit_code": r.returncode,
                "stdout": r.stdout, "stderr": r.stderr}


class OpenClawConnector(Connector):
    platform = "openclaw"
    namespace = "openclaw"
    display_name = "OpenClaw (agent/gateway)"

    OPS = {
        "status": Op("status", "OpenClaw availability + version.", []),
        "agent_run": Op("agent_run", "Run a non-interactive agent turn via the "
                        "OpenClaw Gateway.", [
            Param("message", "str", True, "Task for the agent, natural language."),
            Param("agent", "str", False, "Agent id.", "main"),
            Param("timeout", "int", False, "Seconds.", 600)], "openclaw.agent"),
        "execute": Op("execute", "High-level: hand a natural-language job to "
                      "OpenClaw to orchestrate using its own tools/channels.", [
            Param("task", "str", True, "What to do."),
            Param("agent", "str", False, "Agent id.", "main")], "openclaw.agent"),
        "channels": Op("channels", "Inspect OpenClaw channels (incl. Discord, "
                       "Google Chat).", []),
        "channel_send": Op("channel_send", "Send a message through an OpenClaw "
                           "channel, reusing its auth.", [
            Param("channel", "str", True, "Channel: discord|googlechat|whatsapp|telegram|..."),
            Param("to", "str", True, "Target (channel/#channel/@user, E.164, or space)."),
            Param("text", "str", True, "Message text."),
            Param("account", "str", False, "Channel account id (e.g. acct1/acct2).", "")],
             "openclaw.send", True),
    }

    def __init__(self, settings, log, audit, accounts):
        self.cli = _OcwCli(settings)          # must exist before configured()
        super().__init__(settings, log, audit, accounts)

    def configured(self) -> bool:
        return self.cli._bin() is not None

    def _require_live(self):
        if self._mock:
            raise NotConfigured("openclaw connector is mock/offline; install "
                                "openclaw on the host.")

    def _version(self):
        r = self.cli.run(["--version"], timeout=20)
        return (r["stdout"] or r["stderr"] or "unknown").strip()

    def op_status(self, args, account):
        self._require_live()
        return {"version": self._version(),
                "gateway_url": self.settings.openclaw_gateway_url}

    def op_agent_run(self, args, account):
        self._require_live()
        cmd = ["agent", "--message", args["message"], "--agent",
               args.get("agent", "main"), "--json"]
        if args.get("timeout"):
            cmd += ["--timeout", str(args["timeout"])]
        return self.cli.run(cmd, timeout=int(args.get("timeout", 600)))

    def op_execute(self, args, account):
        self._require_live()
        cmd = ["agent", "--message", args["task"], "--agent",
               args.get("agent", "main"), "--json"]
        return self.cli.run(cmd, timeout=1800)

    def op_channels(self, args, account):
        self._require_live()
        return self.cli.run(["channels", "list", "--json"])

    def op_channel_send(self, args, account):
        self._require_live()
        cmd = ["message", "send", "--json",
               "--channel", args["channel"],
               "--target", args["to"],
               "--message", args["text"]]
        if args.get("account"):
            cmd += ["--account", args["account"]]
        return self.cli.run(cmd)
