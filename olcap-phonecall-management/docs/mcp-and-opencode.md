# MCP & OpenClaw / OpenCode integration

## One server, one operator

Register a **single** MCP server, `olcap-phonecall-management`. All capabilities surface
as structured `phone.*` tools. OpenClaw is the orchestration/agent layer on top; it does
not need to touch Android telephony APIs itself.

```jsonc
// examples/mcp-servers.json
{
  "mcpServers": {
    "olcap-phonecall-management": {
      "command": "olcap-phonecall-management",
      "env": {
        "OLCAP_BACKEND": "simulated",     // or android_bridge for the real phone
        "OLCAP_AI_CALLS_ENABLED": "false",
        "OLCAP_AUTO_ANSWER_ENABLED": "false"
      }
    }
  }
}
```

Install the console script (`pip install -e .` → `olcap-phonecall-management`) or run
`python -m olcap.main`.

## Agent-facing workflow guidance

1. **Discover first.** `phone.get_capabilities` tells the agent exactly what this device
   can do (control vs. audio, voice mode). Treat `simulated`/`false` honestly.
2. **Check state.** `phone.get_status` → active calls & mode; `phone.get_call_history` →
   what happened.
3. **Call only with authorization.** `phone.place_call(destination, authorized=true,
   sim?, objective?)`. Do not auto-call a number just because it appears in a task.
4. **Autonomous inbound** only via explicit policies (`phone.create_call_policy`), never
   assumed.
5. **AI calls**: start an AI session on an active call with an objective
   (`phone.start_ai_voice_session(call_id, objective, ...)`), stream/read the transcript,
   then `phone.get_call_summary`.
6. **Emergency stop** is one call away (`phone.emergency_stop`) and persists.

## OpenClaw integration approach

* OpenClaw treats the OLCAP MCP as a normal MCP tool provider (subscribes to its `phone.*`
  tools). No duplication of OLCAP's Android/state logic.
* Where OpenClaw already has production infrastructure for a function (e.g. realtime
  voice), integrate with it via the `RealtimeVoiceProvider` / `OpenClawVoiceBackend` seam
  rather than reimplementing it.
* Events are available through the EventBus; connect a realtime transport (WS/SSE) to push
  `state_changed`, `incoming_call`, `ai_session_*`, etc. to OpenClaw instead of polling.

## Not overwriting existing integrations

This module adds a separate, namespaced `phone.*` MCP server under its own name. It does
not overwrite any existing OpenClaw/OpenCode MCPs, skills, configurations or
integrations — add it as an additional `mcpServers` entry.
