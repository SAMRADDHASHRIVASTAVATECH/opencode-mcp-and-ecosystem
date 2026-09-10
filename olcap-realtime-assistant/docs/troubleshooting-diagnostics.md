# Troubleshooting, diagnostics & observability

## Diagnostics (spec 34)

`assistant.diag` runs an end-to-end pipeline diagnostic that checks each stage honestly:
mode, microphone (device count), screen (mss presence + reason), STT, reasoning, TTS. It
reports `all_ok` only if every available stage is truly available.

`python -m olcap_realtime.main --diag` prints the report.

## Health (spec 33)

`assistant.health` returns a structured report with `audio`, `screen`, `stt`, `reasoning`,
`tts`, and `mode` sub-reports. Each shows true availability + running state.

## Observability (spec 47)

* Every event carries timestamp + sequence; important events are appended to the session
  store (session_id, event type, payload).
* Audit log records actor/action/detail via `Store.audit` (see `session_export`).
* No secrets are logged; raw audio/screenshots are not stored unless configured.

## Common issues

| Symptom | Likely cause / fix |
|---|---|
| `audio.*` returns `AUDIO_UNAVAILABLE` | `sounddevice` not installed or mic permission denied; install extra + grant privacy permission |
| `screen.*` returns `SCREEN_UNAVAILABLE` | `mss` missing, headless session, or `screen_monitoring=false`; enable config + install extra |
| `transcript`/STT unavailable | `faster-whisper` not installed or model failed to load; see health reason |
| `MODEL_UNAVAILABLE` on `assistant.analyze`/practice | LM Studio not running / wrong endpoint; run `model.get_status`, fix `LM_STUDIO_ENDPOINT` |
| Everything blocked after estop | Release it: `assistant.release_emergency_stop` |
| Context keeps overflowing | That shouldn't happen — rolling context is bounded; if you see it, confirm a very old build and reinstall `-e .` |
| MCP not appearing in OpenCode | Add the entry to the existing config; don't overwrite others |

## Restart / recovery (spec 46)

Sessions persist in SQLite (`OLCAP_STATE_DIR`). After app/computer/model/MCP/network/mic/
display restarts the assistant reconnects and sessions are recovered from the store. On
boot, re-activate the mode explicitly.
