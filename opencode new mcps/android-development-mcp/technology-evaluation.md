# Android MCP — Technology Evaluation

| Concern | Primary | Why | Rejected |
|---------|---------|-----|----------|
| MCP | Official Python SDK | Matches sibling specialists | Node-only ADB MCPs |
| Project model | Parse Gradle KTS + XML + TOML | Real structure, not regex-only | Treat as opaque text |
| Scaffold | In-process templates | Deterministic, no network | `android create project` (legacy), Studio wizards |
| Build | `./gradlew` if present else `gradle` | Wrapper is canonical | Invoking Studio |
| Devices | `adb` | Official | scrcpy (device GUI, extra binary) |
| Emulator | `emulator` + `avdmanager` | Official CLI | Android Studio Device Manager only |
| APK inspect | `apkanalyzer` / `aapt2` / zip+XML | Official | apktool as required dep (optional later) |
| Sign | `apksigner` | v1–v4 schemes | jarsigner |
| UI automation | Not primary | This MCP is *development*, not QA farm | uiautomator dumps as optional later |
| Versions | Catalog defaults + SDK probe | Not frozen 2021 numbers | Hardcoded Compose 1.0 |

NDK/CMake: detect and report; do not generate JNI unless requested in a future increment.

Hilt vs Koin: scaffold optional `di=hilt|koin|none`. Default none to keep first build simple; MVVM still generates ViewModel without Hilt.
