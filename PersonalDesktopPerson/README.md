# Personal Desktop Person for OpenCode

A runnable persistent cognitive runtime based on the supplied architecture PDF. It maintains identity, deterministic affect-like state, goals, intentions, approvals, local SQLite memory, dialogue through a configurable local/remote model, and a live local avatar. OpenCode orchestrates work; an external computer-use MCP performs approved GUI interaction.

## Install
Windows PowerShell: `./install.ps1`. macOS/Linux: `./install.sh`. Then import `opencode.jsonc` into your OpenCode configuration and replace absolute paths. Restart OpenCode and call `personal_desktop_person_start_person` (the displayed prefix depends on OpenCode).

The installer does not download models. Configure any OpenAI-compatible local endpoint in `config/default.json`, such as Ollama, llama.cpp, or LM Studio. Keep `provider_url` empty to run cognition/memory without generated dialogue.

## Computer control
The included OpenCode template registers Qwen's cross-platform `open-computer-use` MCP command separately. Install it only after reviewing its source and permissions: `npm install -g @qwen-code/open-computer-use`. The person runtime never bypasses conservative approval; approved actions return a delegation envelope that OpenCode routes to that MCP. You may substitute another audited computer-use MCP by changing `computer_use_server`.

## Avatar
After `start_person`, open `http://127.0.0.1:8765`. It visualizes actual state and activity. It is an interface, not the cognitive process. It binds to loopback only.

## Data
`runtime/person.db` contains local memories; `runtime/identity.json` contains the editable identity. Screens and audio are not captured by this package. Back up/export the runtime directory if desired. Delete it to erase the person data after stopping the server.

## Limits
This is a complete runnable foundation, not consciousness and not a universal game player. OpenCode must remain connected for tool orchestration. Physical computer control depends on the separately installed platform MCP and OS permissions. A model cannot safely invent or execute arbitrary skills. Voice recognition/TTS, native transparent overlays, sophisticated reflection consolidation, and game-specific controllers are extension modules rather than falsely simulated features.

## PADP 2.1 complete runtime services
Version 2 adds the typed priority event bus, six-rate logical runtime (synchronous safety path plus environment events, cognition, tasks, on-demand deliberation and reflection), provenance-aware world beliefs, attention routing, motivations, strategy utility, persistent tasks/plans, HMAC-scoped expiring capabilities, append-only chained audit, source-grounded reflection, explicit feedback learning, reviewed skill registry, simulator, migrations, integrity checks, backup/restore, daemon supervisor commands, and 47 MCP tools.

The existing AI is OpenCode itself; no OpenCode engine source exists in this workspace. `cognitive_context` supplies identity/state/drives/world/memory to that intelligence, and OpenCode returns structured plans through PADP tools. Optional direct model endpoints handle dialogue/reflection without replacing the one persistent identity.

### Operations
```bash
pdp initialize
pdp doctor
pdp start
pdp status
pdp backup padp-backup.zip
pdp stop
pdp restart
pdp repair
pdp restore padp-backup.zip --force
pdp delete-data --yes
```

### Demonstrate the cognitive feedback loop
```bash
python -m personal_desktop_person.simulator
pytest -q
```


## True user and desktop reactivity
`interact` classifies every typed/transcribed utterance with the configured model (heuristic fallback), then enters it into the persistent event loop as conversation, information, task, feedback, direct address, or interruption. Consent-gated `DesktopWatcher` observes active application/window/cursor metadata, optional Windows UI Automation summaries, and optional local downsampled changed-region ratios. Pixels are not retained or blindly sent to a model. Meaningful attended events can invoke rate-limited semantic interpretation and feed the same world/appraisal/affect/intention/memory path. Enable each sensor explicitly in configuration.
