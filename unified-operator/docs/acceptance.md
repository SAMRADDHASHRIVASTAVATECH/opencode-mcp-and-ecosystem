# Verification & acceptance

Two layers of verification ship with the project.

## 1. Automated (offline/deterministic)

The whole dispatch/audit/permission/engine stack runs in mock mode against the real
`Runtime` and engines. Output is explicitly flagged simulated — these tests prove the
**machinery** works (routing, persistence, permission gating, approval pauses, call
queueing, retry), not that a live Gmail account was touched.

```bash
UNIFIED_OFFLINE=1 python -m unittest tests.test_offline tests.test_acceptance -v
```

| Suite | Checks |
|---|---|
| `test_offline.py` | namespace coverage (>60 tools), capability report, google/discord/voice/meet mocks, workflow lifecycle + approval pause/resume + restart recovery, call schedule→queue→run, follow-up/tasks, permission gating |
| `test_acceptance.py` | the three end-to-end acceptance flows below |

## 2. Live acceptance (requires real credentials)

Re-run the same flows with credentials configured (no `UNIFIED_OFFLINE`) and assert real
side effects. Provide a real number + a throwaway Gmail/Discord when doing this.

### Flow A — Sarah: call & confirm Friday meeting (consent-first)
1. `system_capabilities` → confirm voice + google live.
2. Agent calls Sarah (or `voice.schedule` for a real callback) to ask whether she can attend
   Friday's meeting.
3. On her **verbal consent**, the operator runs the `workflow_example` acceptance workflow:
   approval → `google.calendar.create` (Friday slot) → `google.gmail.send` confirmation →
   `notify` to Discord.
4. If Sarah declines, the workflow is cancelled and **no** calendar/email is created.
   *(Automated offline form: `test_friday_consent_workflow`, `test_consent_not_given_halts`.)*

### Flow B — Gmail urgent → phone triage
1. `google.gmail.search` for urgent/unread.
2. Read the message, decide triage, get human approval for the reply.
3. Create a follow-up task and reply in-thread.
4. Prove the write ops are permission-gated by denying an unauthorized send.
   *(Automated offline form: `test_triage_workflow_and_permission_gating`,
   `test_schedule_then_escalate_call`.)*

### Flow C — Join a Google Meet → notes → tasks → summary → Discord
1. `meet.capability` (honest transport report).
2. With a real Meet transport: `meet.join` → take notes (`google.docs.create`) →
   `google.tasks.create` for action items → `meet.summary` → `notify`/`discord.send` to
   `#design`. Without a transport the join op must raise `NotSupported`, and `meet.create`
   (via Calendar) is still verified.
   *(Automated offline form: `test_meet_flow`, `test_meet_join_not_claiming_live_without_transport`.)*

## Manual smoke checklist (once creds are set)

- [ ] `system_capabilities` shows google/discord/voice configured and `"mode":"live"`.
- [ ] `google.gmail.send` to a throwaway inbox arrives (mode live, no `simulated`).
- [ ] `google.calendar.create` returns an event id and `freebusy` reflects it.
- [ ] `discord.send` posts to a test channel.
- [ ] `voice.call` to a real test number places the call (with a real provider).
- [ ] `meet.join` reports correctly for your transport state (works or `NotSupported`).
- [ ] `openclaw.status` reflects the installed OpenClaw.
- [ ] Restart the process; `operator_call_queue` and `workflow_status` still show prior
      entries (SQLite persistence).
