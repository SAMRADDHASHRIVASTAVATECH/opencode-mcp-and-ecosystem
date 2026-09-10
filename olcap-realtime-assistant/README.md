# OLCAP Realtime Assistant

`olcap-realtime-assistant` — a **real-time multimodal AI assistant** delivered as **one
unified MCP server** (`olcap-realtime-assistant-mcp`). It integrates alongside your
existing **OpenCode, OpenClaw, MCP servers, skills, local LM Studio models and OLCAP
Android tooling** — it does **not** replace any of them.

It is designed for low latency and continuous operation, with two explicit modes:

```
INTERVIEW / PRACTICE MODE        +        ALWAYS-ON WORKSPACE ASSISTANT
```

Default state is **OFF / INACTIVE**. Microphone and continuous screen monitoring are
**never silently activated** — activation is explicit.

> **Honesty rule (spec section 45):** No fake capabilities. If audio capture, screen
> capture, transcription, a model, or TTS is not available on the current host, the tool
> returns **`UNAVAILABLE` with the actual reason**. Nothing is simulated and reported as
> real.

---

## What it is

A single coordinating assistant that can *hear* permitted audio, *understand* speech,
*observe* permitted screen context, *maintain bounded context*, *reason* via local or
optional cloud models, *use MCP tools*, *speak*, *summarise*, and *remember the current
session* — recovering safely across restarts.

```
Screen / Audio / User Input
            ↓
     OLCAP Realtime Engine      (audio + screen + context)
            ↓
     Session + Context Layer    (persistent, bounded rolling memory)
            ↓
     AI Reasoning Layer         (LM Studio / OpenClaw / optional cloud, with fallback)
            ↓
       Tool / MCP Layer
            ↓
OpenCode / OpenClaw / External Services
```

## Primary architecture (shared by both modes)

```
                         USER
                           │
                           ▼
                    OPEN CODE / UI
                           │
                           ▼
                OLCAP REALTIME MCP
             ┌─────────────┼─────────────┐
             ▼             ▼             ▼
         Audio Engine  Screen Engine  Context Engine
             │             │             │
             ▼             ▼             ▼
            STT          Vision       Session State
             └─────────────┼─────────────┘
                           ▼
                    Reasoning Engine
              ┌────────────┼────────────┐
              ▼            ▼            ▼
          LM Studio     OpenClaw      Other MCPs
              └────────────┼────────────┘
                           ▼
                       Actions / Responses
                           ▼
                    Optional TTS
```

## MCP namespaces (66 tools)

* **assistant.** — `get_status`, `mode.get/set/interview/workspace/pause/resume`,
  `start/stop/pause/resume`, `health`, `diag`, `analyze`, `analyze_screen`,
  `analyze_voice`, `analyze_context`, `emergency_stop`, `release_emergency_stop`
* **audio.** — `list_devices`, `get_status`, `select_device`, `start/stop/pause/resume`,
  `test`, `health`
* **screen.** — `get_status`, `start/stop/pause/resume`, `get_current`,
  `get_active_window`, `get_changes`, `capture_region`, `health`
* **transcript.** — `get_live`, `get_recent`, `get_history`, `search`
* **practice.** — `analyze_question`, `generate_answer`, `generate_hint`,
  `evaluate_answer`, `analyze_code`, `generate_solution`, `explain_solution`
* **meeting.** — `summarize`, `extract_actions`, `extract_decisions`, `extract_questions`
* **session.** — `create`, `get`, `pause`, `resume`, `end`, `summarize`, `delete`,
  `export`, `list`
* **model.** — `list`, `get_status`, `set_provider`, `get_usage`

No unrestricted shell tool is exposed; workspace execution reuses existing approved
OpenCode/OLCAP tooling (spec section 19).

---

## Quickstart (control-plane, no hardware required)

```bash
cd olcap-realtime-assistant
python -m pip install -e .            # core (MCP + control plane)
python -m olcap_realtime.main --list-tools      # show the 66-tool manifest
python -m olcap_realtime.main --health          # honest availability report
python -m olcap_realtime.main --diag            # pipeline diagnostic
python examples/client_demo.py                  # end-to-end demo (stdio)
python -m unittest discover -s tests            # 25 offline tests
```

Optional extras for real capture/inference:

```bash
python -m pip install -e ".[audio,stt,screen]"
```

### Register with OpenCode / OpenClaw (additive)

Add the `examples/mcp-servers.json` entry to your **existing** MCP config under the name
`olcap-realtime-assistant-mcp`. Do not remove any current servers/skills.

---

## Layout

```
olcap-realtime-assistant/
  README.md  pyproject.toml
  config/assistant.example.json   .env.example
  examples/client_demo.py         mcp-servers.json
  src/olcap_realtime/
    config.py  errors.py  events.py  modes.py  security.py
    context.py  session.py  store.py  assistant.py  server.py  main.py
    engines/ audio.py  screen.py  stt.py  reasoning.py  tts.py
    practice.py                       # interview/coding/workspace/meeting
  tests/ test_core.py test_mcp.py
  docs/ architecture.md installation.md configuration.md mcp-opencode.md
        openclaw.md lmstudio.md whisper-stt.md tts.md modes-privacy.md
        screen-audio-permissions.md troubleshooting-diagnostics.md
        testing.md performance.md
```

Read [docs/architecture.md](docs/architecture.md) next.
