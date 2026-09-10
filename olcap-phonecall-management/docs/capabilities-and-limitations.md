# Capabilities, honesty & known limitations

This system will never claim a capability the Android device/API does not actually
support. This file is the source of truth for what each capability *means* and what the
honest defaults are.

## The audio honesty rule (most important)

`android.permission.CALL_PHONE` lets an app **initiate a call** (with a user-visible
notification). It does **not** let the app capture or inject the call's audio.

* A **normal (non-default-dialer) Android app cannot capture or inject cellular call
  audio**.
* A **default-dialer app** on Android 10+ can request *telecom* call audio
  (`TelecomManager` / `InCallService`), which is the only ordinary route to in-call audio.
* Even then this is call audio, subject to Android/carrier policy; realtime AI over it
  additionally requires that audio to be transmittable to a voice engine.

`CapabilityProbe.probe()` therefore sets `call_audio_capture`, `call_audio_injection` and
`ai_cellular_conversation` **true only when the app is the default dialer on Android 10+
with the audio permission**. Otherwise they are `false`, and `phone.get_capabilities`
reports that honestly.

## Capability vocabulary

| Capability | Meaning | Honest default |
|---|---|---|
| `call_state_monitoring` | observe ring/offhook/idle | needs `READ_PHONE_STATE` |
| `cellular_call_control` | dial / answer / reject / hangup on SIM | needs `CALL_PHONE` or default-dialer telecom APIs |
| `call_audio_capture` | capture of a cellular call's audio | ordinary app: **false** |
| `call_audio_injection` | injecting audio into a cellular call | ordinary app: **false** |
| `ai_cellular_conversation` | AI speaking over cellular-call audio | **false** unless audio path real |
| `provider_realtime_voice` | AI voice via a realtime provider/VoIP | only when a real provider is reachable |
| `voip_available` | internet calling (network + mic) | device-dependent |
| `multi_sim` | >1 SIM slot exposed by the device | device-dependent |

## Backend & provider honesty

* **Simulated backend/provider** are used only for deterministic testing/demos and are
  explicitly labelled `simulated` in status and capability output. They are never presented
  as live.
* **AndroidBridge backend** reports exactly the booleans the device probe returns; if the
  bridge is not configured/reachable it returns a truthful "not connected" report and
  operations raise `NOT_CONFIGURED` / `NETWORK_UNAVAILABLE`.
* **AI voice** requires a configured realtime voice provider. Without one, an AI session
  cannot be created (or runs against the clearly-labelled simulated provider for tests).

## Structured errors

`CALL_AUDIO_UNAVAILABLE`, `ANDROID_PERMISSION_DENIED`, `SIM_UNAVAILABLE`,
`CALL_NOT_ACTIVE`, `AI_PROVIDER_UNAVAILABLE`, `MCP_UNAUTHORIZED`,
`DESTINATION_NOT_ALLOWED`, `CAPABILITY_UNSUPPORTED`, `UNSUPPORTED_ON_THIS_DEVICE`,
`NETWORK_UNAVAILABLE`, `RATE_LIMITED`, `EMERGENCY_STOP_ACTIVE`, `INVALID_CALL_STATE`.
Every MCP result that fails carries `{"ok": false, "code": "...", "error": "..."}`.

## What was / wasn't verified in this sandbox

* **Verified here:** the entire control plane + MCP surface + call-state machine + policy +
  security + AI-session lifecycle, run against the simulated backend (28 automated tests).
* **Not verified here (no Android SDK/device/credentials in this environment):** compiling
  the APK, running the Android foreground service, live SIM calls, live audio, a real
  voice provider, and the real device bridge. These require your Android Studio SDK and a
  physical device, per `docs/android.md`. This is stated plainly, not hidden.

## Safety / authorization constraints

Designed for calls initiated/managed by the **authorized phone owner**. No stealth
calling, caller-ID spoofing, covert recording, or interception of third-party calls.
AI callers identify themselves appropriately. Recording/transcription are configurable and
must comply with applicable law.
