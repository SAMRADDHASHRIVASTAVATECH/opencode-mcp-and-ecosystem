# Verification & acceptance

## 1. Automated (this repository, all green)

```bash
python -m unittest discover -s tests        # 28 tests
```

| Suite | Covers |
|---|---|
| `test_core.py` | state machine; inbound/outbound; answer/reject/hangup; DTMF; SIM selection; destination allowlist; authorization required; auto-answer only with policy; AI-session lifecycle; summary; emergency stop; remote token auth; **restart persistence**; ambiguous-contact handling |
| `test_mcp.py` | tool manifest (39 `phone.*`), honest capability report, place-call, emergency stop, structured errors |

`examples/client_demo.py` runs the full surface over MCP stdio end-to-end (simulated).

## 2. Live acceptance (requires real Android device + credentials)

These map to spec section 33. Mark them green **only after** performing them on-device.

1. **Builds** — `android/` opens in Android Studio and `:app:assembleDebug` succeeds
   (needs SDK + JDK 17).
2. **Installs** — APK installs and launches on the target phone.
3. **Background** — foreground service stays up within Android's permitted model.
4. **OpenClaw connects** to the control-plane MCP (`olcap-phonecall-management`).
5. **OpenCode discovers** the capabilities (`phone.get_capabilities`, tool list).
6. **Real call state reflected** — with `android_bridge`, `phone.get_status` shows the
   phone's actual active/ringing call.
7. **Incoming calls generate events** — on-device monitor → bridge → EventBus.
8. **Outgoing calls can be initiated** where Android permits (`phone.place_call`).
9. **Lifecycle tracked** through the explicit state machine (records + transitions).
10. **Multiple SIMs** handled where supported (probe reports `multi_sim`).
11. **AI voice sessions** created through a supported backend (real provider required for
    real audio).
12. **Unsupported cellular audio detected** — probe reports `false` for non-default-dialer
    apps; not faked.
13. **Autonomous answering** requires an explicit policy.
14. **Unique call id** per call.
15. **History & summaries** available (`phone.get_call_history` / `.get_call_summary`).
16. **Emergency stop** works and persists.
17. **Authentication/authorization** work (remote token mode + authorized calls).
18. **Tests** cover the core lifecycle (automated suite above).
19. **Docs explain Android/device limitations** (this docs set).
20. **No existing MCPs/skills/configs overwritten** (separate namespaced server).

## Safety checklist

- No stealth calling / spoofing / covert recording / interception logic present.
- AI callers identify themselves; recording/transcription configurable.
- Emergency stop halts autonomous activity and persists.
