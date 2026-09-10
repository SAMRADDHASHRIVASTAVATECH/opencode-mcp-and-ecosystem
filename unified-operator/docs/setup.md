# Setup & credentials

All secrets come from environment variables (or a credential file/keystore) — **never** from
code and never echoed back in MCP responses. See `.env.example`.

Quick truth-table:

| Connector | Live when | Else |
|---|---|---|
| google | a service-account or OAuth token is available | mock |
| discord | `DISCORD_TOKEN` set | mock |
| voice | `VOICE_PROVIDER=generic` **and** `VOICE_API_URL` (+reachable bridge) | mock |
| meet | create via Calendar; join/etc. only with a reachable transport | create mock; join=NotSupported |
| openclaw | binary/gateway reachable | mock |

## Google Workspace

Prefer a **service account** with domain-wide delegation enabled on your Google Workspace
(you must grant each needed scope to the service account in the Admin console).

```bash
export GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account.json
export GOOGLE_ACCOUNT=work          # human/account label used for isolation
```

**Desktop OAuth** (personal Gmail) alternative:

```bash
export GOOGLE_CLIENT_SECRETS=/path/to/client_secret.json
export GOOGLE_TOKEN_PATH=/path/to/token.json
export GOOGLE_SCOPES=...            # comma list (see .env.example)
```

The first live call performs the one-time consent flow. All read/write ops then run through
`googleapiclient`. Scopes gate what the operator may do — keep them minimal
(e.g. `gmail.modify`, `calendar`, `tasks`, not `gmail.settings` etc.).

## Discord

```bash
export DISCORD_TOKEN=your-bot-token
export DISCORD_ACCOUNT=main
```

Bot must have the needed intents/permissions on the target servers. The connector uses the
REST API: listing servers/channels, reading/searching messages, sending, replying, DMs,
file upload, reactions and threads. Where OpenClaw already manages a Discord session, prefer
`openclaw.channel_send` to reuse that session.

## Voice / telephony

Real **PSTN phone calling** is not something OpenClaw's app-voice does, so the operator uses
a pluggable provider. Implement (or point at) a gateway that speaks this small contract —
e.g. a Twilio/Asterisk/Custom bridge — then:

```bash
export VOICE_PROVIDER=generic
export VOICE_API_URL=https://your-bridge.example.com
export VOICE_API_KEY=...
export VOICE_AGENT_ID=business-number
export VOICE_DEFAULT_PHONE=+18005550199
```

Provider contract (JSON over HTTPS):

```
POST {VOICE_API_URL}/call   {action:"dial", call_id, to, objective?, from?} -> {status, call_id, ...}
POST {VOICE_API_URL}/call   {action:"answer|hangup|speak|listen|transfer|cancel|retry", call_id, ...}
```

`status` may be one of the engine's lifecycle states so outcomes normalise correctly:
`answered / completed / voicemail / no_answer / busy / failed / transferred / escalated`
(see `CallEngine.CALL_STATES`). Without a provider the operator runs the full call-state
engine against explicit mock output.

## Google Meet

- `meet.create` — creates a calendar event with conference data; works whenever Google
  Calendar is configured.
- `meet.join / transcript / participate / leave / summary` — only available when a **Meet
  transport** is reachable on the host (e.g. the OpenClaw Google Meet plugin + a browser +
  mic). `meet.capability` reports which modes are actually available. If none, these raise
  `NotSupported`. The operator will not claim to have joined/participated in a meeting it
  didn't.

## OpenClaw

The operator reuses the installed OpenClaw as its agent/gateway substrate (OpenClaw-first:
it inspects version/plugins/channels before falling back to custom adapters). Discovery
checks `OPENCLAW_BIN`, then `PATH`, then common home locations.

```bash
# (optional) force a specific binary/gateway
export OPENCLAW_BIN=/path/to/openclaw
export OPENCLAW_GATEWAY_URL=http://127.0.0.1
export OPENCLAW_GATEWAY_PORT=18789
export OPENCLAW_GATEWAY_TOKEN=...
```

`openclaw.status` shows what the installed OpenClaw exposes (version, channels, voice,
plugins). Reuse its auth/sessions/channels rather than duplicating credentials wherever
possible.
