# Audio Workstation MCP

Installable Python MCP server for a local real-time microphone → DSP/soundboard/DJ mixer → output endpoint pipeline. It independently implements PortAudio device discovery/streaming, composable DSP, 14 original voice presets, persistent profiles/state, reference-audio preprocessing, WAV sound synthesis/import, polyphonic soundboard mixing, two-deck transport state/playback, analysis, triggers, and exact approval.

## Truthful scope
This package **does not install a virtual audio driver**. On Windows, install/configure a dedicated virtual cable and select its capture endpoint as Discord's microphone. The Python stream writes processed audio to the cable's render endpoint. The current build has a pluggable AI-engine registry, but no RVC/ONNX inference runtime or model is present; reference import preprocesses audio and never pretends to train or clone a voice. DSP is real. Genuine AI conversion becomes available only after a compatible adapter, legal model, HuBERT/F0 assets, and adequate hardware are installed.

## Install (Windows)
1. Install Python 3.11/3.12 x64 and a dedicated virtual audio cable; reboot if its driver requires it.
2. `py -m venv .venv && .venv\Scripts\activate`
3. `pip install -e .`
4. Set `AUDIO_WORKSTATION_DATA` to a durable private data directory.
5. Configure OpenCode:
```json
{"mcp":{"audio-workstation":{"type":"local","command":["C:\\path\\.venv\\Scripts\\audio-workstation-mcp.exe"],"environment":{"AUDIO_WORKSTATION_DATA":"C:\\Users\\you\\AudioWorkstationData"}}}}
```
6. Call `audio_list_devices`; note physical microphone ID and the cable **render/input** endpoint ID. Call `audio_start`, inspect its exact plan, `audio_approve_change`, then `audio_execute_change`.
7. In Discord, choose the virtual cable's corresponding **capture/output** endpoint as Input Device and physical headphones as Output Device. Keep the MCP process running.

All mutations use plan → explicit approval → execute → readback verification. Read-only discovery and analysis execute directly. Raw microphone audio/content is never logged or uploaded.

## Development
`pytest -q` and `python -m compileall -q src`. See `docs/` for architecture, research, tool usage, setup, troubleshooting, performance, privacy and gaps.
