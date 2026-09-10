# Android Application Development MCP

Standalone MCP for the **Android app lifecycle**: environment detection, project creation, architecture scaffolding, Gradle, ADB/emulator, testing, crash/build diagnosis, security audit, and APK/AAB inspection.

It is **not** merged with the Office, Database, or Windows MCPs. The previous Audio/Video research MCP was removed in favor of this specialist.

Research artifacts in this folder: `research-report.md`, `capability-matrix.md`, `technology-evaluation.md`, `architecture.md`, `security-model.md`, `implementation-plan.md`, `gap-analysis.md`.

## Why this shape

Existing Android MCPs are mostly **device operators** (screenshots, taps, logcat). This one is a **development** specialist: Kotlin DSL + version catalog templates, project inspection, manifest/security, Gradle failure mapping, and fail-closed toolchain adapters.

Defaults (overridable, and raised if a higher `platforms;android-N` is installed): AGP **8.7.3**, Kotlin **2.0.21** + Compose compiler plugin, Compose BOM **2025.01.01**, compile/target **35**, minSdk **26**, Java **17**.

## Install

```bash
pip install -e ./android-development-mcp
python -m android_mcp
```

```json
{
  "mcpServers": {
    "android-development": {
      "command": "python",
      "args": ["-m", "android_mcp"],
      "env": { "ANDROID_MCP_ROOT": "/path/you/allow" }
    }
  }
}
```

## Honest environment behavior

If JDK 17 / Android SDK / adb are missing (as on many CI agents):

- **Works:** create, inspect, components, manifest, resources, deps, security audit, crash/build-log analysis, `android_plan`
- **Returns `DEPENDENCY_MISSING`:** assemble, emulator, install, logcat, screenshot, sdkmanager

Never pretends a build succeeded.

## Tools

`android_detect_environment` `android_plan` `android_create_project` `android_inspect_project` `android_create_module` `android_create_component` `android_modify_manifest` `android_manage_dependencies` `android_manage_resources` `android_gradle` `android_analyze_build_failure` `android_devices` `android_avd` `android_app` `android_logcat` `android_screenshot` `android_adb` `android_run_tests` `android_analyze_crash` `android_profile` `android_security_audit` `android_inspect_artifact` `android_sdk`

`adb shell` is **allowlisted**. APK install needs `confirm=true`.

## Tests

```bash
PYTHONPATH=android-development-mcp/src pytest android-development-mcp/tests -q
```
