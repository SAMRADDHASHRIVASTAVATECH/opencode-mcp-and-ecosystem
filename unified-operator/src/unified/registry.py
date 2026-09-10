"""Runtime registry: owns connectors + permission/account/audit/state and
dispatches tool/action calls across platforms. This is the single dispatcher the
MCP server and the workflow/call engines both use."""
from __future__ import annotations

import json

from .accounts import AccountRegistry
from .config import Settings
from .observability import Audit, OperatorLog
from .permissions import PermissionManager
from .state import StateStore
from .errors import AmbiguousTarget, PermissionDenied


class Runtime:
    def __init__(self, settings: Settings | None = None, offline: bool = False):
        self.settings = settings or Settings()
        if offline:
            self.settings.offline = True
        from pathlib import Path
        Path(self.settings.state_dir).mkdir(parents=True, exist_ok=True)
        Path(self.settings.log_dir).mkdir(parents=True, exist_ok=True)
        self.log = OperatorLog()
        self.store = StateStore(self.settings)
        self.audit = Audit(self.store.conn)
        self.accounts = AccountRegistry(self.settings)
        self.perms = PermissionManager(self.settings)
        self.connectors = {}
        self._init_connectors()
        # engines
        from .engines.workflow import WorkflowEngine
        from .engines.calls import CallEngine
        self.workflows = WorkflowEngine(self)
        self.calls = CallEngine(self)

    def close(self):
        try:
            self.store.conn.close()
        except Exception:
            pass

    def _init_connectors(self):
        from .providers.google import GoogleConnector
        from .providers.discord_provider import DiscordConnector
        from .providers.voice import VoiceConnector
        from .providers.meet import MeetConnector
        from .providers.openclaw import OpenClawConnector
        for cls in (GoogleConnector, DiscordConnector, VoiceConnector,
                    MeetConnector, OpenClawConnector):
            try:
                c = cls(self.settings, self.log, self.audit, self.accounts)
                self.connectors[c.namespace] = c
            except Exception as e:
                self.log.error(f"failed to init {cls.__name__}: {e}")

    # ---- dispatch ---------------------------------------------------- #
    def resolve_action(self, action: str) -> tuple:
        """'google.gmail.send' -> (namespace, op)."""
        if "." in action:
            ns, op = action.split(".", 1)
        else:
            ns, op = action, action
        if ns in self.connectors and self.connectors[ns].can(op):
            return ns, op
        return None, None

    def call(self, action: str, args: dict, *, account: str = None,
             authorized: bool = False, reason: str = "",
             request_id: str = "") -> dict:
        ns, op = self.resolve_action(action)
        if ns is None:
            # engine / namespaced non-connector ops handled by caller
            raise KeyError(action)
        conn = self.connectors[ns]
        spec = conn.OPS[op]
        acct = conn.account(account)
        perm_action = spec.action or action
        self.perms.require(perm_action, account=acct, authorized=authorized,
                           reason=reason)
        self.audit.record(request_id=request_id, account=acct, platform=ns,
                          action=action, status="started")
        result = conn.invoke(op, args, account=account)
        self.audit.record(request_id=request_id, account=acct, platform=ns,
                          action=action, status="ok", detail={
                              "operation": f"{ns}.{op}", "mode": result.get("mode")})
        return result

    def capability_report(self) -> dict:
        rep = {}
        for ns, c in self.connectors.items():
            avail = c.available()
            rep[ns] = {"configured": avail["configured"], "mock": avail["mock"],
                       "note": avail["note"],
                       "operations": sorted(c.OPS.keys())}
        rep["mode"] = "mock" if self.settings.offline else "live"
        rep["voice_provider"] = self.settings.voice_provider
        return rep

    def check_ambiguity(self, candidates):
        if candidates and len(candidates) == 1:
            return candidates[0], False
        return None, True
