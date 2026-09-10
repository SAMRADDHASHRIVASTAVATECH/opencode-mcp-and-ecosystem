# Universal Android Control — Skill & Runtime

A production-shaped, reusable **Universal Android Control** skill for an AI
agent running on **Windows**. It lets the agent autonomously **discover,
initialize, connect, observe, control, verify, recover and disconnect** one
Android phone **or any number of phones simultaneously**, primarily over
wireless ADB — without the human translating goals into ADB commands.

The user thinks in terms of:

> "Control my Android phones."

not:

> "Run this ADB command."

The agent (or this package's natural-language engine) chooses and executes the
correct underlying mechanism.

> **Honesty note.** Real-device control needs real host tooling (adb, and
> optionally scrcpy) and real devices. Everything here is implemented and runs,
> but **no physical phone is available in this workspace**, so every end-to-end
> behaviour is validated against a **deterministic offline mock transport**
> (`AC_OFFLINE=true` / `--offline`) that exercises the same code paths without
> hardware. Live ADB is wired but untested against hardware here — treat it as
> such until exercised on a phone.

---

## What it does

- **No hard-coded device limit.** 1, 2, 5, 10, 20 … N devices. Each device gets
  an isolated `DeviceSession` + `CapabilityProfile`.
- **Scoped capabilities only:** Screen (view/screenshot/record) · Touch/Mouse
  (tap/swipe/scroll/long-press) · Keyboard (type/keys) · Files (both
  directions, list) · **Agent Messaging** (a structured agent⇄device channel —
  not SMS/WhatsApp) · Multi-device. Nothing beyond that is included (no
  app-management-only automation, no stealth/takeover, etc.).
- **One place for two directions.** The same agent interface also manages the
  vendored **Remote Touchpad** host (`Unrud/remote-touchpad`, GPLv3) so an
  authorized phone can act as a wireless touchpad + keyboard **for this PC**.
  The ADB engine drives Android from Windows; Remote Touchpad lets a phone
  drive the PC. See `docs/REMOTE_TOUCHPAD.md`.
- **Agent-callable as an MCP server.** The whole unified system is exposed as
  an MCP **stdio server** (`android-control-mcp`, `python mcp_server.py`,
  `python -m android_control --mcp`) with 38 tools + resources & prompts, while
  remaining importable as a normal Python library. See `docs/MCP.md`.
- **Master skill** `android_control()` plus **individually callable skills**
  (never a monolithic black box): discovery, adb, shell, input, screen, ui,
  apps, files, intents, vision, device-info, recovery, multi-device, messaging.
- **Zero-assumption bootstrap**: discover → check environment/deps → install
  missing host tools (only from official sources, only when permitted) →
  discover devices → connect/pair → verify → capability scan → ready.
- **Multi-device operations**: single, parallel, broadcast, group, conditional,
  per-device-different-tasks — with **failure isolation** and per-device
  structured results (`SUCCESS / PARTIAL_SUCCESS / FAILED / OFFLINE /
  REQUIRES_AUTHORIZATION / UNSUPPORTED / TIMEOUT`).
- **OBSERVE → PLAN → ACT → VERIFY** for every meaningful action; never assume
  success from an exit code alone.
- Semantic UI control with a **vision / coordinate fallback**.
- Self-healing: reconnect, reboot recovery, capability refresh — a device
  going offline never crashes the fleet.

---

## Layout

```
android-control/
├── pyproject.toml
├── README.md  ARCHITECTURE.md  SECURITY.md  .env.example  LICENSE
├── skills/                      # travelling markdown skills (see below)
├── third_party/remote-touchpad/ # vendored GPLv3 Unrud/remote-touchpad host
├── docs/                        # API, MCP, SECURITY, REMOTE_TOUCHPAD, …
├── examples/
│   ├── quickstart_offline.py
│   ├── selfcheck.py
│   ├── mcp_client.py            # drive the MCP server as a client
│   ├── remote_touchpad_demo.py
│   └── custom_authorizer.py
├── mcp_server.py                # MCP stdio entry point
└── src/android_control/
    ├── config.py  errors.py  result.py  transport.py  hosts.py
    ├── capabilities.py  logging.py  controller.py  high.py  mcp.py
    ├── devices/          # registry + sessions
    ├── engines/          # adb shell input screen ui apps files intents
    │                     # info recovery message
    ├── backends/         # remote_touchpad companion backend
    ├── vision/           # visual fallback
    ├── orchestration/    # multi-device runner, groups, autonomous goals
    ├── skills/           # master + individual skills (the callable layer)
    └── __main__.py       # CLI
```

---

## Install & run

Python 3.10+. No hard Python runtime deps (host tools are detected/installed).

```bash
cd android-control
python -m venv .venv && . .venv/Scripts/activate    # Windows
pip install -e .

# deterministic offline demo (no phone) — the master boot report
android-control --offline
# or
python -m android_control --offline

# list available skills
android-control --offline --list-skills

# natural-language goal
android-control --offline --goal "open the camera on every connected phone"
android-control --offline --goal "take screenshots of every phone"

# serve the MCP server (agent-callable, stdio)
android-control-mcp --offline
# or
python mcp_server.py --offline
```

**Live mode** (requires a Windows host with real devices):
```bash
android-control                     # discover + connect real devices
python -m android_control --goal "open settings on phone 2"
android-control-mcp                 # live MCP server
```

If `adb` is missing the bootstrap reports it; enable `AC_AUTO_INSTALL=true` to
attempt an official install via `winget` (Google.PlatformTools), or set
`AC_ADB_PATH` / `AC_PLATFORM_TOOLS_DIR`.

---

## Python API (offline demo)

```python
import android_control as ac

# deterministic, no hardware
f = ac.boot_offline()
print(len(f.ctrl.registry.all()), "devices")

r = f.screenshot()                      # every device
print([(o.device_id, o.status) for o in r.devices])

# groups
f.groups.create("pixels", ["device_001", "device_002"])
f.screenshot(device="pixels")

# one device explicitly
f.app_launch("com.whatsapp", device="device_001")

# natural-language goal across the fleet
res = ac.run_goal("open the camera on every connected phone", offline=True)
for o in res.devices:
    print(o.device_id, o.status, o.data)
```

Live is identical but with `ac.boot()` / `ac.android_control()`.

---

## Skills

Canonical markdown lives in `skills/`; the Python callables live in
`android_control.skills`. See `skills/INDEX.md`. The master skill
(`skills/android-control/SKILL.md`) documents the full lifecycle and §29 API.

---

## Configuration

All knobs are `AC_`-prefixed env vars (copy `.env.example`). Highlights:

| Var | Meaning | Default |
|-----|---------|---------|
| `AC_OFFLINE` | deterministic mock mode (no hardware) | false |
| `AC_ADB_PATH` / `AC_SCRCPY_PATH` / `AC_PLATFORM_TOOLS_DIR` | explicit host tools | auto |
| `AC_AUTO_INSTALL` | allow official-source installs (winget) | true |
| `AC_WIRELESS` / `AC_ADB_TCP_PORT` | wireless debugging | true / 5555 |
| `AC_AUTO_RECONNECT` / `AC_RECOVER_ON_OFFLINE` | self-healing | true |
| `AC_MAX_PARALLEL` | worker limit (0 = auto) | 0 |
| `AC_REQUIRE_AUTH_DESTRUCTIVE` | gate destructive ops | true |
| `AC_VISION_BACKEND` | `offline` or `external` | offline |
| `AC_MOCK_DEVICES` | custom offline fleet (comma separated) | 4 demos |

See [ARCHITECTURE.md](ARCHITECTURE.md), [SECURITY.md](SECURITY.md), and
`docs/API.md`.
