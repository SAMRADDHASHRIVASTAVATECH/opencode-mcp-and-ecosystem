# Android MCP — Architecture

```
MCP tools (semantic)
    ▼
android_plan / policy (sandbox, confirm, allowlists)
    ▼
domain
  inspect | scaffold | components | manifest | catalog
    ▼
adapters
  env | gradle | adb | emulator | apk | diagnostics
    ▼
host toolchain (may be missing → structured error)
```

## Tool surface (optimal, not 70 micro-tools)

1. `android_detect_environment`
2. `android_plan`
3. `android_create_project`
4. `android_inspect_project`
5. `android_create_module`
6. `android_create_component`
7. `android_modify_manifest`
8. `android_manage_dependencies`
9. `android_manage_resources`
10. `android_gradle`
11. `android_analyze_build_failure`
12. `android_devices`
13. `android_avd`
14. `android_app`
15. `android_logcat`
16. `android_screenshot`
17. `android_adb`
18. `android_run_tests`
19. `android_analyze_crash`
20. `android_profile`
21. `android_security_audit`
22. `android_inspect_artifact`
23. `android_sdk` (list/install packages if sdkmanager exists)

## Why this grouping

`android_app` covers install/uninstall/launch/stop/clear/permissions instead of six tools. `android_gradle` takes a `task` enum. `android_create_component` is the code generator. `android_plan` implements research-before-action without executing.

## Result contract

Same `{ok, data, warnings, error{code,message,details}}` as sibling MCPs.
Codes: VALIDATION, NOT_FOUND, PERMISSION, UNSUPPORTED, DEPENDENCY_MISSING, TIMEOUT, SECURITY, EXTERNAL, INTERNAL.
