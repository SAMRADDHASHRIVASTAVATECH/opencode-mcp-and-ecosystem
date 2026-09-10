# Example — Voice Command Lifecycle (Detailed)

> Source: PART IV §4.6 / PART XVIII §18.2. Preserved exactly as a runnable conceptual sequence.

```
1.  Wake word matched → Audio Capture begins recording
2.  VAD monitors for end-of-utterance silence (default 800 ms)
3.  Audio segment closed and passed to STT Transcriber
4.  STT returns raw text transcript (200 ms–2 s depending on engine/hardware)
5.  Context Manager assembles context window: last 10 turns + active workspace + knowledge graph neighborhood
6.  Context + transcript sent to NLU Intent Parser via Provider Abstraction Layer
7.  NLU returns IntentObject {action_type, entities, confidence, ambiguity_flags, suggested_plan}
8.  If confidence < 0.75 or ambiguity_flags set → Disambiguation Engine asks a clarifying question; TTS speaks it; loop
9.  Confirmed intent passed to Workflow Planner
10. Workflow Planner generates ExecutionPlan (DAG) from intent + available modules + CapabilityMap
11. ExecutionPlan validated by Permission Router (capability check for each step)
12. DAG Executor begins execution; parallel steps dispatched to thread pool
13. Each completed step: checkpoint written; TTS announces progress (T1+); HUD updated
14. All steps complete: TTS speaks final result; HUD shows completion banner
15. Memory Broker writes EpisodicRecord with full provenance metadata
16. Voice pipeline returns to wake-word monitoring state
```
