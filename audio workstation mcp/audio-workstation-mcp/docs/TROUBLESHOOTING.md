# Troubleshooting
- `PortAudio unavailable`: install the platform PortAudio runtime; Windows sounddevice wheels normally include needed binaries, while Linux may need `libportaudio2`.
- No devices: run in the interactive desktop user session, check Windows microphone privacy permission, driver installation and disabled endpoints.
- Stream open failure: verify direction, channel count and matching 44.1/48 kHz settings; close exclusive users.
- Discord silence: MCP must be running; confirm Python writes to cable render endpoint and Discord reads paired capture endpoint; speak and inspect MCP levels first.
- Crackles: increase latency/buffer, reduce effects, avoid CPU saturation and inspect underruns.
- Feedback/echo: remove route loops and duplicate “listen to this device”/monitoring paths.
- AI engine unavailable: install a separately reviewed compatible runtime/assets/model and adapter; a reference WAV alone is not a model.
