# STT (Faster-Whisper) & TTS setup

## Local speech-to-text — Faster-Whisper (spec 6, 23)

1. `pip install faster-whisper` (or `pip install -e ".[stt]"`).
2. Configure:

```bash
OLCAP_STT_PROVIDER=faster_whisper
OLCAP_STT_MODEL=small        # tiny/base/small/medium/large-v3
OLCAP_STT_DEVICE=auto        # auto|cpu|cuda
OLCAP_STT_LANGUAGE=          # empty = auto-detect
```

3. `assistant.health().stt.faster_whisper.available` confirms the model loads.

Pipeline (spec 6): Audio → VAD → Faster-Whisper → partial → final → conversation state.
Each audio chunk is processed once — no duplicated processing. Language is configurable /
auto-detected; timestamps and (where the model provides) speaker/channel metadata are
carried in transcripts.

> On hosts without `faster-whisper`, `transcript`/STT tools return `STT_UNAVAILABLE` —
> they are never faked.

## Voice output — TTS (spec 14, 15)

Local providers (Kokoro/Piper) are supported via a configured command, or a configured
cloud TTS.

```bash
OLCAP_TTS_PROVIDER=local
OLCAP_TTS_CMD=/path/to/kokoro        # or piper on PATH
OLCAP_TTS_VOICE=                     # optional
```

`TTSEngine` supports interruption/cancellation, voice, volume and rate. Voice output is
optional and off by default (`OLCAP_TTS_PROVIDER=none`). Without a configured TTS,
`tts.speak` returns `TTS_UNAVAILABLE` honestly.

## Natural conversation (spec 15)

Turn detection, barge-in/interruption, silence handling and short-by-default responses are
governed by the realtime engine; `assistant` exposes interruption via `interruption()`
which cancels stale generation when new speech arrives (never lets stale output overwrite
newer context).
