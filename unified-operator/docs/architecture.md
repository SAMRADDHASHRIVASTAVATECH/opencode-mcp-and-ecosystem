# Architecture

## High-level

```
OpenCode / any MCP client
        │  stdio JSON-RPC  (one connection: "unified-operator-mcp")
        ▼
┌─────────────────────────────────────────────────────────────┐
│ OperatorServer (MCP)  -- src/unified/server.py              │
│  • 87 tools auto-registered from each connector's Op table  │
│  • engine tools: workflow_* / operator_* / system_*          │
│  • uniform JSON results with ok / mode / account / operation │
└──────────────────────────────┬──────────────────────────────┘
                               │ Runtime.call(action,args,account,authorized,reason)
                               ▼
┌──────────────────────────────────────────────────────────────────┐
│ Runtime (registry.py) — single dispatcher                         │
│   account isolation (accounts.py)                                  │
│   permission gate  (permissions.py)  automatic/confirm/blocked     │
│   audit (observability.py)  request + action + outcome             │
│   connectors  google/discord/voice/meet/openclaw                    │
│   engines     WorkflowEngine, CallEngine (state.py persistence)    │
└──────────────────────────────────────────────────────────────────┘
```

### The core idea

Every operation across every platform is declared once in a connector's `OPS` table as an
`Op` with typed `Param`s, a permission `action` id and `mutating/destructive` flags. The
MCP server **auto-registers** one tool per op. A tool call always flows through
`Runtime.call`, so identity, permission and audit are uniform — no way to bypass them by
picking a "different" tool name.

```python
# base.py
Op(name, desc, params=[Param(name,type,required,desc,default)],
   action="", mutating=False, destructive=False)
```

Permission `action` id can be broadened so several ops share a policy
(e.g. all `gmail.reply/forward/send/draft` use `google.gmail.send`; calendar mutations use
`google.calendar.write`).

## Connectors (src/unified/providers)

Each implements `Connector`:
- `configured()` — is real-mode config present?
- `OPS` — the operation table.
- `op_<name>(args, account)` — live implementation.
- `simulate(op, args, account)` — optional richer offline output.

Mode is chosen at construction: `mock` if `UNIFIED_OFFLINE=1` **or** the connector isn't
configured; otherwise `live`. A small `ALWAYS_REAL` set lets pure-introspection ops
(`meet.capability`, `voice.status`) return meaningful output even in mock.

- **google.py** — official `googleapiclient`: Gmail, Calendar (+ `freebusy` availability),
  Drive, Docs, Sheets, People (Contacts), Tasks, Chat. Service-account or Desktop OAuth.
- **discord_provider.py** — real Discord HTTP API (`/api/v10`) with a bot token.
- **voice.py** — provider-agnostic HTTPS gateway. Live only when a provider is configured.
- **meet.py** — create via Calendar; join/transcribe/participate require a configured
  transport and otherwise raise `NotSupported` honestly.
- **openclaw.py** — drives the installed OpenClaw CLI/gateway: status, agent_run, execute,
  channels, channel_send. OpenClaw is the **agent/gateway substrate** of this operator.

## Engines

- **WorkflowEngine** (workflow.py): persistent definitions; sequential, `parallel`,
  `approval` (pause), `notify`, tool steps with optional `when` conditions + retries.
  State (step results, pointer, pending approval) is stored so a run can pause on approval
  and resume after a restart.
- **CallEngine** (calls.py): authoritative call records + a persistent outbound queue with
  due-time firing (`run_due`), retry/backoff up to `max_attempts`, follow-up task creation,
  and human escalation. Call lifecycle states are modelled explicitly
  (`queued…escalated`).

## Persistence & observability (state.py, observability.py)

A single SQLite DB (`UNIFIED_STATE_DIR`, default `~/.unified-operator/operator.db`) holds
`calls`, `call_queue`, `workflows`, `tasks`, `audit`. `OperatorLog` + `Audit` record every
dispatch with an id, account, action and outcome. Engines + audit survive restarts.

## Honesty control

Results are JSON like:

```json
{"ok": true, "platform": "google", "account": "default",
 "operation": "google.gmail.send", "mode": "mock",
 "result": {"simulated": true, ...}}
```

`mode` is always `mock` or `live` — callers can tell. Unsupported/unreachable transports
raise `NotSupported`/`NotConfigured` with a reason rather than fabricating output.
