# Android Application Development MCP — Research Report

**Date:** 2026-09-09  
**Status:** Research complete. Implementation follows this report.

---

## 1. Domain model

Android development is not “run `adb`.” The lifecycle is:

```
idea → project shape → source/resources/manifest
  → Gradle resolve → compile/D8/R8 → APK/AAB
  → sign/align → install → run → logcat/tests
  → crash/ANR/perf diagnosis → iterate → release
```

An MCP that only wraps CLI commands without **project understanding** (modules, AGP, manifests, Compose vs Views, variants) cannot create or maintain apps.

**Core artifacts**

| Artifact | Role |
|----------|------|
| `settings.gradle(.kts)` | Module graph, plugin management, catalogs |
| `build.gradle(.kts)` | AGP, SDK levels, flavors, deps |
| `gradle/libs.versions.toml` | Version catalog (modern default) |
| `AndroidManifest.xml` | Components, permissions, export, queries |
| `res/` | XML layouts, values, drawables |
| `kotlin/` or `java/` | Source |
| `local.properties` | `sdk.dir` (machine-local, never commit secrets) |
| APK / AAB | Installable / Play upload |
| keystore | Signing identity |

**Languages:** Kotlin is the official default. Java remains for legacy. NDK/CMake for native.

**UI:** Jetpack Compose + Material 3 is the current default for new apps. XML Views remain required for legacy and some OEM/widget surfaces.

**Architecture in the wild:** MVVM + Repository is the Android-recommended baseline (ViewModel, UseCase optional, Hilt/Koin DI). MVI and full Clean Architecture are variants, not mandatory.

---

## 2. Official toolchain (must detect, never assume)

| Tool | Location | Purpose |
|------|----------|---------|
| JDK 17+ | `JAVA_HOME` | AGP 8.x **requires 17**; JDK 21 common |
| Android SDK | `ANDROID_HOME` / `ANDROID_SDK_ROOT` | Platforms, build-tools, extras |
| `sdkmanager` | `cmdline-tools/latest/bin` | Install platforms/images |
| `avdmanager` | same | AVD CRUD |
| `adb` | `platform-tools` | Device bridge |
| `emulator` | `emulator/` | AVD runtime |
| `apkanalyzer` | cmdline-tools | APK size/DEX/manifest |
| `apksigner` / `zipalign` / `aapt2` | `build-tools/<ver>` | Sign, align, resources |
| `bundletool` | separate jar/Google | AAB → APKs |
| Gradle wrapper | `./gradlew` | Canonical build |
| Kotlin | via Gradle plugin | Compiler |
| NDK / CMake | SDK ndk; cmake | Native |
| Android Studio | optional IDE | Not required for CLI MCP |

`sdkmanager` is being superseded by a newer “Android CLI” in cmdline-tools 22+, but `sdkmanager`/`avdmanager` remain the practical automation surface in 2026.

**Environment variables:** `ANDROID_HOME`, `ANDROID_SDK_ROOT`, `JAVA_HOME`, `ANDROID_AVD_HOME`, `GRADLE_USER_HOME`.

---

## 3. Current version reality (2026)

Research (developer.android.com, Compose BOM notes, AGP/KMP plugin docs):

| Coordinate | Practical default for new projects | Notes |
|------------|--------------------------------------|-------|
| compileSdk / targetSdk | **35** (36 appearing in templates) | Detect installed platforms if SDK present |
| minSdk | **26** (Compose works from 21) | 24 still common |
| AGP | **8.7.x – 8.13.x** | Needs JDK 17 |
| Gradle | **8.11+** matching AGP table |
| Kotlin | **2.0.21 – 2.2.x** | Compose compiler is `org.jetbrains.kotlin.plugin.compose` matching Kotlin |
| Compose BOM | **2025.01+ / 2026.08.00** | Always BOM, never pin every artifact |
| Java bytecode | **17** | |

The MCP **must not hardcode as the only truth**. Defaults are used when the SDK cannot be queried; if platforms are installed, pick the highest installed `android-N` ≥ 34.

This sandbox (research host): OpenJDK 11, **no Android SDK, no adb, no emulator**. The MCP must work in this state: generate/inspect/audit fully; build/device/emulator return `DEPENDENCY_MISSING` with install steps.

---

## 4. Existing Android MCPs (lessons)

| Project | Focus | Gap |
|---------|-------|-----|
| MauricePutinas/Android-Studio-MCP | 73 tools: Gradle, ADB, AVD, APK, Studio UI | Windows-heavy IDE automation; huge tool count |
| iksnerd/adb-mcp | Device UI drive + Gradle | Device-operator, weak project authoring |
| scrcpy-mcp / android-mcp-server | Screenshots, taps, logcat | Not an app factory |
| Bzcasper/android-adb-mcp | Allowlisted shell | Correct security instinct |

**Takeaway:** Device-control MCPs are common. **Project creation, architecture scaffolding, manifest/security audit, Gradle diagnosis, and release verification** are the gaps this specialist must fill. Do not expose unbounded `adb shell`. Self-healing build errors (map failure → next tool) is worth copying.

---

## 5. Gradle / AGP capabilities to expose

Tasks that matter:

- `assembleDebug` / `assembleRelease` / `bundleRelease`
- `test` / `connectedAndroidTest` / `lint`
- `clean`, `dependencies`, `signingReport`, `outgoingVariants`
- Product flavors + build types (`debug`, `release`, custom)
- Version catalogs
- Dependency conflict diagnosis (`--scan` optional, never required)

Failure classes: missing SDK, license not accepted, compileSdk/AGP mismatch, JDK too old, kapt vs KSP, Compose compiler mismatch, resource merge, manifest merge, R8/proguard.

---

## 6. ADB / emulator

**Devices:** `adb devices -l`, distinguish `emulator-*` vs USB vs `unauthorized` vs none.

**App:** install (`-r -d -t`), uninstall, `am start` / `am force-stop`, `pm clear`, `pm grant`/`revoke`.

**Observe:** logcat (buffered, filtered by pid/tag/package), `dumpsys` allowlist (`meminfo`, `cpuinfo`, `gfxinfo`, `batterystats`, `activity`, `package`, `window`, `connectivity`), screenshot (`screencap`), screenrecord (time-capped), bugreport (opt-in, huge).

**Emulator:** `emulator -list-avds`, `avdmanager create/delete`, `emulator -avd NAME -no-window -gpu swiftshader_indirect` for CI, wait for `sys.boot_completed`.

**Not in default MCP:** `fastboot flash`, `adb reboot bootloader`, root, arbitrary shell, installing random Magisk modules.

---

## 7. Testing

- JVM unit: `./gradlew :app:testDebugUnitTest`
- Instrumented: `connectedDebugAndroidTest` (needs device)
- Espresso / Compose UI test
- JUnit XML under `build/test-results` and `build/outputs/androidTest-results`
- Lint XML `build/reports/lint-results-*.xml`

Workflow: BUILD → INSTALL → RUN → TEST → parse reports → diagnose.

---

## 8. Security (apps and the MCP)

**App audit:** exported components without permission, `android:debuggable`, `allowBackup` + sensitive data, cleartext traffic, WebView JS interface, hardcoded secrets, overly broad permissions, `taskAffinity` tricks, FileProvider paths.

**MCP:** path sandbox, no secret echo, release signing confirm + env for passwords, allowlisted dumpsys/shell, no fastboot flash, APK install confirm.

---

## 9. Packaging

```
assemble/bundle → zipalign (APK) → apksigner → apksigner verify / apkanalyzer
```

AAB is the Play Store artifact. APK for sideload/emulator. Debug uses the Android debug keystore; release needs a user keystore **path**, never generated into git with a default password in-repo.

---

## 10. Implementation implication

Build a **project-aware** Android MCP:

1. Environment detector first.
2. Scaffold Kotlin DSL + version catalog templates (Compose default, Views, library, multi-module).
3. Inspect/modify real Gradle/manifest/source.
4. Gradle/ADB/emulator adapters that fail closed when tools missing.
5. Diagnostic analyzers for Gradle, logcat crashes, ANR, lint, JUnit.
6. Security audit + artifact inspect.

Python + official `mcp` SDK, same pattern as the other specialists. No Android Studio required.
