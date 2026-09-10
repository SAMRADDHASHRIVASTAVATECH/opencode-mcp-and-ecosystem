# Architecture

Universal Android Control is built so **the agent is the operator** and any
number of phones can be driven concurrently with full isolation.

```
                         AI AGENT
                            │
              (natural-language goal or android.<skill>)
                            ▼
                  UNIVERSAL ANDROID CONTROL MASTER
                  (controller.py + skills.android_control)
                            │
         ┌──────────────────┼──────────────────┐
         ▼                  ▼                  ▼
   AndroidFacade      MultiRunner         Autonomous
   (android.* API)    groups+parallel      goal engine
         │                  │                  │
         ▼                  ▼                  ▼
   DeviceRegistry  ←────────────────  DeviceRegistry
   device_001..N   (isolated DeviceSession + CapabilityProfile each)
         │
         ▼
   Engines: adb · shell · input · screen · ui · apps · files · intents ·
            info · recovery
         │
         ▼
   Transport: AdbTransport (real adb)  |  MockTransport (deterministic, offline)
         │
         ▼
   Android A / B / C … (ADB / Wi-Fi / USB)
```

## Layers

## Two ways to call it
- **Python library:** `import android_control` and use `boot()/boot_offline()`,
  the facade, the skills, or the raw controller.
- **MCP server:** `mcp.py` exposes the whole facade as MCP **tools / resources /
  prompts** over stdio (SDK-independent JSON-RPC). Entry: `android-control-mcp`,
  `python mcp_server.py`, or `python -m android_control --mcp`. See
  `docs/MCP.md`.

## Two directions, one interface
- **ADB engine (primary):** Windows agent → Android (screen stream via scrcpy,
  touch/keyboard into the phone, files, messaging, multi-device).
- **Remote Touchpad backend (companion):** an Android phone → this Windows PC
  (`backends/remote_touchpad.py`, vendored GPLv3 host in `third_party/`).
  Exposed through the same facade + skill registry (`android_remote_touchpad`).
  See `docs/REMOTE_TOUCHPAD.md`.

### Transport — `transport.py`
The single seam between engines and a device. Two implementations:
- **`AdbTransport`**: shells out to the real `adb` binary on the Windows host.
  Every command is run with an explicit `-s <serial>` target when one exists.
  `screencap()` returns raw PNG bytes (never text-decoded).
- **`MockTransport`**: deterministic, hardware-free. Parses the same command
  surface so every engine runs identically in `AC_OFFLINE` selfchecks.

### Engines — `engines/`
Device-targeted stateless engines, each taking `(transport, settings)`:
- `adb.py` — server lifecycle, `devices`, connect/disconnect/pair,
  forward/reverse.
- `shell.py` — `am/pm/cmd/settings/dumpsys/getprop/logcat/screencap/…` plus
  checked free-form `shell(serial, command)` (destructive host-style commands
  refused).
- `input.py` — tap, double-tap, long-press, swipe, drag, scroll, text, key,
  back/home/recents/volume/power.
- `screen.py` — screenshots (binary), screen recording, display/density/
  orientation, optional scrcpy streaming.
- `ui.py` — accessibility hierarchy dump → semantic `UINode`s (text,
  resource-id, content-desc, class, bounds, clickable/editable/…); find /
  click_element / type_into / read_text / scroll_to.
- `apps.py` — list packages, launch, force-stop, inspect, install/uninstall/
  clear/disable (destructive gated by an authorizer).
- `files.py` — list/read/mkdir/rm/push/pull/copy/verify/sha1, Windows↔Android,
  path-traversal protected.
- `intents.py` — open_url/app/settings panels, share, open_file, start_activity,
  broadcast.
- `info.py` — full machine-readable profile (manufacturer/model/version/sdk/arch,
  android_id, display, battery, storage, network, current focus).
- `recovery.py` — wait-for-device, reconnect, restart adb server, reboot
  recovery, capability refresh.

### Vision fallback — `vision/`
`VisionEngine.observe() -> screenshot -> backend -> elements`. The default
`offline` backend returns no false element boxes (honest) so callers use safe
coordinate fallbacks; an `external` backend can be wired via
`AC_VISION_BACKEND=external` + a `{path}` command returning JSON elements.

### Capabilities — `capabilities.py`
Probes a device and builds its `CapabilityProfile` (`ADB`, `Wireless ADB`,
`Shell`, `Input`, `Screenshot`, `Screen Recording`, `File Transfer`,
`Package Control`, `Intent Control`, `UI Hierarchy`, `Semantic UI`,
`scrcpy`) plus version facts (sdk level, Android version). Nothing is assumed
identical across Android versions.

### Registry — `devices/registry.py`
`DeviceRegistry` holds N isolated `DeviceSession`s. Each session carries real
identity (serial, model, manufacturer, android_id, ip/port, connection type)
— never just "Phone 1". Sessions are keyed by `device_id` (device_001…N,
assigned per-registry, deterministic in offline). Thread-safe; a failure in one
session can't corrupt another. Natural-language + group selection resolves to
deterministic ids and raises on ambiguity.

### Facade & orchestrators — `high.py`, `orchestration/`
- `AndroidFacade` exposes the coherent §29 API
  (`screenshot/ui_find/file_pull/open_url/…`) that fans out to one/many/group
  devices and returns `ActionResult` with isolated per-device `DeviceOutcome`s.
- `MultiRunner` executes a per-device callable in parallel with failure
  isolation.
- `DeviceGroups` manages named groups (`all_devices`, `wifi_devices`,
  `android_15`, custom `my_group`).
- `Autonomous` maps natural-language goals (§41) to plans/executions with
  observe→act→verify.

### Results — `result.py`
Structured statuses. Multi-device ops never collapse into one ambiguous status;
they return per-device outcomes plus an aggregated status
(`SUCCESS/PARTIAL_SUCCESS/FAILED/OFFLINE/REQUIRES_AUTHORIZATION/…`).

### Hosts — `hosts.py`
`HostBootstrap` detects/versions/locates/validates host tools (python, adb,
scrcpy, platform-tools), records locations, avoids duplicates, installs only
from official sources when permitted, and raises clear guidance otherwise.

---

## Lifecycle (master command)

```
android_control()
  DISCOVER   → discover devices (usb + paired wireless), register sessions
  VERIFY     → health-check each
  CAPABILITY → scan each device
  READY / PARTIAL  (structured report)
```

On later calls the master returns `VERIFY → REFRESH IF NECESSARY → READY`.

A device that reboots: disconnect is detected → `wait_for_device` → rediscover →
verify adb → refresh state → refresh capabilities → resume.
