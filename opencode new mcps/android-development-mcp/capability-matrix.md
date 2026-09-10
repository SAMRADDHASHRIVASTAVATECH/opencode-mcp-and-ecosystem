# Android MCP — Capability Matrix

P = primary, F = fallback when tool present, N = not exposed.

## BASIC

| Capability | Status | Tool |
|------------|--------|------|
| Detect JDK/SDK/adb/emulator/gradle | P | `android_detect_environment` |
| Create Kotlin Compose app | P | `android_create_project` |
| Create Views/XML app | P | `android_create_project` |
| Create library / multi-module | P | `android_create_project` |
| Inspect project structure | P | `android_inspect_project` |
| List devices | P | `android_devices` |

## ADVANCED

| Capability | Status | Tool |
|------------|--------|------|
| Create Activity/Fragment/Compose/VM/Repo/Service/Receiver | P | `android_create_component` |
| Manifest permissions/components | P | `android_modify_manifest` |
| Version catalog + Gradle deps | P | `android_manage_dependencies` |
| Strings/themes/locales | P | `android_manage_resources` |
| Gradle assemble/bundle/test/lint/clean | P | `android_gradle` |
| Install/launch/stop/clear app | P | `android_app` |
| Logcat filter | P | `android_logcat` |
| Screenshot | P | `android_screenshot` |
| AVD list/create/start/stop | P | `android_avd` |

## EXPERT / DIAGNOSTICS / SECURITY / RELEASE

| Capability | Status | Tool |
|------------|--------|------|
| Plan before action | P | `android_plan` |
| Build failure analysis | P | `android_analyze_build_failure` |
| Crash / ANR analysis | P | `android_analyze_crash` |
| dumpsys mem/cpu/gfx/battery/activity | P | `android_profile` |
| Manifest/source security audit | P | `android_security_audit` |
| APK/AAB inspect + signature verify | P | `android_inspect_artifact` |
| JUnit/lint report parse | P | `android_run_tests` |
| Allowlisted adb shell | P | `android_adb` |
| NDK project authoring | N | Detect-only |
| fastboot flash | N | Too destructive |
| Unbounded shell | N | RCE |

## AUTOMATION

Create → inspect → (build if SDK) → install → launch → logcat → test → audit → artifact.
