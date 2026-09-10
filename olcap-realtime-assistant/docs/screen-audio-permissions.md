# Screen & audio permissions (Windows)

## Microphone (spec 5)

* Requires the OS microphone permission. On Windows 10/11, enable **Settings →
  Privacy → Microphone** for this app.
* Uses `sounddevice` (PortAudio). Select a device with `audio.select_device` after
  `audio.list_devices`. `audio.test` verifies the input.
* The assistant never bypasses OS privacy controls; without permission, `audio.start`
  returns `AUDIO_UNAVAILABLE` with the reason.

## System audio

Configurable (`audio.capture_system_audio`) but only where the OS permits (WASAPI loopback
on Windows). It stays OFF by default and is never silently enabled.

## Screen (spec 9, 10, 30)

* Uses `mss`. On a headless session or without a desktop, `screen.*` returns
  `SCREEN_UNAVAILABLE` — never faked.
* Privacy controls: `screen_monitoring`, `active_window_only`, `selected_region_only`,
  `capture_interval_s`, `record_screenshots`, `cloud_vision`, plus
  `ignored_applications`/`allowed_applications`.
* Change detection + duplicate-frame suppression means the assistant does **not** capture
  every moment — only meaningful changes, downscaled before any inference.
* Global `assistant.emergency_stop` stops capture immediately.

### Allowed / ignored applications

```jsonc
{ "screen": { "ignored_applications": ["password_manager", "banking_app"] } }
```

Windows app/window detection uses a desktop API (`pygetwindow`) when available; active
window/title is used only to enrich context and can be disabled.
