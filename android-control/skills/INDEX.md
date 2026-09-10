# android-control skills

Each skill is an independently callable module under ``android_control.skills``; the master skill orchestrates them. No device limit is assumed.

- `android_control` — Universal Android Control Master
- `android_discovery` — Discover connected Android devices
- `android_adb` — ADB engine: server, devices, connect/pair
- `android_shell` — Run checked Android shell commands
- `android_device_info` — Read the full device profile
- `android_input` — Inject taps, swipes, text and key events
- `android_screen` — Screenshots, screen recording, display info
- `android_ui` — Semantic UI hierarchy, find/click/type
- `android_apps` — List/launch/stop/inspect applications
- `android_files` — Push/pull/list/verify files
- `android_intents` — Fire Android intents
- `android_vision` — Visual fallback observation
- `android_recovery` — Reconnect & self-heal devices
- `android_multi_device` — Fleet overview, groups, parallel control
- `android_messaging` — Agent<->device messaging channel
- `android_remote_touchpad` — Remote-Touchpad host: phone as PC touchpad/keyboard
