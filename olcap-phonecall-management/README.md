# OLCAP Phone Call Management

**`olcap-phonecall-management`** — a unified, always-available phone-call management
layer for an Android phone, exposed to **OpenClaw / OpenCode** through one secure,
structured **MCP** interface.

This is **not merely a dialer**. It manages the complete lifecycle of phone calls
end-to-end and exposes that to an agent, while remaining **honest about what Android and
your carrier actually permit** — it never claims it can do something (e.g. capture or
inject cellular call audio) unless the device genuinely supports it.

---

## What it answers

* *What's happening with my phone calls?*
* *Who is calling?*
* *Can I answer? / Can I call this person? / Which SIM should I use?*
* *Can this device provide realtime call audio?*
* *Can the AI conduct this call?*
* *What happened during the call? What should happen next?*

---

## Two cooperating parts

| Part | Location | Role |
|---|---|---|
| **Android app (authoritative device source)** | `android/` | Foreground service, call-state monitoring, **real capability probe**, contacts, per-call state, bridge to the control plane. |
| **Control plane + MCP server** | `src/olcap/` | One MCP server (`olcap-phonecall-management`) exposing structured `phone.*` tools; owns the call-state machine, policy engine, security, history store and AI-voice session abstraction. |

OpenClaw/OpenCode talk to the **control plane MCP**. The Android component is the
authoritative source for phone state; the agent never manipulates telephony APIs directly.

> The control plane is fully implemented and **tested here** (28 tests) using a clearly
> labelled **simulated telephony backend**. The Android app ships as a Gradle project
> ready to open in Android Studio. See [`docs/android.md`](docs/android.md) for the honest
> note about what was and was not compiled in this environment (no Android SDK/device is
> present here).

---

## Feature surface (MCP tools — 43 `phone.*` tools)

* **Device:** `phone.get_status`, `.get_capabilities`, `.get_network_status`,
  `.get_sim_status`, `.get_default_sim`, `.list_sim_slots`
* **Calls:** `.get_active_calls`, `.get_call_status`, `.get_call_history`, `.place_call`,
  `.answer_call`, `.reject_call`, `.hangup_call`, `.hold_call`, `.resume_call`,
  `.mute_call`, `.unmute_call`, `.send_dtmf`
* **Caller info:** `.identify_caller`, `.lookup_contact`, `.get_contact_context`
* **AI voice:** `.start_ai_voice_session`, `.stop_ai_voice_session`,
  `.get_ai_voice_session`, `.set_call_objective`, `.get_live_transcript`,
  `.get_call_transcript`, `.get_call_summary`, `.list_speaking_styles`,
  `.get_call_conduct`, `.list_languages` (India's 22 scheduled + major world),
  `.detect_language`
* **Policies:** `.list_call_policies`, `.create_call_policy`, `.update_call_policy`,
  `.delete_call_policy`, `.enable_auto_answer`, `.disable_auto_answer`
* **System:** `.health`, `.version`, `.reconnect`, `.get_logs`, `.emergency_stop`

Each MCP tool reflects the *capabilities the device reports*. **No arbitrary shell
execution is exposed.**

---

## Quickstart (control plane, offline / simulated)

```bash
cd olcap-phonecall-management
python -m pip install -e .
python -m olcap.main --list-tools            # show the phone.* manifest
python examples/client_demo.py               # end-to-end MCP client demo (simulated)
```

Run the full verification suite:

```bash
python -m unittest discover -s tests          # 28 tests
```

To register with OpenCode, add the `examples/mcp-servers.json` entry (one server =
one operator). See [`docs/mcp-and-opencode.md`](docs/mcp-and-opencode.md).

---

## Honesty model (the part that must not be faked)

The system distinguishes these capabilities and reports each truthfully via
`phone.get_capabilities`:

1. **SIM-native / Android call-state monitoring** — real, with `READ_PHONE_STATE`.
2. **Call control (dial/answer/reject/hangup)** — real where the device permits.
3. **Cellular call-audio capture/injection** — *normally **not** available* to ordinary
   apps. `CALL_PHONE` does **not** grant audio. Only default-dialer apps on Android 10+
   can request telecom call audio. This is probed, never assumed.
4. **Provider-based telephony** — via a pluggable `TelephonyBackend` / voice provider.
5. **VoIP / internet calling** — via a pluggable backend.
6. **AI voice** — a realtime `RealtimeVoiceProvider` abstraction; **no audio path is
   assumed** for cellular calls.

If an operation can't be done on the current device it returns a structured code such as
`UNSUPPORTED_ON_THIS_DEVICE`, `CALL_AUDIO_UNAVAILABLE`, `CAPABILITY_UNSUPPORTED`, or
`ANDROID_PERMISSION_DENIED` — with the supported alternative — rather than pretending.

See [`docs/capabilities-and-limitations.md`](docs/capabilities-and-limitations.md).

---

## Layout

```
olcap-phonecall-management/
  README.md
  pyproject.toml
  config/olcap.example.json        olcap.env.example
  examples/client_demo.py          mcp-servers.json
  src/olcap/
    config.py  model.py  state_machine.py  telephony.py
    manager.py policy.py contacts.py security.py store.py events.py voice.py
    errors.py  server.py  main.py  __init__.py  __main__.py
    backends/ simulated.py  android_bridge.py
  docs/ architecture.md capabilities-and-limitations.md android.md security.md
        mcp-and-opencode.md acceptance.md operations.md
  tests/ test_core.py test_mcp.py
  android/  (Gradle app module)
```

Read [`docs/architecture.md`](docs/architecture.md) next.
