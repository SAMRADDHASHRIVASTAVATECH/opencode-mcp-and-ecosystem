"""Policy decision engine (sections 9-12).

Encodes the standardized policy actions (ALLOW / ALLOW_WITH_CONDITIONS /
REQUIRE_APPROVAL / DENY / ESCALATE) and the authorization ladder (OBSERVE /
RECOMMEND / SAFE_EXECUTE / AUTHORIZED_AUTONOMOUS / EXPLICIT_APPROVAL / DENIED).

Non-override rule (section 12): this engine is purely ADDITIVE. A policy file can
only impose MORE restrictive outcomes; it can never widen an existing
authorization. Concretely: the resolver returns the most restrictive applicable
policy outcome, and it never reduces an authorization requirement that a host
policy already sets.
"""
from __future__ import annotations

from dataclasses import dataclass, field


class PolicyAction:
    ALLOW = "ALLOW"
    ALLOW_WITH_CONDITIONS = "ALLOW_WITH_CONDITIONS"
    REQUIRE_APPROVAL = "REQUIRE_APPROVAL"
    DENY = "DENY"
    ESCALATE = "ESCALATE"


class AuthLevel:
    OBSERVE = "OBSERVE"
    RECOMMEND = "RECOMMEND"
    SAFE_EXECUTE = "SAFE_EXECUTE"
    AUTHORIZED_AUTONOMOUS = "AUTHORIZED_AUTONOMOUS"
    EXPLICIT_APPROVAL = "EXPLICIT_APPROVAL"
    DENIED = "DENIED"


# Ordering from least to most restrictive action (higher index = stricter)
_ACTION_ORDER = [PolicyAction.ALLOW, PolicyAction.ALLOW_WITH_CONDITIONS,
                 PolicyAction.REQUIRE_APPROVAL, PolicyAction.ESCALATE,
                 PolicyAction.DENY]

# ordering auth level least->most permissive intent
_AUTH_ORDER = [AuthLevel.DENIED, AuthLevel.EXPLICIT_APPROVAL,
               AuthLevel.AUTHORIZED_AUTONOMOUS, AuthLevel.SAFE_EXECUTE,
               AuthLevel.RECOMMEND, AuthLevel.OBSERVE]


@dataclass
class PolicyDecision:
    action: str = PolicyAction.DENY
    auth_level: str = AuthLevel.DENIED
    reasons: list = field(default_factory=list)
    conditions: list = field(default_factory=list)
    matched_policies: list = field(default_factory=list)
    host_override_stricter: bool = False     # true when host already stricter
    timestamp: str = ""

    def to_dict(self):
        import time
        return {
            "action": self.action,
            "auth_level": self.auth_level,
            "reasons": self.reasons,
            "conditions": self.conditions,
            "matched_policies": self.matched_policies,
            "host_override_stricter": self.host_override_stricter,
            "timestamp": self.timestamp or time.strftime("%Y-%m-%dT%H:%M:%SZ"),
        }


def _most_restrictive_action(actions):
    """Higher _ACTION_ORDER index == more restrictive (DENY is strictest)."""
    if not actions:
        return PolicyAction.ALLOW
    return max(actions, key=lambda a: _ACTION_ORDER.index(a)
               if a in _ACTION_ORDER else -1)


def evaluate(policy_set, *, operation: str, capability: str | None = None,
             skill_id: str | None = None, agent: str | None = None,
             required_auth: str | None = None,
             host_deny: bool = False, host_min_auth: str | None = None,
             context: dict | None = None) -> PolicyDecision:
    """Apply the most restrictive rule across all applicable policies.

    policy_set: list of policy dicts each with {scope, action, auth_level,
    when, conditions, reason}.
    Non-override: host_deny forces DENY; host_min_auth narrows allowed level.
    """
    import time
    applicable = []
    for p in policy_set or []:
        scope = p.get("scope", {})
        matches = True
        if capability and scope.get("capability") and capability not in scope["capability"]:
            matches = False
        if skill_id and scope.get("skills") and skill_id not in scope["skills"]:
            matches = False
        if agent and scope.get("agents") and agent not in scope["agents"]:
            matches = False
        if operation and scope.get("operations") and operation not in scope["operations"]:
            matches = False
        if matches:
            when = p.get("when")
            if when:
                ok = True
                for k, v in when.items():
                    if context and k in context and context[k] != v:
                        ok = False
                if not ok:
                    continue
            applicable.append(p)

    if host_deny:
        d = PolicyDecision(action=PolicyAction.DENY, auth_level=AuthLevel.DENIED,
                           reasons=["host policy denies"],
                           matched_policies=[p.get("id") for p in applicable],
                           host_override_stricter=True)
        d.timestamp = time.strftime("%Y-%m-%dT%H:%M:%SZ")
        return d

    if not applicable:
        action = PolicyAction.ALLOW
        reasons = ["no add-on policy constrains this operation"]
    else:
        action = _most_restrictive_action([p.get("action", PolicyAction.ALLOW)
                                           for p in applicable])
        reasons = [p.get("reason", p.get("id", "policy")) for p in applicable]

    # authorization level: required_auth for the skill/capability (declared)
    auth = required_auth or AuthLevel.RECOMMEND
    # host minimum auth (non-override): if the operation already demands a higher
    # bar, we keep that higher bar.
    if host_min_auth:
        # pick the more restrictive (lower in _AUTH_ORDER is more restrictive
        # per intent ordering DENIED first)... choose stricter of the two
        auth = _stricter_auth(auth, host_min_auth)
    if auth == AuthLevel.DENIED:
        action = PolicyAction.DENY

    conditions = []
    for p in applicable:
        conditions.extend(p.get("conditions", []))
    matched = [p.get("id") for p in applicable]

    d = PolicyDecision(action=action, auth_level=auth, reasons=reasons,
                       conditions=conditions, matched_policies=matched,
                       host_override_stricter=bool(host_min_auth))
    d.timestamp = time.strftime("%Y-%m-%dT%H:%M:%SZ")
    return d


def _stricter_auth(a, b):
    """Return the more restrictive auth level (denied is most restrictive)."""
    ia = _AUTH_ORDER.index(a) if a in _AUTH_ORDER else 99
    ib = _AUTH_ORDER.index(b) if b in _AUTH_ORDER else 99
    return a if ia <= ib else b
