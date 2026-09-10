"""jarvis_addon — runtime helper library for the JARVIS add-on package.

This is NOT a standalone JARVIS. It is a small, framework-independent reference
implementation of the package's contracts so that (a) the package can validate
its own definitions and (b) any host can import the same logic. It implements
schema validation, the policy-decision engine, capability/skill lifecycle state
machines, and the universal result/verification contracts. Host-specific STT/TTS/
GUI/OS bindings are intentionally NOT included here; they live behind the
interfaces defined under contracts/ and orchestrator/.
"""
__version__ = "1.0.0"
__package_id__ = "jarvis-addon-ops-core"
