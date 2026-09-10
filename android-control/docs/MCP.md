# MCP server — agent-callable unified Android Control

The **whole** Android Control system — the ADB engine (drive Android from
Windows: screen, touch, keyboard, files, messaging, multi-device) **and** the
Remote Touchpad companion (authorized phone → this PC) — is exposed as an MCP
**stdio server**. An agent host (Claude Desktop, Cursor, OpenCode, custom
clients) calls it via tools. The same package stays importable as a normal
Python library.

No MCP SDK is needed: the server speaks newline-delimited JSON-RPC 2.0 over
stdio, so it does not break as MCP SDKs change.

## Run it (stdio)

```bash
# from an installed package:
android-control-mcp --offline     # deterministic mock (no phone)
android-control-mcp               # live (needs adb on this Windows host)

# or directly:
python mcp_server.py --offline
python -m android_control --mcp --offline
```

Wire it into an MCP client as a stdio server, e.g.:
```jsonc
{
  "mcpServers": {
    "android-control": {
      "command": "android-control-mcp",   // or "python .../mcp_server.py"
      "args": ["--offline"],              // omit for live
      "env": { "AC_RT_ENABLED": "true" }  // optional: enable Remote Touchpad companion
    }
  }
}
```

## Tools (38)

Discovery/connection: `list_devices`, `discover`, `status`, `connect`,
`disconnect`, `reconnect`, `verify`.

Screen: `take_screenshot`, `screen_record`, `screen_info`.

Touch / mouse: `tap`, `long_press`, `swipe`, `scroll`.

Keyboard: `type`, `key`, `back`, `home`, `recents`.

Semantic UI: `ui_tree`, `ui_find`, `ui_click`, `ui_type`, `ui_read`.

Apps / intents: `apps_list`, `app_launch`, `app_stop`, `open_url`,
`open_settings`.

Files: `files_list`, `send_file` (Windows→Android), `receive_file`
(Android→Windows).

Messaging: `send_message`, `receive_messages` (agent ⇄ device; not SMS).

Shell / info: `shell`, `device_info`.

Remote Touchpad companion (phone → this PC): `remote_touchpad`
(status/start/stop/resolve).

Autonomy: `run_goal` (natural-language goal over the fleet).

Every device-taking tool accepts an optional `device` argument: omit or use
`"all"` for every connected device, or pass a device id (`device_001`), serial,
model, or group name. Multi-device operations return isolated per-device
outcomes (never one ambiguous status).

## Resources & prompts
- Resources: `android://registry` (device fleet), `android://skills`
  (skill catalogue), `android://capabilities`.
- Prompts: `control_device` (drive a named device), `phone_touchpad` (start the
  Remote Touchpad companion and report its URL).

## Example session
See `examples/mcp_client.py` for a working stdio client. In brief:
```
initialize        -> serverInfo {name:"android-control", version:"1.0.0"}
tools/call discover            -> registers the fleet
tools/call list_devices        -> device profiles
tools/call take_screenshot     -> {device, status: SUCCESS, ...}
tools/call send_message {message:"...", device:"device_001"}
tools/call remote_touchpad {action:"status"}
```

## Verification status (honest)
Verified in this workspace (offline, deterministic): the MCP surface —
initialize, 38 tools/list, tool calls (discover/list_devices/screenshot/tap/
type/ui_tree/send_message/remote_touchpad), resources, prompts, and the stdio
client round-trip — all pass with 4 mock devices. Real-device behaviour still
requires adb + hardware on your Windows host (not exercised here).
