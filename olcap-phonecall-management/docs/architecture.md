# Architecture

## Layered design

```
Android Phone
   |
   |  (authoritative source of call state)
   v
+-- OLCAP Phone Service (android/) ---------------------+
|  CapabilityProbe        - real device capability check |
|  CallStateMonitor       - TelephonyManager call state  |
|  ForegroundService      - availability while permitted |
|  BridgeClient           - publish events/state         |
+--------------------------------------------------------+
   |  secure bridge (HTTP/WS, configurable URL + token)
   v
+-- Control plane + MCP (src/olcap) ---------------------+
|  PhoneManager           - single authority             |
|  CallMachine            - explicit call state machine  |
|  TelephonyBackend       - dial/answer/hangup/...       |
|  PolicyEngine           - autonomous incoming policy   |
|  SecurityManager        - authz / emergency stop / rl  |
|  Store (SQLite)         - history/policies/audit       |
|  RealtimeVoiceProvider  - AI-voice abstraction         |
|  OlcapServer            - MCP: phone.* tools           |
+--------------------------------------------------------+
   |  stdio / socket MCP
   v
OpenClaw  ->  OpenCode / other authorized clients
```

### Core idea

The **PhoneManager** is the single authority. Every `phone.*` tool is a thin wrapper over
it, so:

* account/device identity, permission, policy and audit are applied uniformly;
* the call-state machine is authoritative and records every transition;
* each call gets a unique `call_id` (never the bare number);
* unsupported operations raise structured errors rather than being faked.

### Backends (`TelephonyBackend`)

The call layer talks only to this interface: `dial / answer / reject / hangup / hold /
resume / mute / unmute / transfer / send_dtmf / get_state / start_audio / stop_audio` plus
device/sim introspection and `attach_call`. Backends:

* `SimulatedTelephonyBackend` — deterministic test/demo; clearly labelled `simulated`;
  models two SIMs; never claims real cellular audio.
* `AndroidBridgeBackend` — real device bridge; only reports capabilities the device probe
  returns; raises structured errors when the bridge is unconfigured/unreachable.
* (Pluggable: `ProviderTelephonyBackend`, `VoipBackend`, `OpenClawVoiceBackend` fit the
  same interface.)

### Voice providers (`RealtimeVoiceProvider`)

Provider-agnostic realtime AI voice: create session, stream transcript, barge-in / turn /
interruption semantics, cancellation, reconnect, graceful termination. `SimulatedRealtimeVoiceProvider`
exercises the AI-session lifecycle offline (flagged `simulated`). A real provider (OpenClaw
voice / a realtime provider / a local pipeline / provider telephony) implements the same
interface; **no real-time cellular audio is assumed**.

### Call state machine

```
IDLE ─ INCOMING_RINGING ─ CALL_ANSWERING ─ CALL_ACTIVE ─ AI_SESSION_STARTING
  │                                                    ─ AI_CONVERSATION_ACTIVE
  └─ OUTGOING_DIALING ─ OUTGOING_RINGING ─ CALL_ACTIVE ...
also: BUSY / REJECTED / MISSED / VOICEMAIL / TRANSFERRED / ON_HOLD /
      DISCONNECTED / FAILED / ERROR
```

Every transition is recorded on the call record (`call.transitions`), and terminal states
can't be re-animated. See `src/olcap/state_machine.py`.

### Events

An in-process `EventBus` publishes typed events (`incoming_call`, `outgoing_call`,
`ringing`, `answered`, `connected`, `disconnected`, `missed`, `rejected`, `voicemail`,
`transfer`, `ai_session_started/ended`, `transcription_update`, `state_changed`, ...).
Push-based, no aggressive polling; a realtime transport (WebSocket/SSE on Android) can
subscribe.

### Persistence

SQLite store (`OLCAP_STATE_DIR`, default `~/.olcap/olcap.db`): call records, policies,
audit. Survives service/process restarts.

### Config

`AppConfig` (`config/olcap.example.json` / `OLCAP_*` env) is the central model. Secrets
are only referenced by env/keystore key and redacted from every output.
