"""Simulated telephony backend (spec section 28).

Explicitly a *test/demo* backend so the full call state machine, policy engine,
authorisation and MCP surface can be exercised without making real calls or
touching real SIM audio. It is clearly labelled `simulated` in every capability
and status result; it is NEVER presented as live cellular capability.

Backend state is keyed by the manager's authoritative call_id (single source of
truth). It models two SIM slots and deterministic inbound/outbound lifecycles so
tests and the acceptance suite are repeatable.
"""
from __future__ import annotations

import time

from ..model import DeviceCapabilities, SimInfo
from ..telephony import TelephonyBackend
from ..errors import CallNotActive, SimUnavailable, CapabilityUnsupported


class SimulatedTelephonyBackend(TelephonyBackend):
    name = "simulated"

    def __init__(self, config=None):
        self.cfg = config
        self._calls: dict = {}
        default = getattr(config, "default_sim", "system") if config else "system"
        self._sims = [
            SimInfo(slot="SIM1", carrier="TestMobile", subscription_id=1,
                    active=True, default=(default in ("SIM1", "system", ""))),
            SimInfo(slot="SIM2", carrier="TestAir", subscription_id=2, active=True,
                    default=(default == "SIM2")),
        ]
        if not any(s.default for s in self._sims):
            self._sims[0].default = True

    # ---- capabilities (honest: simulation only) ----------------------- #
    def capabilities(self) -> DeviceCapabilities:
        c = DeviceCapabilities(device_attached=False, source=f"backend:{self.name}")
        c.call_state_monitoring = True
        c.cellular_call_control = False   # no real SIM control/audio
        c.multi_sim = True
        return c

    # ---- introspection ------------------------------------------------ #
    def device_status(self) -> dict:
        return {"source": self.name, "online": True,
                "note": "simulated device - no real phone attached"}

    def network_status(self) -> dict:
        return {"source": self.name, "online": True, "simulated": True}

    def sim_slots(self) -> list:
        return [s.dict() for s in self._sims]

    # ---- inbound registration ----------------------------------------- #
    def attach_call(self, number, direction, sim, call_id) -> dict:
        self._calls[call_id] = {"state": ("INCOMING_RINGING" if direction == "incoming"
                                          else "OUTGOING_RINGING"),
                                "sim": sim or "SIM1", "destination": number,
                                "direction": direction}
        return {"ref": call_id}

    # ---- call control (deterministic simulation) ---------------------- #
    def dial(self, destination: str, sim: str = "", call_id: str = "") -> dict:
        slot = sim or self._default_slot()
        if not any(s.slot == slot and s.active for s in self._sims):
            raise SimUnavailable(f"sim {slot} unavailable")
        ref = call_id or f"sim_{int(time.time()*1000)}"
        self._calls[ref] = {"state": "OUTGOING_RINGING", "sim": slot,
                            "destination": destination, "direction": "outgoing"}
        return {"ref": ref, "sim": slot, "simulated": True}

    def answer(self, call_id: str) -> dict:
        self._active(call_id)["state"] = "CALL_ACTIVE"
        return {"ok": True, "simulated": True}

    def reject(self, call_id: str) -> dict:
        c = self._active(call_id)
        c["state"] = "REJECTED"
        return {"ok": True, "simulated": True}

    def hangup(self, call_id: str) -> dict:
        self._active(call_id)["state"] = "CALL_COMPLETED"
        return {"ok": True, "simulated": True}

    def hold(self, call_id: str) -> dict:
        self._active(call_id)["state"] = "ON_HOLD"
        return {"ok": True, "simulated": True}

    def resume(self, call_id: str) -> dict:
        self._active(call_id)["state"] = "CALL_ACTIVE"
        return {"ok": True, "simulated": True}

    def mute(self, call_id: str) -> dict:
        self._active(call_id)["muted"] = True
        return {"ok": True, "simulated": True}

    def unmute(self, call_id: str) -> dict:
        self._active(call_id)["muted"] = False
        return {"ok": True, "simulated": True}

    def transfer(self, call_id: str, destination: str) -> dict:
        self._active(call_id)["state"] = "TRANSFERRED"
        return {"ok": True, "simulated": True}

    def send_dtmf(self, call_id: str, digits: str) -> dict:
        self._active(call_id)["dtmf"] = digits
        return {"ok": True, "digits": digits, "simulated": True}

    def get_state(self, call_id: str) -> dict:
        return dict(self._active(call_id))

    def start_audio(self, call_id: str) -> dict:
        raise CapabilityUnsupported(
            "simulated backend has no real call audio path", capability="start_audio",
            backend=self.name)

    def stop_audio(self, call_id: str) -> dict:
        raise CapabilityUnsupported(
            "simulated backend has no real call audio path", capability="stop_audio",
            backend=self.name)

    def _active(self, call_id: str) -> dict:
        c = self._calls.get(call_id)
        if not c:
            raise CallNotActive(f"no simulated call '{call_id}'")
        return c

    def _default_slot(self) -> str:
        for s in self._sims:
            if s.default:
                return s.slot
        return self._sims[0].slot
