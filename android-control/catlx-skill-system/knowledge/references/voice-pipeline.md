# Voice-First AI OS — Canonical Reference

> Source: PART IV — VOICE-FIRST AI OS. The single authoritative source for the voice processing
> pipeline, wake word configuration, continuous context, real-time responses, and the voice command
> lifecycle.

## 4.1 Voice as the Primary Interface

Every capability in CATLX is accessible by voice. The voice pipeline is **not** a convenience layer — it
is the primary interaction model from which all other interfaces (keyboard, GUI, API) are derived. The
keyboard command palette and GUI controls exist as convenience alternatives to voice, not the other way
around.

## 4.2 Voice Processing Pipeline

A multi-stage processing chain. Each stage is an isolated module connected by typed message queues.
Stages are individually replaceable and independently benchmarked.

| Stage | Component | Description |
|---|---|---|
| 1. Wake Word | OpenWakeWord / Porcupine | Continuous low-CPU audio monitoring; triggers on configured keyword (default `Hey CATLX`); 1–3% CPU on T0 |
| 2. Audio Capture | PortAudio ring buffer | Captures voice segment from wake word onset to end-of-utterance (via VAD) |
| 3. STT Transcription | Vosk / Whisper (tier-scaled) | Converts audio to text. T0: Vosk tiny; T1: Vosk large; T2+: Whisper large-v3 |
| 4. Context Injection | Context Manager | Prepends current workspace context, recent history, active task state to the raw transcript |
| 5. NLU / Intent | Intent Parser (LLM-backed) | Sends context-enriched transcript to AI provider; returns structured IntentObject |
| 6. Clarification | Disambiguation Engine | If confidence < threshold or ambiguity flags set, generates a clarifying question; TTS speaks it; loop until confirmed |
| 7. Planning | Workflow Planner | Converts IntentObject to an ExecutionPlan (DAG of atomic steps with resource requirements, estimated duration, fallbacks) |
| 8. Execution | Workflow Engine | Executes the plan; each step calls the appropriate module |
| 9. Feedback | TTS + HUD | Speaks progress and final result; renders status on the HUD overlay |
| 10. Memory Write | Memory Broker | Writes the completed interaction to episodic memory with full provenance |

## 4.3 Wake Word Configuration

Default wake word model `Hey CATLX`; custom wake words trained via the **Wake Word Studio** in settings
using 10–30 user-recorded samples, compiled to a local ONNX model that runs entirely on-device with no
cloud dependency.

## 4.4 Continuous Context

CATLX maintains a **Conversational Context Window** that persists across individual voice commands. It
remembers the last N turns (N by hardware tier), the current active application, the last file operated
on, and the state of any in-progress workflow. Injected into every NLU call, enabling pronoun resolution
("run that again"), implicit object references ("what was the last thing I asked you to download?"), and
multi-step workflows spanning several utterances.

## 4.5 Real-Time Voice Responses

On **T1+** hardware CATLX streams TTS output in parallel with workflow execution — the user hears
confirmation of each step as it completes rather than waiting for the whole workflow. On **T0** hardware
TTS is buffered and played at completion to avoid CPU contention with execution.

## 4.6 Voice Command Lifecycle

1. Microphone stream → Wake Word Detector (continuous 24/7 monitoring)
2. Wake word matched → Audio Capture segment begins
3. End of utterance detected → Audio segment closed
4. Audio segment → STT Transcriber → raw transcript
5. Raw transcript + Context → NLU Intent Parser → IntentObject
6. IntentObject confidence check → Disambiguation if needed
7. Confirmed intent → Workflow Planner → ExecutionPlan (DAG)
8. ExecutionPlan → Workflow Engine → step-by-step execution
9. Each step result → TTS feedback + HUD update (streamed, T1+)
10. Workflow complete → Memory Broker writes episodic record
11. System returns to wake word monitoring state

## Cross-references
- Consumed by: `skills/catlx-voice-pipeline/SKILL.md`.
- Delegates to: `catlx-workflow-engine`, `catlx-desktop-control`, `catlx-memory`, `catlx-ai-provider`.
- Detailed lifecycle: `knowledge/references/runtime-lifecycle.md` (§18.2).
