# Android module — build, install, run

The `android/` folder is a complete Gradle application module (Kotlin + Jetpack
Compose) implementing the authoritative on-device source: capability probe, call-state
monitor, foreground service, boot handling, secure bridge.

## HONEST REQUIREMENTS NOTE

This repository was produced in a Linux sandbox with **no Android SDK and no physical
device**, and **JDK 11 only** (modern Android Gradle Plugin needs JDK 17+). Therefore the
APK was **not compiled or run here**. The Android source is provided to be opened and
built in **Android Studio** (or with an Android SDK + JDK 17). Do not treat this module as
a verified build until you compile it on your machine. All honesty logic in
`CapabilityProbe` is designed to report the *actual* device state at runtime.

## Requirements

* Android Studio (Ladybug or newer) — or Android command-line tools + JDK 17.
* A physical Android phone (API 26+, i.e. Android 8.0+) to test real telephony.
* Google USB debugging / adb for install.

## Build & install

1. Open the `android/` folder in Android Studio and let it sync (downloads the Gradle
   wrapper + SDK components). If you only have the CLI, from `android/` run
   `gradle wrapper` first if needed, then:
   ```bash
   ./gradlew :app:assembleDebug
   adb install -r app/build/outputs/apk/debug/app-debug.apk
   ```
2. Grant runtime permissions the first time the app asks (Phone state, Phone,
   Contacts, Call log, Notifications). The capability probe reflects what you actually
   granted.

## What the app does on-device

* **CapabilityProbe** — runs a real probe and reports honest booleans (default-dialer
  status, audio capture/injection availability, multi-SIM, etc.).
* **CallStateMonitor** — observes `TelephonyManager` call state and forwards transitions.
* **OlcapForegroundService** — keeps the operator available within Android's permitted
  model; shows the persistent "OLCAP Phone Management: ACTIVE" notification. Cleanly stops
  on emergency stop / Stop.
* **BootReceiver** — restarts the service after reboot where permitted.
* **BridgeClient** — publishes device state/events to the control plane over the
  configured bridge URL + token (from secure prefs via `SecretStore`). Never sends raw
  call audio.
* **MainActivity** — status screen (PHONE / MCP / Telephony / AI Voice / SIMs / ACTIVE
  CALL / AUTONOMOUS ANSWERING), Start/Stop, Emergency Stop, diagnostics.

## Permissions (honest mapping)

`READ_PHONE_STATE` → call-state monitoring. `CALL_PHONE` → initiate calls (not audio).
`READ_CONTACTS`/`READ_CALL_LOG` → caller identity/history. `RECORD_AUDIO` → used only for
an active AI/voice session with explicit opt-in (never covert). `FOREGROUND_SERVICE`
(+ `_PHONE_CALL`) → availability. `RECEIVE_BOOT_COMPLETED` → restart.

## Connecting the app to the control plane

1. Run the control-plane MCP server on the PC/host that runs OpenClaw/OpenCode.
2. Set the bridge endpoint on the phone (via `SecretStore`, e.g. entered in-app or via an
   OLCAP config screen): `bridge_url` = `http://<pc-ip>:<port>` and `bridge_token`.
3. On the host set `OLCAP_BACKEND=android_bridge` and
   `OLCAP_ANDROID_BRIDGE_URL=<same URL>`; keep `remote_access`/token consistent.

The AndroidBridge backend then proxies real device state/capabilities into the MCP surface.
When the phone is not reachable, operations return honest `NOT_CONFIGURED` /
`NETWORK_UNAVAILABLE` errors.

## Troubleshooting

* Service doesn't stay alive → Android battery optimization / vendor restrictions; guide
  the user to disable battery optimization for OLCAP (the app shows a guidance screen).
  Do not bypass OS security.
* No call events → `READ_PHONE_STATE` not granted (re-grant and restart).
* Probe shows audio capture false → that's the honest answer for a non-default-dialer
  app; see `capabilities-and-limitations.md`.
* Gradle build fails on JDK 11 → use JDK 17 (Android Studio ships it).
