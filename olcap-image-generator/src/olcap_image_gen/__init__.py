"""OLCAP Image Generator.

AI-controlled local image-generation infrastructure exposed through MCP.
Runs on a machine with an NVIDIA GPU (e.g. Windows RTX 2050) to fully automate:
hardware detection -> model select/install/quantize -> backend (ComfyUI
preferred) -> offloaded generation -> editing -> upscaling -> jobs -> diagnostics.

Honesty contract: real inference requires a real model + running backend on the
machine that runs it. The quarantined demo backend is only for offline plumbing
self-tests and is never routed to by production tools.
"""

__version__ = "1.0.0"
