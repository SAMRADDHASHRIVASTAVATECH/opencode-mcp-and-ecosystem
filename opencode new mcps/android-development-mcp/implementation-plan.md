# Android MCP — Implementation Plan

1. Kernel (errors, sandbox, runner)
2. Environment detection
3. Scaffold + inspect (no SDK required)
4. Components, manifest, resources, dependencies
5. Gradle/ADB/emulator adapters (fail closed)
6. Diagnostics, security audit, artifact inspect
7. Tests without SDK + mocked CLI
8. Gap audit

Host limitation: this environment has JDK 11 and no Android SDK. Tests must not require a successful `assembleDebug`.
