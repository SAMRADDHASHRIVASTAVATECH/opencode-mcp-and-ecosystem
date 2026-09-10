"""Lifecycle state machines.

Implements section 24 (capability lifecycle), section 25 (self-maintenance
lifecycle) and section 26 (capability-generation lifecycle) as explicit, valid
state machines. Hosts reuse these to guarantee transitions are legal.
"""
from __future__ import annotations

# Capability lifecycle (section 24)
CAPABILITY_LIFECYCLE = [
    "DISCOVERED", "DESIGNED", "EXPERIMENTAL", "TESTING", "VALIDATED",
    "ENABLED", "DEGRADED", "DISABLED", "DEPRECATED",
]

_CAPABILITY_TRANSITIONS = {
    "DISCOVERED": ["DESIGNED", "DEPRECATED"],
    "DESIGNED": ["EXPERIMENTAL", "VALIDATED", "DISABLED"],
    "EXPERIMENTAL": ["TESTING", "DISABLED", "DEPRECATED"],
    "TESTING": ["VALIDATED", "EXPERIMENTAL", "DISABLED"],
    "VALIDATED": ["ENABLED", "DEGRADED", "DISABLED", "DEPRECATED"],
    "ENABLED": ["DEGRADED", "DISABLED", "DEPRECATED"],
    "DEGRADED": ["VALIDATED", "DISABLED", "DEPRECATED"],
    "DISABLED": ["ENABLED", "DEPRECATED"],
    "DEPRECATED": ["DISABLED"],
}

# Self-maintenance lifecycle (section 25)
MAINTENANCE_LIFECYCLE = [
    "HEALTHY", "DEGRADED", "DIAGNOSTIC", "REPAIRING", "TESTING", "VERIFIED",
]

_MAINTENANCE_TRANSITIONS = {
    "HEALTHY": ["DEGRADED", "DIAGNOSTIC"],
    "DEGRADED": ["DIAGNOSTIC", "REPAIRING"],
    "DIAGNOSTIC": ["REPAIRING", "HEALTHY", "DEGRADED"],
    "REPAIRING": ["TESTING", "HEALTHY"],
    "TESTING": ["VERIFIED", "DIAGNOSTIC"],
    "VERIFIED": ["HEALTHY", "DEGRADED"],
}

# Capability-generation lifecycle (section 26)
GENERATION_LIFECYCLE = [
    "MISSING", "DESIGNED", "GENERATED", "SANDBOXED", "TESTED", "VALIDATED",
    "REGISTERED", "ENABLED",
]

_GENERATION_TRANSITIONS = {
    "MISSING": ["DESIGNED"],
    "DESIGNED": ["GENERATED"],
    "GENERATED": ["SANDBOXED", "DESIGNED"],
    "SANDBOXED": ["TESTED", "GENERATED"],
    "TESTED": ["VALIDATED", "SANDBOXED"],
    "VALIDATED": ["REGISTERED", "GENERATED"],
    "REGISTERED": ["ENABLED", "VALIDATED"],
    "ENABLED": ["REGISTERED"],
}


def _machine(name, states, transitions):
    def can_transition(frm, to):
        return to in transitions.get(frm, [])

    def legal_transitions(frm):
        return list(transitions.get(frm, []))

    return {
        "name": name,
        "states": list(states),
        "can": can_transition,
        "next": legal_transitions,
    }


def capability_machine():
    return _machine("capability", CAPABILITY_LIFECYCLE, _CAPABILITY_TRANSITIONS)


def maintenance_machine():
    return _machine("maintenance", MAINTENANCE_LIFECYCLE, _MAINTENANCE_TRANSITIONS)


def generation_machine():
    return _machine("generation", GENERATION_LIFECYCLE, _GENERATION_TRANSITIONS)
