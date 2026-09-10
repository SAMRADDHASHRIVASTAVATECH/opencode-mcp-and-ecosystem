# Android MCP — audit / second research pass

## Lifecycle coverage

| Phase | Covered | Notes |
|-------|---------|-------|
| Environment | yes | JDK major, SDK, platforms, adb, emulator, NDK detect |
| Create | yes | Compose, Views, library, multi-module, MVVM/Clean |
| Modify | yes | components, manifest, catalog deps, strings/locales |
| Build | adapter | Needs JDK 17 + SDK + wrapper jar |
| Device | adapter | adb allowlist |
| Emulator | adapter | list/start/create |
| Test | adapter | unit + connected + JUnit XML paths |
| Debug | yes | Gradle rules + crash/ANR parser |
| Profile | adapter | dumpsys allowlist |
| Security | yes | static audit |
| Package | adapter | assemble/bundle + apkanalyzer/apksigner if present |

## Missed / deferred (honest)

- Full Gradle wrapper JAR vendoring (legal/size; generate via `gradle wrapper`)
- Hilt/Koin full DI Gradle wiring (components can be added; not default)
- NDK/CMake project gen
- Compose UI tests beyond template
- Perfetto traces
- Play Developer API upload
- uiautomator dump / tap (device QA MCPs already exist)
- fastboot flashing (unsafe)

## Redundancy check

23 tools. Device/app actions grouped. No `run_anything`.

## Host test limitation

This sandbox: **OpenJDK 11, no Android SDK**. Tests cover scaffold/inspect/audit/diagnostics. Live assembleDebug / emulator cannot run here; adapters return structured missing-tool errors.

## Improvements after audit

- `android_plan` for research-before-action
- Compose compiler as Kotlin plugin (not old `kotlinCompilerExtensionVersion`)
- Network security config in templates (cleartext off)
- Secret redaction in runner
