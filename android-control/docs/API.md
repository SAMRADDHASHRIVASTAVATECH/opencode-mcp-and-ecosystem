# API reference

Two surfaces: the **facade** (`android.<op>` style) and the **skill modules**
(individually callable). Both return `ActionResult`.

## Result envelope (`android_control.result`)

```python
{
  "operation": "...",
  "status": "SUCCESS",          # or PARTIAL_SUCCESS/FAILED/OFFLINE/…
  "error": "",
  "note": "",
  "duration_ms": 12.3,
  "data": ...,
  "devices": [                  # multi-device outcomes
     {"device_id": "device_001","serial":"…","model":"…","status":"SUCCESS",
      "data":…,"error":"","duration_ms":…,"verification":"…","recovery":""}
  ]
}
```

Statuses: `SUCCESS, PARTIAL_SUCCESS, FAILED, OFFLINE, REQUIRES_AUTHORIZATION,
UNSUPPORTED, TIMEOUT, RUNNING, CANCELLED, SKIPPED`.

## Facade (`AndroidFacade`) — §29

Every method takes an optional `device` selector (`None`=all connected, or an
id/serial/model/token or a group name).

Discovery & state
- `discover()`, `devices()`, `status(device)`, `capabilities(device)`,
  `verify(device)`, `recover(device)`, `reconnect(device)`, `connect(id)`

Control
- `shell(command, device)` · `tap(x,y,device)` · `swipe(x1,y1,x2,y2,dur,device)`
- `key(keycode, device)` · `type(text, device)` · `back(device)` · `home(device)`
- `screenshot(device)` · `screenrecord(seconds, device)`
- `ui_tree(device)` · `ui_find(device, **criteria)` ·
  `ui_click(device, **criteria)` · `ui_type(text, device, **criteria)` ·
  `ui_read(device)`

Apps & intents & files
- `apps_list(device)` · `app_launch(package, device)` · `app_stop(package, device)`
- `open_url(url, device)` · `open_settings(panel, device)`
- `files_list(path, device)` · `file_push(src,dst,device)` ·
  `file_pull(src,dst,device)`
- `info(device)` · `dumpsys(service, device)` · `logs(device)` · `restart(id)`

Messaging (§5, agent ⇄ device application channel — not SMS/WhatsApp/etc.)
- `send_message(message, device)` — agent → device plain text
- `send_message(None, structured={...}, device)` — agent → device structured event
- `receive_messages(device)` — poll device → agent since last read (cursor based)
- `ingest_message(message, device)` — route/simulate an inbound message for tests

> These are an application-level channel over the control connection; no
> third-party messaging service is used or implied.

`ui_find/ui_click/ui_type` criteria: `text`, `text_contains`, `resource_id`,
`content_desc`, `cls`.

## Skill modules (`android_control.skills`)

`android_control`, `android_discovery`, `android_adb`, `android_shell`,
`android_device_info`, `android_input`, `android_screen`, `android_ui`,
`android_apps`, `android_files`, `android_intents`, `android_vision`,
`android_recovery`, `android_multi_device`.

Each is a plain function returning `ActionResult`. Examples:

```python
from android_control import skills as sk
sk.android_screen(screenshot=True, device="all", offline=True)
sk.android_apps(action="launch", package="com.whatsapp", device="device_001", offline=True)
sk.android_control(offline=True)      # master boot report
```

## Top-level helpers (`android_control`)

- `android_control(offline=None)` — master boot.
- `boot(settings)` / `boot_offline()` — get a facade for real / mock.
- `run_goal(goal, offline=None)` — natural-language autonomous goal.
- `control(settings)` — low-level master controller.

## Autonomous goals

`run_goal()` parses representative natural language (§41) and executes with
per-device verification. Supported intent families: screenshot, record,
launch an app, open a URL, open settings (+ sub-panels), open the camera,
list devices, list apps, what's foreground, pull latest photo, restart,
shell, read UI. Unrecognised goals raise `UnsupportedOperationError` listing
the supported intents (the agent is expected to drive recognised ones or call
a skill directly).

## Engines

For fine-grained control, engines are reachable on the controller:
`f.ctrl.shell|input|screen|ui|apps|files|intents|info|vision`. Each method
takes an explicit device `serial`.
