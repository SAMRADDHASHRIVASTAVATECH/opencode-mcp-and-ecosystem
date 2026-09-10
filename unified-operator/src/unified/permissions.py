"""Permission system.

Every action has an action id like '<platform>.<op>'. The effective policy is:
  - explicit override for this exact action / account / destination
  - confirm/block patterns configured via env
  - else the default policy.

Outcomes: automatic | confirmation_required | blocked.
"""
from __future__ import annotations

from .config import Settings
from .errors import PermissionDenied


class Policy:
    AUTO = "automatic"
    CONFIRM = "confirmation_required"
    BLOCKED = "blocked"


class PermissionManager:
    def __init__(self, settings: Settings):
        self.s = settings
        self._overrides: dict = {}  # key: action -> policy ; optional "account:<id>:action"

    def _parse(self, raw: str) -> dict:
        out = {}
        for item in raw.split(","):
            item = item.strip()
            if not item or ":" not in item:
                continue
            action, pol = item.rsplit(":", 1)
            pol = pol.strip().lower()
            if pol in (Policy.AUTO, Policy.CONFIRM, Policy.BLOCKED):
                out[action.strip()] = pol
        return out

    def _patterns(self) -> tuple[dict, dict]:
        return (self._parse(self.s.perm_confirm_patterns),
                self._parse(self.s.perm_blocked_patterns))

    def effective(self, action: str, account: str = "") -> str:
        # exact override, account-scoped
        for scope in (f"account:{account}:{action}" if account else "", action):
            if scope and scope in self._overrides:
                return self._overrides[scope]
        confirm, blocked = self._patterns()
        # longest-prefix match (support 'email.send' and 'email:*' style)
        def match(table):
            for pat, pol in table.items():
                if pat == action or pat.endswith("*") and action.startswith(pat[:-1]):
                    return pol
            return None
        b = match(blocked)
        if b:
            return Policy.BLOCKED
        c = match(confirm)
        if c:
            return Policy.CONFIRM
        return self.s.perm_default if self.s.perm_default in (
            Policy.AUTO, Policy.CONFIRM, Policy.BLOCKED) else Policy.AUTO

    def require(self, action: str, *, account: str = "", authorized: bool = False,
                reason: str = "") -> str:
        """Return outcome after applying caller-provided confirmation signal."""
        pol = self.effective(action, account)
        if pol == Policy.BLOCKED:
            raise PermissionDenied(f"{action} is blocked by policy.")
        if pol == Policy.CONFIRM and not authorized:
            raise PermissionDenied(
                f"{action} requires confirmation (authorized=true + reason).")
        return pol

    def set_override(self, action: str, policy: str, account: str = "") -> None:
        if policy not in (Policy.AUTO, Policy.CONFIRM, Policy.BLOCKED):
            raise PermissionDenied(f"invalid policy {policy}")
        key = f"account:{account}:{action}" if account else action
        self._overrides[key] = policy

    def snapshot(self) -> dict:
        return {"default": self.s.perm_default,
                "overrides": dict(self._overrides),
                "confirm_patterns": self.s.perm_confirm_patterns,
                "blocked_patterns": self.s.perm_blocked_patterns}
