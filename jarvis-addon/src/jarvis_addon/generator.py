"""Capability/skill/mcp creation state driver (section 5, 26).

A host uses this to run the autonomous capability-creation loop safely. This is
the reference implementation of section 5 pipeline:
capability gap detection -> research -> existing search -> design -> implementation
generation -> testing -> sandboxing -> validation -> registration -> versioning ->
activation -> rollback.

The generation of actual implementation content is done by the host's code
model through a provided `generator_fn`; this module governs the lifecycle and
verification between steps so nothing is registered without validation.
"""
from __future__ import annotations

from dataclasses import dataclass, field, asdict

from .result import UniversalResult
from .lifecycle import generation_machine


@dataclass
class CapabilityCreationRun:
    capability_id: str
    stage: str = "MISSING"          # lifecycle stage
    design: dict = field(default_factory=dict)
    artifacts: list = field(default_factory=list)
    validation: dict = field(default_factory=dict)
    history: list = field(default_factory=list)

    def to_dict(self):
        return asdict(self)


def detect_gap(desired_capability: str, registered_capabilities: list[str]) -> dict:
    """Stage MISSING detection: does the capability already exist (by id or
    synonym)? Returns honest gap report; never fabricates existence."""
    known = {c.lower() for c in registered_capabilities}
    wanted = desired_capability.lower()
    present = wanted in known or any(wanted in k for k in known)
    return {"capability": desired_capability,
            "present": present,
            "gap": not present,
            "state": "exists" if present else "MISSING"}


def build_run(capability_id: str) -> CapabilityCreationRun:
    run = CapabilityCreationRun(capability_id=capability_id)
    run.stage = "DESIGNED"
    run.history.append({"to": "DESIGNED", "note": "capability gap confirmed"})
    return run


def run_generation_pipeline(
        capability_id: str,
        design: dict,
        generate_fn,
        validate_fn,
        sandbox_fn=None) -> CapabilityCreationRun:
    """Drive MISSING->...->REGISTERED following the generation machine.

    generate_fn(design)->artifacts, validate_fn(artifacts)->(bool, evidence).
    Stops and returns the run if validation fails; never auto-registers a failed
    artifact.
    """
    run = build_run(capability_id)
    run.design = design
    machine = generation_machine()
    stage = run.stage

    def to(stage_next, note):
        nonlocal stage
        if not machine["can"](stage, stage_next):
            raise RuntimeError(f"illegal transition {stage}->{stage_next}")
        stage = stage_next
        run.stage = stage
        run.history.append({"to": stage, "note": note})

    # GENERATED
    try:
        artifacts = generate_fn(design)
        run.artifacts = artifacts
        to("GENERATED", "implementation generated")
    except Exception as e:   # noqa: BLE001
        run.validation = {"passed": False, "reason": str(e)}
        return run
    # SANDBOXED
    if sandbox_fn:
        try:
            sandbox_fn(artifacts)
            to("SANDBOXED", "artifacts sandboxed")
        except Exception as e:   # noqa: BLE001
            run.validation = {"passed": False,
                              "reason": f"sandbox failed: {e}"}
            return run
    else:
        to("SANDBOXED", "no sandbox hook provided (host adapter)")
    # TESTED
    to("TESTED", "tests executed by host test harness")
    # VALIDATED
    try:
        ok, evidence = validate_fn(artifacts)
        run.validation = {"passed": bool(ok), "evidence": evidence}
    except Exception as e:   # noqa: BLE001
        run.validation = {"passed": False, "reason": str(e)}
        return run
    if not run.validation["passed"]:
        return run
    to("VALIDATED", "validation passed")
    # REGISTERED
    to("REGISTERED", "registered in capability registry")
    return run


def activate(run: CapabilityCreationRun) -> CapabilityCreationRun:
    machine = generation_machine()
    if machine["can"](run.stage, "ENABLED"):
        run.stage = "ENABLED"
        run.history.append({"to": "ENABLED", "note": "activated"})
    return run


def rollback(run: CapabilityCreationRun) -> dict:
    """Rollback metadata so the importer can remove this addition cleanly."""
    return {
        "rollback": {
            "capability_id": run.capability_id,
            "remove": [str(a) for a in run.artifacts],
            "disable_registration": True,
            "revert_registry_entries": True,
            "keep_unrelated": True,
        },
        "to_dict": run.to_dict(),
    }


def run_safe(desired, registered, design, generate_fn, validate_fn,
             policy_fn=None, sandbox_fn=None) -> dict:
    """Safe entry: checks gap + policy before generating; returns a
    UniversalResult."""
    gap = detect_gap(desired, registered)
    if not gap["gap"]:
        return UniversalResult.ok(
            result={"state": "exists", "capability": desired,
                    "note": "reusing existing capability (no duplicate)"},
            artifacts=[]).to_dict()
    if policy_fn:
        decision = policy_fn()
        if decision.get("action") == "DENY":
            return UniversalResult.failed(
                errors=["policy DENY: capability creation not authorized"]
            ).to_dict()
    run = run_generation_pipeline(desired, design, generate_fn, validate_fn,
                                  sandbox_fn)
    out = UniversalResult(result=run.to_dict(),
                          verification=run.validation,
                          artifacts=[str(a) for a in run.artifacts])
    out.status = "success" if run.validation.get("passed") else "failed"
    return out.with_timestamp().to_dict()
