# Architecture
MCP semantic tools → exact approval manager → Workstation service → persistent state and modular engines.

`PortAudioBackend` owns actual device queries and a full-duplex stream. `RealtimeEngine` callback runs stateful NumPy/SciPy DSP, live microphone levels, limiter output and soundboard/deck mixing. File decode, synthesis, reference preprocessing, persistence, and MCP work happen outside the callback. Effect chains are rebuilt off-callback and atomically replaced. State is atomically persisted with revision numbers.

Interfaces separate audio backend, DSP chain, voice profiles/engine capability, synthesis and library. The current process has one duplex route. A production deployment should run under a watchdog; endpoint hotplug is detectable through rediscovery, but automatic restart policy is intentionally operator-approved to avoid silently reopening a microphone.
