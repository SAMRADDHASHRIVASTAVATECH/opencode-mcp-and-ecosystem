# Security & call policies

This system controls a real phone, so security is mandatory and layered.

## Authentication & authorization

* **Local-only mode** (default): `OLCAP_REMOTE_ACCESS=false`. The on-device operator is
  trusted; no token required. OpenClaw/OpenCode on the same host runs locally.
* **Remote mode**: set `OLCAP_REMOTE_ACCESS=true` and `OLCAP_MCP_TOKEN=<secret>` (from
  env / secure storage). Every sensitive call is checked against the token with a
  constant-time compare. `SecurityManager.require_authorized()` gates these operations.
* **Emergency stop**: `phone.emergency_stop` (or the in-app button) engages an emergency
  stop that hangs up active calls, blocks all autonomous calling and persists the stop
  across restarts. Release requires an operator action.
* **Rate limiting**: outbound calls are throttled (configurable per-minute limit).
* **Audit logging**: every dispatch is recorded (`phone.get_logs`). Secrets are never
  written.

## Destination / caller allowlists & denylists

E.164 allow/deny lists (`OLCAP_DEST_ALLOW`, `OLCAP_DEST_DENY`, `OLCAP_CALLER_ALLOW`,
`OLCAP_CALLER_DENY`):

* A number not in the allowlist (when one is set) cannot be called →
  `DESTINATION_NOT_ALLOWED`.
* A number in the denylist is always blocked.
* Caller identity is resolved before deciding how to handle an inbound call.

## Calling requires authorization

OpenCode must **not** automatically place a call just because a number appears in a task.
`phone.place_call` requires `authorized=true` **unless** a user-created policy authorizes
that caller/destination. This is enforced in `PhoneManager.place_call`.

## Autonomous incoming-call policies

Policies are explicit and inspectable (`phone.list_call_policies`). An inbound call is
**never** auto-answered unless a matching, enabled policy authorizes it. Policy shape:

```json
{
  "name": "AI Assistant Calls",
  "enabled": true,
  "callers": ["allowlisted"],      // or a specific number/name, "all", "denylisted", "unknown"
  "action": "ai_answer",           // notify|ring_normal|reject|silence|auto_answer|ai_answer|...
  "hours": "09:00-18:00"
}
```

Evaluation is fully local (`PolicyEngine`). If the matched action needs an unavailable
capability (e.g. `ai_answer` with no voice provider), the system degrades to a notified
fallback and reports an `AI_PROVIDER_UNAVAILABLE` event rather than faking an AI answer.

## Enforcement summary

| Need | Control |
|---|---|
| Place call | authorized=true **or** authorizing policy; allowlist; not emergency-stopped; not rate-limited |
| Auto-answer / AI-answer | matching enabled policy only |
| Emergency stop | `phone.emergency_stop`, persisted |
| Remote access | token check + `remote_access=true` |
| Audit | every action recorded with actor/action/detail |
