# Operations

## Start with discovery

```
system_capabilities   -> per-namespace configured/mock + full op list, voice provider
system_accounts       -> identities per platform
system_permission     action="..."   -> effective policy
system_permission_set action="..." policy="confirmation_required|blocked|automatic"
system_audit          limit=...      -> recent dispatch audit
```

## Tool call shape

Every connector op is an auto-registered tool with this signature:

```
<nsp>.<op>(args = "{...JSON...}", account = "", authorized = false, reason = "")
```

- `args` — JSON string; the exact keys (with `*` = required) are listed in the tool
  description. Connector ops that take no args ignore it.
- `account` — which identity to act as (`google::work`, `discord::main`, `voice::...`).
  Empty = the platform default.
- `authorized` + `reason` — required signal for any action whose policy is
  `confirmation_required` (and never allowed for `blocked`).

Response (always JSON):

```json
{"ok": true, "platform":"google", "account":"default",
 "operation":"google.gmail.search", "mode":"mock|live", "result": {...}}
```

Non-connector tools are ordinary typed tools: `workflow_*`, `operator_*`, `system_*`.

## Permissions

Effective policy for an action = first match of:
1. account-scoped override `account:<id>:<action>`
2. global override `<action>`
3. blocked patterns → confirm patterns (from `UNIFIED_PERM_BLOCKED`/`UNIFIED_PERM_CONFIRM`,
   wildcard `action:*` supported)
4. default `UNIFIED_PERM_DEFAULT`.

`confirmation_required` → raises unless `authorized=true`. `blocked` → always raises.
Set per-action / per-account overrides at runtime with `system_permission_set`.

For a safer default in production set `UNIFIED_PERM_DEFAULT=confirmation_required` and
whitelist read ops as `automatic`:

```
UNIFIED_PERM_DEFAULT=confirmation_required
UNIFIED_PERM_CONFIRM=google.gmail.send:confirmation_required,voice.call:confirmation_required,google.calendar.write:confirmation_required
```

## Multi-step workflows (workflow_*)

`workflow_create(name, steps)` then `workflow_run(id)`. Step schema:

```json
{ "id":"s1", "tool":"google.calendar.create",
  "args": {"summary":"Review","start":"...","end":"..."}, "account":"google::work",
  "authorized":true, "reason":"per user request",
  "when":[{"key":"steps.find.result","exists":true}], "retries":2 }
```

Special steps:

| type | behaviour |
|---|---|
| `approval` | pauses the workflow (`waiting_approval`) until `workflow_resume(id, approved_step=...)` |
| `parallel` | runs nested steps, collecting each result |
| `notify` | `channel:"discord"|"gmail"`, `to`, `text` → routes to messaging via openclaw/google |
| `tool` (default) | dispatch through the registry (permission + audit applied) |

Step results are stored at `workflow.status().state.steps[<id>]` so later `when` gates can
dereference values (e.g. `steps.find.result.result.simulated`). Pause on approval and resume
after a restart are supported. `workflow.cancel` aborts; `workflow.list(status)` lists.

## Call management & follow-ups (operator_*)

- `operator_call_schedule(to, at, purpose, objective, priority, max_attempts)` → persistent
  queue entry (`queued`).
- `operator_call_run_due()` → fires every due queued call through `voice.call`, applies
  retry/backoff up to `max_attempts`, records outcome in call history, and creates a
  follow-up task when attempts are exhausted.
- `operator_call_queue`, `operator_call_cancel(queue_id)`, `operator_call_history(status)`
- `operator_followup(summary, due)` → creates an open task.
- `operator_tasks(status)` → list open/completed follow-ups.
- `operator_escalate(call_id, reason, destination)` → marks escalated, creates follow-up.

Call lifecycle (authoritative): `created → queued/scheduled → dialing → ringing →
answered → greeting → listening/speaking/processing/executing → … → completed`, with
`voicemail / busy / no_answer / failed` triggering retry, and `transferred / escalated` for
human handoff.

## High-level orchestration

`operator_plan` / `operator_execute(task)` decompose a natural-language job into a concrete,
ordered list of the exact tools to run and flag anything needing confirmation/credentials.
It does **not** blindly execute ambiguous jobs — for repeatable jobs use
`workflow_create` so every step is observable and approvable. For an inbound-call style
workflow see `workflow_example` (the Sarah acceptance template).

## Honesty guidelines for the agent

- Call `system_capabilities` first. Treat `"mode":"mock"` results as **simulated**, not real.
- If a `meet.*` join op says `NotSupported`, don't claim participation; you can still
  `meet.create` (via Calendar) and take notes.
- Voice calls only reach a human when a real provider is configured; otherwise you're in
  the queue engine's mock path.
- Never report success on a failed Gmail/Discord op — relay `"ok":false` + `error`.

## Account isolation

Accounts are resolved per platform (`google::work`, `google::home`, `discord::main`, …).
Default identities come from env (`GOOGLE_ACCOUNT`, `DISCORD_ACCOUNT`, `VOICE_AGENT_ID`).
Overrides and audit entries carry the resolved account so you can prove which identity did
what. No info is shared between concurrent calls on different accounts.
