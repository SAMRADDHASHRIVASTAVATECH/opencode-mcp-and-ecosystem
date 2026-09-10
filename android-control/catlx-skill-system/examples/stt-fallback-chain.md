# Example — Speech-to-Text Capability Fallback Chain

> Source: PART III §3.4.1. Preserved exactly. Used to show how Capability Routing resolves a capability
> request ("transcribe audio") when the best module is unavailable.

```
capability_request: transcribe audio
  -> Capability Router queries CapabilityMap[stt_engine]
  -> routes to best module; if unavailable, transparently falls back
```

| Priority | Engine |
|---|---|
| 1 (Best) | Whisper large-v3 on GPU |
| 2 | Whisper medium on CPU |
| 3 | Vosk large model |
| 4 | Vosk small model |
| 5 (Last resort) | Remote API (Google Speech / Groq Whisper) |

**Behavior:** If Whisper large-v3 requires a GPU that is currently under load, the router transparently
selects the next-best engine (Whisper medium on CPU, then Vosk large, ...). The user is never required to
pick an engine; the routing decision is automatic.
