# Known limitations & honesty contract

These are intentional, not bugs — the operator reports only what real services/OpenClaw can
do and never fabricates capability or success.

## OpenClaw app-voice ≠ PSTN
OpenClaw's realtime `talk.*` / `tts.*` is in-app voice, **not** phone calling. The operator
makes phone calls only through a configured provider contract (`VOICE_API_URL`). Nothing in
the operator presents app-voice as making PSTN calls. Without a provider, the call engine
runs on explicitly-flagged mock output.

## Google Meet participation
`meet.create` works via Google Calendar whenever Calendar is configured. But
`meet.join / transcript / participate / leave / summary` are only real when a **Meet
transport** is reachable on the host (OpenClaw Google Meet plugin + browser + mic). If none
is reachable these raise `NotSupported` with the reason; `meet.capability` always tells you
the truth. The operator will not claim to have joined/participated in a meeting it did not.

## Offline / mock mode is explicit
When `UNIFIED_OFFLINE=1` or a connector has no credentials, that connector returns
`"mode":"mock"` with clearly-flagged simulated output. This is ideal for deterministic tests
and demos, but is not a substitute for real integrations. Agents must not present mock
results as live.

## Credentialed live adapters here are validated offline only
The Google/Discord/voice/OpenClaw adapters are code-complete against the official APIs but
could not be exercised against live accounts in this offline environment (no credentials
present). They should be smoke-tested once you supply env creds, per docs/acceptance.md.

## Google Docs / Sheets live code paths
Reads use Drive `export`; writes use `docs.documents.batchUpdate` / `sheets.values` — coded
against the official APIs and offline-validated at the contract level, not run live here.

## Scope of people/contacts matching
`google.contacts.resolve` returns a single unique match; on ambiguity it returns candidates
and requires explicit confirmation — it never sends to the wrong target on its own.

## Concurrency & scheduling
`run_due` must be invoked to fire queued calls (a scheduler/loop or the agent calling
`operator_call_run_due`). By default only one outbound call is dialled at a time
(`UNIFIED_ALLOW_CONCURRENT_CALLS`); info is never shared between concurrent calls.

## Windows
Pure-Python + stdio; works on Windows 10/11. Path env defaults (`~/.unified-operator`) and
the `httpx`/`googleapiclient`/`discord` deps are cross-platform.
