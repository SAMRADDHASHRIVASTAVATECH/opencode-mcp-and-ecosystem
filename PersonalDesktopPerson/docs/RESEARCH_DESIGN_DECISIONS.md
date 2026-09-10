# Research-to-design mapping
- Generative Agents: adopt event memory, retrieval and source-grounded reflection; reject free-form memory as fact.
- ACT-R/Soar: adopt explicit working/declarative/procedural separation and deterministic module status.
- Voyager: adopt versioned temporally extended skill manifests and verification before promotion; reject auto-executing generated code.
- Reflexion: use failure summaries to force strategy change; do not treat verbal reflection as ground truth.
- Hierarchical RL/options/SEADS: reserve learned local policies for repeated measurable domains; symbolic task layer selects skills. No online gradient learning is enabled by default.
- GUI-agent surveys: accessibility/structured interfaces before pixels; local controller below LLM.
- 2026 agent-memory security survey: write-time provenance, trusted-source flags, corrections, deletion and no authority from retrieved content.
- MCP 2026-07-28: use MCP as supervisory surface, not event bus. Sampling is deprecated in the current spec, so the existing OpenCode intelligence is integrated through tool calls and a provider-neutral model endpoint rather than a brittle server-initiated sampling dependency.
- SQLite WAL: selected for single-user local durability, transactions, backup API, FTS and migrations.
- Contextual bandit feedback: implemented as bounded strategy success estimates. Full RL is intentionally not run across unrestricted desktop actions because rewards are sparse, safety-sensitive and nonstationary.

The workspace contains PADP source plus the architecture PDF, but no inspectable source for OpenCode's internal AI agent. Integration therefore uses the supported MCP boundary: OpenCode remains the reasoning orchestrator, while PADP owns persistent cognition/state. This is not replaced with a second generic brain.

## Desktop companion research additions
Desktop Mate demonstrates convincing presence through window-edge placement, cursor chasing, direct touch/drag reactions, alarms and high-quality animation, but not a complete cognitive architecture. NekoAI demonstrates Tauri/Rust portability, window reactivity, multiple provider support, persistent mood/memory and local model support. Clawd Pet demonstrates scheduled screen-awareness and voice/chat but its periodic screenshot-to-model pattern is too privacy/cost heavy as a default. MiniCPM Desk Pet demonstrates guided local-model setup and coding-agent state reactions. Clicky demonstrates push-to-talk, cursor-following embodiment, multi-monitor/DPI care and explicit processing/speaking states. Open-LLM-VTuber demonstrates interruptible voice and Live2D state mapping.

PADP adopts their embodiment/event patterns while rejecting continuous screenshot upload, pet-local duplicate memory, scripted mood as the authority, and avatar-owned actions. OS metadata and accessibility are primary; changed-region sampling gates optional vision; semantic model calls are event/attention-triggered and rate limited.
