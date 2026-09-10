"""Connector framework.

A Connector represents one platform (google, discord, voice, meet, openclaw).
Each declares operations via OPS. The MCP server auto-registers one typed tool
per operation, named ``<namespace>.<op>``, and routes calls to the connector.

Every connector can run in two modes:
  * real  - talks to the actual service using configured credentials.
  * mock  - deterministic offline simulation, clearly flagged, used when
            UNIFIED_OFFLINE=1 or when credentials are absent (so engines/tests
            run without a live account). Real mode is authoritative.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, List, Optional

from .errors import NotConfigured, NotSupported


@dataclass
class Param:
    name: str
    type: str = "str"          # str|int|float|bool|json|list
    required: bool = False
    desc: str = ""
    default: Any = None


@dataclass
class Op:
    name: str
    desc: str
    params: List[Param] = field(default_factory=list)
    action: str = ""           # permission id, defaults to platform.op
    mutating: bool = False
    destructive: bool = False


PY = {"str": str, "int": int, "float": float, "bool": bool,
      "json": Any, "list": list}


class Connector:
    platform: str = "base"
    namespace: str = "base"
    display_name: str = "Base"
    OPS: dict = {}
    # Pure-introspection operations that return meaningful output even in mock
    # mode (capability/status reports that need no live service).
    ALWAYS_REAL: set = set()

    def __init__(self, settings, log, audit, accounts):
        self.settings = settings
        self.log = log
        self.audit = audit
        self.accounts = accounts
        self._mock = settings.offline or not self.configured()

    # ---- state ------------------------------------------------------- #
    def configured(self) -> bool:
        """True when real-mode credentials/config are present."""
        return False

    def available(self) -> dict:
        return {"configured": self.configured(), "mock": self._mock,
                "note": ("simulated output (offline)" if self._mock
                         else "live service")}

    def account(self, account: str | None) -> str:
        return self.accounts.resolve(self.platform, account)

    # ---- operation resolution ----------------------------------------- #
    def can(self, op: str) -> bool:
        return op in self.OPS

    def _handler(self, op: str):
        h = getattr(self, f"op_{op}", None)
        if h is None:
            raise NotSupported(f"{self.namespace}.{op} is not implemented on "
                               f"{self.display_name}")
        return h

    def invoke(self, op: str, args: dict, *, account=None):
        if not self.can(op):
            raise NotSupported(f"unknown operation {self.namespace}.{op}")
        acct = self.account(account)
        mode = "mock" if self._mock else "live"
        if self._mock:
            h = getattr(self, f"op_{op}", None)
            if op in self.ALWAYS_REAL and h is not None:
                try:
                    res = h(args, account=acct)
                    return {"ok": True, "platform": self.platform, "account": acct,
                            "operation": f"{self.namespace}.{op}", "mode": "report",
                            "result": res}
                except Exception:
                    pass
            return {"ok": True, "platform": self.platform, "account": acct,
                    "operation": f"{self.namespace}.{op}", "mode": "mock",
                    "result": self.simulate(op, args, account=acct)}
        h = self._handler(op)
        return {"ok": True, "platform": self.platform, "account": acct,
                "operation": f"{self.namespace}.{op}", "mode": mode,
                "result": h(args, account=acct)}

    # ---- mock support ------------------------------------------------ #
    def simulate(self, op: str, args: dict, account: str) -> Any:
        """Deterministic offline simulation. Override per connector when richer
        output is wanted; default returns a clearly-flagged stub."""
        return {"simulated": True, "operation": f"{self.namespace}.{op}",
                "account": account,
                "note": "offline simulation - no live service was contacted."}


def coerce(params: List[Param], raw: dict) -> dict:
    out = {}
    for p in params:
        if p.name in raw and raw[p.name] is not None:
            v = raw[p.name]
            t = PY.get(p.type, str)
            if p.type == "json":
                if isinstance(v, str):
                    import json
                    v = json.loads(v)
                out[p.name] = v
            else:
                out[p.name] = v if isinstance(v, t) else t(v)
        elif p.required:
            raise ValueError(f"missing required parameter '{p.name}'")
        elif p.default is not None:
            out[p.name] = p.default
    return out
