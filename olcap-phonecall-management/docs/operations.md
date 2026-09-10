# Operations — MCP tool & CLI reference

## CLI

```bash
python -m olcap.main --list-tools     # print the phone.* tool manifest
python -m olcap.main --config config/olcap.example.json   # run MCP with a config file
olcap-phonecall-management            # run MCP (env-configured)
```

Environment: `OLCAP_*` (see `config/olcap.env.example`). `--list-tools` prints JSON for
config validation. The process is a stdio MCP server (no aggressive polling; events are
push-based).

## Device tools

* `phone.get_status` — online state, active calls, emergency-stop flag, voice mode.
* `phone.get_capabilities` — honest capability report (control vs. audio vs. AI voice).
* `phone.get_network_status` / `.get_sim_status` / `.get_default_sim` / `.list_sim_slots`.

## Call tools

* `phone.get_active_calls` / `.get_call_status(call_id)` / `.get_call_history(limit)`.
* `phone.place_call(destination, sim?, authorized=true, objective?)` — requires
  authorization or an authorizing policy.
* `phone.answer_call / reject_call / hangup_call / hold_call / resume_call / mute_call /
  unmute_call (call_id)`, `phone.send_dtmf(call_id, digits)`.
* All return `{"ok":true, "call_id": ..., "state": ...}` or a structured error.

## Caller information

* `phone.identify_caller(number)` → contact or null.
* `phone.lookup_contact(query)` → raises ambiguity error when a name maps to several
  contacts (never guess).
* `phone.get_contact_context(query)` → org/notes context (local, minimal).

## AI voice

* `phone.start_ai_voice_session(call_id, objective?, max_duration_seconds?)` → session id.
* `phone.get_live_transcript(session_id?/call_id?)`, `phone.get_call_transcript(call_id)`.
* `phone.get_call_summary(call_id)` → deterministic, factual summary (no fabricated
  content).
* `phone.set_call_objective(call_id, objective)` → keeps the agent on objective.
* `phone.stop_ai_voice_session(session_id)`.

## Policies

* `phone.create_call_policy(name, policy)` / `.update_call_policy(name, policy)` /
  `.delete_call_policy(name)` / `.list_call_policies()`.
* `phone.enable_auto_answer` / `.disable_auto_answer` — toggles, but individual calls
  still require a matching policy to act.

## System

* `phone.health` / `.version` / `.reconnect` / `.get_logs(limit)` / `.emergency_stop`.

## Account/audit model

Calls record `call_id`, direction, number, contact, SIM/subscription, backend,
timestamps, duration, state/outcome, AI session id, objective, transcript reference,
summary, actions, errors and policy used. No raw audio is stored unless recording is
explicitly enabled. Every dispatch is audited.
