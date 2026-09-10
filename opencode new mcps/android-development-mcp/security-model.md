# Android MCP — Security Model

| Threat | Control |
|--------|---------|
| Path traversal | `ANDROID_MCP_ROOT` sandbox |
| Arbitrary adb shell | Allowlist only |
| fastboot flash / reboot-bootloader | Not implemented |
| Release keystore passwords | Env `ANDROID_MCP_KEYSTORE_PASS`; never logged |
| Overwrite projects | `overwrite=false` default |
| Gradle untrusted init scripts | Invoke wrapper with `--no-daemon` optional; no `-I` user init |
| APK sideload malware | install requires `confirm=true` |
| Secret leakage in logcat | Truncate; optional redact patterns |
| Network SDK install | `android_sdk` install requires confirm |

Read-only mode: `ANDROID_MCP_READ_ONLY=1` blocks create/write/gradle/install.

ADB shell allowlist prefixes: `pm `, `am `, `dumpsys `, `getprop`, `settings get`, `wm `, `input keyevent`, `screencap`, `ps `, `logcat`, `toybox id`, `cmd package`, `cmd activity`.
Denied: `rm`, `reboot`, `su`, `dd`, `chmod 777`, `setprop`, `wipe`.
