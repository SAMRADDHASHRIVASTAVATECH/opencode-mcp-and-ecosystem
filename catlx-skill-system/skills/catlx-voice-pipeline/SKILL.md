---
name: catlx-voice-pipeline
description: "Handles the CATLX voice-first interface: the 10-stage voice processing pipeline (wake word, audio capture, STT, context injection, NLU/intent, clarification, planning, execution, feedback, memory write), wake word configuration, the continuous conversational context window, and real-time streamed TTS. Use when the user asks about voice commands, wake words, speech-to-text, NLU intents, disambiguation, TTS, or how voice is the primary interface."
metadata:
  catlx: subsystem
  category: interface
  subsystem: Voice_Pipeline
  capability: voice-processing
  version: "1.0.0"
  source: "PART IV §4.1-4.6"
  aliases: "voice, speech, wake word, stt, tts, nlu, intent, voice-first, voice commands"
  depends-on: "catlx-ai-provider, catlx-memory, catlx-capability-routing"
---

# CATLX — Voice-First Pipeline

This skill owns the **voice interface**, which is the primary interaction model of CATLX — not a convenience
layer. Every capability is accessible by voice; the keyboard palette and GUI are derivations.

> Canonical detail: `../../knowledge/references/voice-pipeline.md` (+ detailed lifecycle in
> `../../knowledge/references/runtime-lifecycle.md` §18.2). Load on demand.

---

## Purpose

Convert a spoken command, end-to-end, into a completed action: wake word → capture → transcribe → enrich
with context → intent → disambiguate → plan → execute → speak → remember.

## When to activate

- User asks how CATLX hears/understands/speaks, or about STT/NLU/TTS/wake word.
- Configuring a custom wake word (Wake Word Studio).
- Debugging a voice command that failed misinterpretation or disambiguation.
- Designing a multi-utterance conversation flow.

## What this skill handles

1. **The 10-stage pipeline** (each stage an isolated module on typed message queues):
   Wake Word → Audio Capture → STT Transcription → Context Injection → NLU/Intent → Clarification →
   Planning → Execution → Feedback → Memory Write. (Stage table: `../../knowledge/references/voice-pipeline.md` §4.2.)
2. **Wake word configuration** — default `Hey CATLX`; custom via Wake Word Studio with 10–30 samples,
   compiled to a local ONNX model, fully on-device.
3. **Continuous context** — the Conversational Context Window (last N turns by tier, active app, last file,
   in-progress workflow). Injected into every NLU call, enabling pronoun resolution and implicit references.
4. **Real-time responses** — T1+: streamed TTS in parallel with workflow execution; T0: buffered TTS at
   completion to avoid CPU contention.
5. **Lifecycle** — detailed step sequence in `../../examples/voice-command-lifecycle.md` (wake word → memory write).

## Requirements / constraints

- **Voice-first mandate:** other interfaces are convenience alternatives derived from the voice pipeline.
- Tier-scaled STT/TTS from the CapabilityMap (`stt_engine`, `tts_engine`, `gui_mode`); see
  `catlx-hardware-adaptation`.
- **Least privilege (R5):** the NLU step sends the context-enriched transcript through the PAL; the plan is
  validated by the Permission Router before execution.

## Canonical knowledge it reads

`../../knowledge/references/voice-pipeline.md` · `../../knowledge/references/runtime-lifecycle.md` ·
`../../knowledge/references/hardware-adaptation.md`.

## Delegation

- **AI provider for STT/NLU/TTS** → delegate to `catlx-ai-provider`
  (`skill({ name: "catlx-ai-provider" })`). The PAL exposes `transcribe()`, `complete()`, `synthesize()`.
- **Executing the ExecutionPlan / running the DAG** → delegate to `catlx-workflow-engine`
  (`skill({ name: "catlx-workflow-engine" })`).
- **Writing the EpisodicRecord / memory context injection** → delegate to `catlx-memory`
  (`skill({ name: "catlx-memory" })`).
- **Choosing STT/TTS engine + fallback** → delegate to `catlx-capability-routing`
  (`skill({ name: "catlx-capability-routing" })`).
- **Speaking feedback / HUD** → delegate to `catlx-desktop-control` (HUD) /
  `catlx-electron-shell` as appropriate.

## Edge cases & warnings

- **Low confidence / ambiguity:** if `confidence < 0.75` or ambiguity flags set, ask a clarifying question
  and loop — do not guess.
- **T0 CPU contention:** do not stream TTS during execution; buffer it.
- **No cloud dependency:** the wake word and (T0) STT/TTS run locally.
- **Secure contexts:** when the pipeline might touch sensitive input, respect input-synthesis/secure-mode
  (`catlx-security`).

## Component lifecycle policy (reuse → install → adapt → create)

**NEVER create a new component as the default.** Before building/creating anything (a sub-skill, dependency,
reference, workflow, helper, adapter, or template), check, in order:
1. **Reuse** an existing local component (resolve aliases/equivalent capabilities first) — reuse, don't rebuild.
2. **Use** an already-registered component from the registry.
3. **Install** a suitable existing, trusted, supported component → validate → register → connect to the graph → use.
4. **Adapt** an existing compatible component via a small persistent adapter/wrapper instead of re-creating it.
5. **Create only as last resort** — then make it permanent immediately: stable id, canonical location, register,
   add to the capability index + dependency graph, add provenance, use, and allow future reuse.
6. Never reorganise/recreate already-generated components (no `Skill X 2` / `new` / `temp` variants); extend the
   existing one. Never create a second competing knowledge source; connect back to the canonical `knowledge/` layer.
   Promote any reusable artifact out of `/tmp`/scratch into the permanent ecosystem.

> Full policy: `../../knowledge/rules/component-lifecycle.md`.

## Source / provenance

- **Source:** PART IV §4.1–4.6 (voice as primary interface, pipeline, wake word config, continuous context,
  real-time responses, lifecycle). Detailed lifecycle mirrored in PART XVIII §18.2.
- **Inferred:** none beyond Windows adaptation of audio/tray interaction; pipeline stages preserved exactly.
