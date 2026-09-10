# MCP, OpenCode & OpenClaw integration

## Register with OpenCode (additive — never overwrite)

Append one entry to your **existing** MCP config:

```jsonc
{
  "mcpServers": {
    // ...your existing servers stay...
    "olcap-realtime-assistant-mcp": {
      "command": "olcap-realtime-assistant-mcp",
      "env": {
        "LM_STUDIO_ENDPOINT": "http://127.0.0.1:1234/v1",
        "OLCAP_STT_PROVIDER": "faster_whisper",
        "OLCAP_SCREEN_MONITORING": "false",
        "OLCAP_CLOUD_PROCESSING": "false"
      }
    }
  }
}
```

See `examples/mcp-servers.json`. This project does not modify, delete, or shadow any
existing MCP, skill, plugin, provider, tool, instruction, or model configuration.

## OpenClaw

OpenClaw is treated as an existing orchestration layer. This assistant does **not**
duplicate OpenClaw's model/voice/MCP infrastructure:

* Reuses OpenClaw's configured model infra via `OpenClawReasoningProvider` when an
  OpenClaw client hook is injected (spec 20). Additive.
* Can be a fallback reasoning provider (`reasoning.fallbacks: ["openclaw"]`).
* Reuses OpenClaw's MCP capabilities and authentication rather than re-implementing.
* The assistant is itself an MCP tool provider that OpenClaw can drive.

## Tool routing (spec 31)

Meaningful requests detected from voice/screen can trigger existing MCP tools (e.g. an
OpenCode/OpenClaw MCP `workspace` inspection) — but only with authorisation appropriate to
the action. There is no unrestricted `execute_any_command`.

## Agent guidance

Discover first: `assistant.health` / `assistant.diag` report exactly which capabilities
are available on this host. Use `assistant.analyze_context` to inspect the active session.
`assistant.emergency_stop` halts everything instantly.

## Android

The assistant may drive the existing OLCAP Android control MCP for input/audio where
needed — it does not rebuild the Android controller, ADB infra, web protocol, device auth,
or existing Android tools (spec 42).
