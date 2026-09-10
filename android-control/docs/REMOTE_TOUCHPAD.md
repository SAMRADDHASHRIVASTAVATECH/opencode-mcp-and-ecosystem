# Remote Touchpad — embedded companion backend

This is the **`Unrud/remote-touchpad`** project (GPLv3), vendored in full under
`third_party/remote-touchpad/` (source + `COPYING`), and managed through the
same one-interface `android-control` system.

## What it provides (be precise)
Remote Touchpad runs a small **HTTP + WebSocket server on the PC**. An
authorized **Android phone's browser** opens the URL/QR and becomes a **remote
touchpad + keyboard for that PC** (pointer move, left/right/middle button,
scroll, key events, text). Backends: Windows (SendInput), X11, Wayland portal,
uinput.

**Direction is phone → PC.** It is the *companion* of the ADB engine:
- ADB engine (primary): Windows agent → controls Android (screen stream,
  touch/keyboard into the phone, files, messaging, multi-device).
- Remote Touchpad (companion): an Android phone → controls this Windows PC's
  pointer and keyboard over the LAN.

Both are reachable through the single agent interface so the two live "in one
place".

## Why it is separate (licence + scope)
- Remote Touchpad is **GPLv3**. The `android-control` core is MIT. They are kept
  as distinct components: `src/android_control/` (MIT) and
  `third_party/remote-touchpad/` (GPLv3, unchanged, with its licence).
- It does **not** provide Android screen capture, file transfer, messaging, or
  multi-Android-device control — those come from the ADB engine and are not
  duplicated here.

## Install on the Windows host
```bash
# 1) get the binary (official upstream release only)
python scripts/download_remote_touchpad.py
#    -> downloads Unrud/remote-touchpad windows binary to AC_INSTALL_DIR

# 2) enable it
set AC_RT_ENABLED=true
set AC_RT_BIN=%USERPROFILE%\.android_control\tools\remote-touchpad\remote-touchpad_windows_amd64.exe
# (optional) set AC_RT_BIND=:5555 and a fixed AC_RT_SECRET

# 3) start it from Python / CLI
python -m android_control --remote-touchpad start      # (if CLI flag added)
```
Alternative: build from the vendored source with recent Go + mingw-w64
(`cd third_party/remote-touchpad && go build .`), or point `AC_RT_BIN` at any
remote-touchpad binary you already have.

## Agent interface
```python
import android_control as ac
f = ac.boot()                       # real Windows host
info = f.remote_touchpad("start", secret="mysecret")
url  = info.data["url"]             # give this to the phone (or scan QR)
f.remote_touchpad("status")
f.remote_touchpad("stop")
```
Or the individual skill: `android_control.skills.android_remote_touchpad(...)`.

## Configuration
| Var | Meaning | Default |
|-----|---------|---------|
| `AC_RT_ENABLED` | enable the companion backend | false |
| `AC_RT_BIN` | path to remote-touchpad exe | auto |
| `AC_RT_AUTODOWNLOAD` | fetch official release if missing (Windows) | true |
| `AC_RT_BIND` | `[host]:port` (0 = ephemeral) | `:0` |
| `AC_RT_SECRET` | shared secret (empty = random) | random |
| `AC_RT_RELEASE` | release tag to download | v1.5.4 |

## Verification status (honest)
- Verified in this workspace: the Python **manager state machine** (resolve →
  start → parse URL → status → stop) using a stub binary; configuration;
  vendored source + licence present; skill + facade wiring; the 16-skill
  registry and messaging/screen/touch/keyboard/files checks.
- **Not** verified here: running the real Windows binary with a physical phone
  (no Windows/Go/phone in this sandbox). Do that on your Windows host with a
  device you own and are authorized to control, on a network you trust
  (remote-touchpad supports TLS via `--cert/--key`; prefer it on untrusted
  networks).
