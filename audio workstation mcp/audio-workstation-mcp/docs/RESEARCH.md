# Research report — 2026-09-10

## Sources and findings
Current official Voicemod pages describe real-time voice changing, 200+ curated voices, community voices, VoiceLab chains with 100+ effects, pitch/bass/treble/custom controls, noise reduction/enhancement, customizable soundboards, local MP3/WAV import, playback modes/loops, folders, voice-or-sound slots, global keybinds, mobile/Stream Deck control, and virtual-microphone integration. Official Discord guidance requires Voicemod to remain open, selecting its virtual microphone as Discord input and physical headphones as output; Standard audio subsystem is recommended, with Legacy as a troubleshooting alternative. This research treats marketing latency claims as claims, not measurements.

Python `sounddevice` exposes PortAudio full-duplex callback streams, device/host API queries, capability checks, actual stream latency and CPU load. Its documentation warns callbacks must meet deadlines and avoid blocking, allocation, filesystem and unpredictable calls. PortAudio WASAPI supports shared/exclusive modes; exclusive/event-driven can lower latency but can conflict with ordinary shared application use. Microsoft documents WASAPI loopback as capture from a render endpoint and notes protected content restrictions.

For genuine local AI voice conversion, RVC is a distinct model-based process, not pitch/EQ. Current RVC documentation targets Python 3.12 and requires HuBERT/F0/model assets; CUDA, DirectML or CPU dependency sets vary. w-okada VCClient supports real-time Beatrice/RVC depending on edition and local/network split. OpenVoiceChanger documents ONNX/RVC, chunk backpressure and latency profiles. None was installed here, so this server does not claim AI inference.

## Feature parity matrix
| Capability | Current Voicemod evidence | Independent implementation | Backend | Status |
|---|---|---|---|---|
| Full-duplex real-time stream | Yes | callback stream | PortAudio/sounddevice | Implemented; hardware not validated here |
| Virtual microphone | bundled virtual device | user-installed cable endpoint | Windows driver + PortAudio | Integration implemented; driver absent here |
| Device discovery | Yes | actual host/device enumeration | PortAudio | Implemented |
| DSP voice chains | VoiceLab | serial stateful effects | NumPy/SciPy | Implemented subset |
| 12+ voices | 200+ advertised | 14 original data presets | DSP | Implemented |
| AI voices | advertised | adapter capability registry | RVC/ONNX external | Unavailable locally/not integrated |
| Reference-to-model | not verified as general user training | validation/preprocessing/profile reference | soundfile | Preprocessing only; no false cloning claim |
| Sound import | MP3/WAV documented | formats libsndfile can decode | soundfile | Implemented, format-dependent |
| Soundboard into mic | Yes | callback mix with ducking | local mixer | Implemented |
| Synthesis | content/community oriented | oscillator/noise/envelope/layers/effects | NumPy/SciPy | Implemented |
| Hotkeys | global keybinds | persistent trigger mapping controlled via MCP | host listener not included | Mapping implemented; OS hook gap |
| DJ decks | not core parity target | load/play/pause/stop/seek/speed/crossfade | soundboard mixer | Implemented basic two-deck playback |
| Mobile/Stream Deck | Yes | MCP clients can invoke tools | MCP | External client required |
| Monitoring/analysis | UI meters | peak/RMS/clipping/FFT/latency/CPU | NumPy/PortAudio | Implemented |

## Compatibility
Discord, games, OBS, browsers and calling apps can consume processed output only if they can select the configured virtual cable capture endpoint. This is an endpoint-level architecture, not application-specific injection. No complete Windows/Discord signal-path test was possible in the Linux sandbox.
