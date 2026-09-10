"""Autonomous incoming-call policy engine (spec sections 5, 17) plus destination /
caller authorisation (spec 11, 16).

A policy is an explicit, inspectable rule evaluated locally. Auto-answer /
AI-answer is NEVER performed unless a matching policy explicitly authorises it.
"""
from __future__ import annotations

import re
from datetime import datetime

from .errors import DestinationNotAllowed, PolicyConflict
from .config import AppConfig

# Allowed actions for incoming-call policies.
POLICY_ACTIONS = {"notify", "ring_normal", "reject", "silence", "auto_answer",
                  "ai_answer", "route_handler", "answer_collect_message"}

# Group tokens that policies may reference.
GROUP_ALL = "all"
GROUP_ALLOWED = "allowlisted"
GROUP_BLOCKED = "denylisted"
GROUP_UNKNOWN = "unknown"


def _is_e164ish(v: str) -> bool:
    # Validate the number in its *normalised* form so human-friendly formatting
    # (e.g. "+91 98765 43210", "+33 1 42 68 53 00", "(555) 123-4567") is accepted
    # before it reaches the dialer. Digits only, 6..15 after any leading '+'.
    n = normalize_number(v)
    if not n:
        return False
    if n.startswith("+"):
        n = n[1:]
    return bool(re.fullmatch(r"[0-9]{6,15}", n))


def normalize_number(n: str) -> str:
    """Best-effort E.164-ish normalisation for matching/dialling. Strips spaces,
    dashes, parentheses and dots; a leading '+' (country code prefix) is kept so
    international dialling formats survive. The actual dial string handed to the
    telephony backend is the value the backend/device expects."""
    return re.sub(r"[\s\-().]", "", n or "")


class CallerMatcher:
    """A caller 'identity' for policy matching may be a contact name, a phone
    number, an allowlist/denylist group, or 'all'. Used for explicit matching."""

    def __init__(self, config: AppConfig):
        self.cfg = config

    def matches(self, policy_spec, contact: str, number: str) -> bool:
        callers = policy_spec or [GROUP_ALL]
        if not isinstance(callers, list):
            callers = [callers]
        num = normalize_number(number)
        allow = [normalize_number(x) for x in self.cfg.allow_callers]
        deny = [normalize_number(x) for x in self.cfg.deny_callers]
        for tok in callers:
            t = str(tok).strip()
            if t == GROUP_ALL:
                return True
            if t == GROUP_ALLOWED:
                if allow and num and num in allow:
                    return True
                continue
            if t == GROUP_BLOCKED:
                # blocked group only matches if the number is in the denylist
                if num and num in deny:
                    return True
                continue
            if t == GROUP_UNKNOWN:
                # unknown = not in allowlist and no resolved contact
                if num and num not in allow and not contact:
                    return True
                continue
            # direct number or name match
            if num and normalize_number(t) == num:
                return True
            if contact and t.lower() == str(contact).lower():
                return True
        return False


class PolicyEngine:
    def __init__(self, config: AppConfig, store):
        self.cfg = config
        self.store = store
        self._mem = {}   # in-memory cache of enabled policies by name
        self._load()

    def _load(self):
        for p in self.store.list_policies():
            if p.get("enabled", True):
                self._mem[p["name"]] = p

    # ---- CRUD -------------------------------------------------------- #
    def list(self):
        return self.store.list_policies()

    def create(self, name: str, policy: dict) -> dict:
        self._validate(name, policy)
        if self.store.get_policy(name):
            raise PolicyConflict(f"policy '{name}' already exists")
        self.store.put_policy(name, policy)
        self._load()
        return self.get(name)

    def update(self, name: str, policy: dict) -> dict:
        self._validate(name, policy)
        if not self.store.get_policy(name):
            raise KeyError(f"no such policy '{name}'")
        self.store.put_policy(name, policy)
        self._load()
        return self.get(name)

    def delete(self, name: str) -> bool:
        self._mem.pop(name, None)
        return self.store.delete_policy(name)

    def get(self, name: str) -> dict | None:
        return self.store.get_policy(name)

    def _validate(self, name, policy):
        if not name.strip():
            raise ValueError("policy requires a name")
        action = policy.get("action")
        if action not in POLICY_ACTIONS:
            raise ValueError(f"action must be one of {sorted(POLICY_ACTIONS)}")
        hours = policy.get("hours")
        if hours:
            m = re.fullmatch(r"([01]?\d|2[0-3]):[0-5]\d-([01]?\d|2[0-3]):[0-5]\d", hours)
            if not m:
                raise ValueError("hours must look like 'HH:MM-HH:MM'")

    # ---- matching ---------------------------------------------------- #
    def decide_incoming(self, number: str, contact: str = "",
                        now: datetime | None = None) -> dict:
        """Return the policy that governs this inbound call, or a default no-op
        policy that only rings/notifies. Auto-action requires a policy."""
        now = now or datetime.now()
        matcher = CallerMatcher(self.cfg)
        for p in list(self._mem.values()):
            if not _in_hours(p.get("hours"), now):
                continue
            if matcher.matches(p.get("callers"), contact, number):
                return dict(p)
        # default: ring normally + notify; never auto-answer without a policy
        return {"name": "__default__", "enabled": True, "callers": [GROUP_ALL],
                "action": "ring_normal", "notify": True}

    # ---- authorisation of outbound / call actions -------------------- #
    def authorize_destination(self, number: str) -> None:
        num = normalize_number(number)
        if not _is_e164ish(num):
            raise ValueError(f"destination '{number}' is not a valid phone number")
        if self.cfg.deny_dest and num in [normalize_number(x) for x in self.cfg.deny_dest]:
            raise DestinationNotAllowed(f"destination {number} is denied", number=number)
        if self.cfg.allow_dest:
            allowed = [normalize_number(x) for x in self.cfg.allow_dest]
            if num not in allowed:
                raise DestinationNotAllowed(
                    f"destination {number} is not in the allowlist", number=number)


def _in_hours(spec, now: datetime) -> bool:
    if not spec:
        return True
    try:
        start_s, end_s = spec.split("-")
        start = datetime.strptime(start_s.strip(), "%H:%M").time()
        end = datetime.strptime(end_s.strip(), "%H:%M").time()
        t = now.time()
        if start <= end:
            return start <= t <= end
        return t >= start or t <= end   # overnight window
    except Exception:
        return True
