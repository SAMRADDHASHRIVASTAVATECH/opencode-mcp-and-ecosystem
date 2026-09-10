# Configuration & modes & privacy

## Central config model

`AppConfig` (config.py) mirrors spec section 43. Load JSON via
`--config config/assistant.example.json` or set `OLCAP_*` env vars
(`config/.env.example`). Sub-models: `audio`, `screen`, `stt`, `reasoning`, `tts`,
`privacy`, `security`, plus openclaw/opencode/lmstudio integration fields.

## Modes (spec sections 2–4)

* Default `off`. `assistant.mode.interview` / `.workspace` / `.set(mode)` to switch.
* **INTERVIEW/PRACTICE**: audio + transcript + question detection + reasoning priority.
  No continuous screen capture by default.
* **ALWAYS-ON WORKSPACE**: audio + screen-change + active-app + contextual reasoning.
* Activation is explicit; the assistant never silently enables mic or screen.
* Per-sensor indicators: `SCREEN / MICROPHONE / SYSTEM AUDIO / AI` = `ACTIVE/PAUSED/OFF`.

## Screen privacy (spec 10)

`screen_monitoring`, `active_window_only`, `selected_region_only`, `capture_interval_s`,
`cloud_vision`, `record_screenshots`, plus `ignored_applications` / `allowed_applications`.
Global `assistant.emergency_stop` stops capture instantly. Never bypasses OS permissions.

## Privacy defaults (spec 25, conservative)

| Setting | Default |
|---|---|
| `store_transcripts` | true |
| `store_summaries` | true |
| `record_screenshots` | false |
| `cloud_processing` | false (master gate) |
| `retention_days` | 30 |

Raw audio is never stored; screenshots only when `record_screenshots` is true and a
reasoning/vision path needs them.

## Security (spec 26)

Local mode trusts the on-host operator. Remote mode requires `remote_access=true` + a
configured `MCP_TOKEN` (env/keystore), checked with constant-time compare on every call.
API/model keys come from env only and are redacted from any output.

## Emergency stop (spec 27)

`assistant.emergency_stop` stops screen/audio capture, cancels TTS + current generation,
stops tool execution where possible, disables autonomous processing and sets mode to `off`.
It persists across restarts until `release_emergency_stop`.

## Example JSON

See `config/assistant.example.json`. Reasoning example:

```jsonc
{ "reasoning": { "provider": "lmstudio",
                 "endpoint": "http://127.0.0.1:1234/v1",
                 "model": "qwen2.5-coder-7b-instruct",
                 "context_window": 32768,
                 "fallbacks": ["openclaw"] } }
```
