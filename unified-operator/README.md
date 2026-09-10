# Unified Operator — one autonomous MCP server for Google Workspace · Discord · Voice · Meet · OpenClaw

A production-grade, fully-autonomous communications & productivity **operator** built
around **OpenClaw** and exposed to **OpenCode** (or any MCP client) through **ONE MCP
server**. It behaves as a single operator that can read/write email & calendar, chat on
Discord, make scheduled phone calls, join Google Meet, run a persistent multi-step
workflow engine, and call back into OpenClaw's own agent/gateway — all under one
account-aware, permission-gated, audited surface.

> **Design rule: real capabilities only, never fake.** When a live service or a required
> transport isn't configured, the operator says so and (where deterministic) offers an
> explicit offline simulation flagged as such. It never reports false success, never
> claims OpenClaw's app-voice is PSTN calling, and never claims it "participated" in a
> Meet it did not actually join.

---

## Why one server?

Instead of a dozen separate MCP servers with inconsistent auth, the Unified Operator puts
every platform behind a single dispatcher so that:

* **A single autonomous agent** (`openclaw.execute`, `operator_*`) can span systems in one
  call chain and across one persistent workflow.
* **Account isolation** — every action resolves an identity per platform
  (`google::work`, `discord::main`), so one operator can hold several accounts cleanly.
* **One permission system** — `automatic` / `confirmation_required` / `blocked`,
  overridable per action *and* per account.
* **One audit + one state store** (SQLite) that survives restarts: call queue, call
  history, follow-up tasks and workflows all persist.
* **Consistent honesty** — deterministic mock mode is explicitly labelled; anything a real
  API can't do is reported, not invented.

---

## Feature surface

| Namespace | What it does |
|---|---|
| `google.*` (31 ops) | Gmail (search/read/thread/send/reply/forward/draft/labels/trash), Calendar (list/search/create/update/cancel/**availability + conflict check**), Drive, Docs, Sheets, Contacts (with **explicit ambiguity confirmation**), Tasks, Google Chat |
| `discord.*` (10 ops) | List servers/channels/messages, search, send/reply/DM, file upload, reactions, threads |
| `voice.*` (11 ops) | Provider-agnostic telephony lifecycle: call/answer/hangup/speak/listen/transfer/schedule/cancel/retry/history/status |
| `meet.*` (7 ops) | Meet capability + create (via Calendar conferenceData); join/transcript/participate/leave/summary are gated on a configured transport and reported honestly |
| `openclaw.*` (5 ops) | OpenClaw status / agent_run / execute / channels / channel_send (the agent + gateway substrate) |
| `workflow_*` | Persistent workflow engine: sequential + parallel + conditions + approval + notify + retry, pause/resume/cancel, restart-safe |
| `operator_*` | Call management (schedule/queue/run-due/history/cancel), follow-up tasks, escalation, high-level natural-language orchestration (`operator_plan`/`operator_execute`) |
| `system_*` | capability / permission (+ set) / accounts / audit |

**87 auto-registered tools in total.**

---

## Quickstart

### 1. Offline — try the whole thing with no credentials

```bash
cd unified-operator
python -m pip install -e .
UNIFIED_OFFLINE=1 python examples/client_demo.py     # MCP *client* over stdio
```

`UNIFIED_OFFLINE=1` (or `python -m unified.main --offline`) runs every connector in
**deterministic mock mode** — same dispatch/audit/permission paths, output labelled
`"mode":"mock"`, so workflows, call queueing, retries and permissions can be exercised
safely. Run the verification suite:

```bash
UNIFIED_OFFLINE=1 python -m unittest tests.test_offline tests.test_acceptance -v
```

### 2. Add live credentials

Copy `.env.example` and fill in what you have. Configured connectors switch to `"live"`
automatically; unconfigured ones keep honest mock/offline behaviour per connector.
See [docs/setup.md](docs/setup.md).

### 3. Connect OpenCode (ONE connection)

```bash
python -m unified.main            # or: unified-operator-mcp
```

Register it in your MCP client registry. Sample config:

```json
{
  "mcpServers": {
    "unified-operator": {
      "command": "unified-operator-mcp",
      "env": { "UNIFIED_OFFLINE": "0" }
    }
  }
}
```

See [docs/operations.md](docs/operations.md) and the ready-made
[`examples/mcp-servers.json`](examples/mcp-servers.json). Point the client at ONE
`unified-operator-mcp` endpoint and the whole platform is a single operator.

---

## Point your agent here first

The agent should call **`system_capabilities`** before doing anything — it reports which
connectors are `configured` / in `mock`, and lists every operation per namespace. Then
`system_accounts` to pick identities, and `system_permission` to check what needs
authorisation.

Mutating/destructive operations carry explicit `authorized` + `reason` parameters and are
subject to the permission policy. See [docs/operations.md](docs/operations.md#permissions).

---

## Repository layout

```
unified-operator/
  pyproject.toml
  README.md
  docs/architecture.md setup.md operations.md cli.md acceptance.md known_limitations.md
  examples/client_demo.py            mcp-servers.json
  .env.example
  src/unified/
    config.py  errors.py  observability.py  accounts.py  permissions.py  state.py
    base.py    registry.py  server.py  main.py  __init__.py  __main__.py
    engines/  workflow.py  calls.py
    providers/ google.py discord_provider.py voice.py meet.py openclaw.py
  tests/ test_offline.py test_acceptance.py
```

More: [docs/architecture.md](docs/architecture.md).

---

## Honesty & limitations

- OpenClaw's realtime **app voice** (`talk.*`/`tts.*`) is *not* PSTN. Phone calling here
  goes through a documented provider contract (`VOICE_API_URL`) — see
  [docs/setup.md](docs/setup.md#voice--telephony). This is stated, not hidden.
- Meet **join/transcribe/participate** are only reported available when a configured
  transport is reachable; otherwise they raise `NotSupported` with the reason.
  `meet.create` (via Google Calendar) always works when Calendar is configured.
- Google/Discord/voice/OpenClaw adapters are code-complete against the real APIs but can
  only be exercised live once you supply credentials in this environment. All offline
  verification uses explicitly-flagged mock output.

Full list: [docs/known_limitations.md](docs/known_limitations.md).
