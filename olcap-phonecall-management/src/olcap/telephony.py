"""TelephonyBackend abstraction (spec section 9).

The call-management layer interacts only with this interface and never cares
which backend is actually driving the call. A backend declares the capabilities
it can actually perform; unsupported operations raise CapabilityUnsupported (or a
more specific structured error) so nothing is silently faked.
"""
from __future__ import annotations

import abc

from .errors import CallNotActive, CapabilityUnsupported
from .model import DeviceCapabilities


class TelephonyBackend(abc.ABC):
    name = "abstract"

    # ---- lifecycle / control ----------------------------------------- #
    @abc.abstractmethod
    def capabilities(self) -> DeviceCapabilities:
        ...

    @abc.abstractmethod
    def dial(self, destination: str, sim: str = "", call_id: str = "") -> dict:
        """Initiate an outbound call. call_id (optional) is the manager's id to
        key backend state under, so both sides share one authoritative id."""

    def answer(self, call_id: str) -> dict:
        raise CapabilityUnsupported(f"{self.name}.answer",
                                    capability="answer", backend=self.name)

    def reject(self, call_id: str) -> dict:
        raise CapabilityUnsupported(f"{self.name}.reject",
                                    capability="reject", backend=self.name)

    def hangup(self, call_id: str) -> dict:
        raise CapabilityUnsupported(f"{self.name}.hangup",
                                    capability="hangup", backend=self.name)

    def hold(self, call_id: str) -> dict:
        raise CapabilityUnsupported(f"{self.name}.hold",
                                    capability="hold", backend=self.name)

    def resume(self, call_id: str) -> dict:
        raise CapabilityUnsupported(f"{self.name}.resume",
                                    capability="resume", backend=self.name)

    def mute(self, call_id: str) -> dict:
        raise CapabilityUnsupported(f"{self.name}.mute",
                                    capability="mute", backend=self.name)

    def unmute(self, call_id: str) -> dict:
        raise CapabilityUnsupported(f"{self.name}.unmute",
                                    capability="unmute", backend=self.name)

    def transfer(self, call_id: str, destination: str) -> dict:
        raise CapabilityUnsupported(f"{self.name}.transfer",
                                    capability="transfer", backend=self.name)

    def send_dtmf(self, call_id: str, digits: str) -> dict:
        raise CapabilityUnsupported(f"{self.name}.send_dtmf",
                                    capability="send_dtmf", backend=self.name)

    def get_state(self, call_id: str) -> dict:
        raise CallNotActive(f"no active call for '{call_id}' on {self.name}")

    def start_audio(self, call_id: str) -> dict:
        raise CapabilityUnsupported(f"{self.name}.start_audio",
                                    capability="start_audio", backend=self.name)

    def stop_audio(self, call_id: str) -> dict:
        raise CapabilityUnsupported(f"{self.name}.stop_audio",
                                    capability="stop_audio", backend=self.name)

    # ---- device introspection ---------------------------------------- #
    def device_status(self) -> dict:
        return {"source": self.name, "online": False}

    def network_status(self) -> dict:
        return {"source": self.name, "online": False}

    def sim_slots(self) -> list:
        return []

    # ---- inbound registration ---------------------------------------- #
    def attach_call(self, number: str, direction: str, sim: str, call_id: str) -> dict:
        """Register a call the manager already created (e.g. a detected inbound
        call) so the backend can track/control it. Default no-op for backends
        whose state comes from device events."""
        return {"ref": call_id}

    # ---- events ------------------------------------------------------ #
    def subscribe(self) -> None:
        """Optional hook for backends that push realtime state. Default no-op."""

    def shutdown(self) -> None:
        ...
