# Architecture

## Design goal

One realtime assistant, not a pile of tools. `Assistant` (in `assistant.py`) is the single
coordinating object that every MCP handler wraps. Both modes share the same underlying
audio/STT/context/reasoning/TTS/session/security layers but keep distinct policies.

## Core objects

| Object | Responsibility |
|---|---|
| `Assistant` | coordinator; owns the engines; mode/session orchestration; interruption; health/diag; emergency stop |
| `ModeManager` | two modes + switching; per-sensor enablement (`screen`/`microphone`/`system_audio`) + status indicators; OFF by default; no silent activation |
| `SessionManager` + `Store` | persistent sessions (mode, provenance, transcript, summary, actions, events); restart-safe |
| `ContextEngine` | bounded rolling memory (recent transcript/screen/tools/decisions/entities) + compact `rolling_context` for prompts |
| `EventBus` | typed, priority events; interrupt supersedes stale reasoning |
| `SecurityManager` | auth (local/remote token), emergency stop, no secrets in code |
| `AudioEngine`/`MicrophoneSource` | real mic capture via `sounddevice` (Windows); bounded streaming |
| `ScreenEngine` | real capture via `mss`; change detection, duplicate suppression, app/region limits, privacy config |
| `STTEngine`/`FasterWhisperProvider` | local streaming speech-to-text |
| `ModelRouter`/`LmStudioProvider` | LM Studio (OpenAI-compatible), OpenClaw, optional cloud; primary→fallback; context-window aware |
| `TTSEngine`/`LocalTTSProvider` | Kokoro/Piper/configured TTS; interruption |
| practice.py | InterviewPracticeEngine, WorkspaceEngine, MeetingEngine |

## Data flow (end-to-end)

```
microphone/screen  ->  Audio/ScreenEngine (bounded, dedup)   [audio.* / screen.*]
  ->  STT (partial/final)                                    [faster-whisper]
  ->  transcript.final events                                [transcript.*]
  ->  ContextEngine.add_*  (rolling memory per session)
  ->  Reasoning trigger (only on meaningful events)
  ->  ModelRouter.generate( compact rolling_context, user text )   [assistant.analyze*]
  ->  action/response -> optional TTS
  ->  SessionManager.add_transcript / record_action / summarize
```

## Low-latency strategy

* Rolling, bounded context — never send whole transcript + full screen history.
* Event-driven reasoning; debounce; only invoke deeper reasoning on meaningful events.
* Response cancellation on interruption; rolling incremental summaries; duplicate-frame
  suppression; bounded queues; image downscale before any vision.
* Stronger models only when a deeper/complex event or explicit request needs them.

## Honesty

Every engine reports true availability. On a host without `sounddevice`/`mss`/
`faster-whisper`/a reachable LM Studio/`TTS`, the relevant tools return `UNAVAILABLE`
with the concrete reason — nothing is faked and reported as real.
