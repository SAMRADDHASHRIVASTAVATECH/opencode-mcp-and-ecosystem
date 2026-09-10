# Runtime Lifecycle Sequences — Canonical Reference

> Source: PART XVIII — RUNTIME LIFECYCLE SEQUENCES. The authoritative step sequences for boot, the
> detailed voice-command lifecycle, the workflow lifecycle, the plugin lifecycle, and the recovery
> lifecycle. These are the executable procedural truth this system preserves.

## 18.1 Boot Sequence
1. Launcher detects `CATLX_ROOT` from its own executable path.
2. Check for PID lockfile → initiate crash-recovery sequence if a stale PID is found.
3. Hardware Profiler scans CPU, RAM, GPU, storage, network (< 50 ms).
4. Capability Router consumes HardwareProfile → emits CapabilityMap.
5. Core databases opened (SQLite WAL replay if needed).
6. Module Registry scanned → active modules loaded in dependency order.
7. Event Bus WebSocket server started on `:7701`.
8. Security Layer initialized: Credential Vault unsealed, Permission Router loaded.
9. Memory Broker initialized: Episodic, Semantic, and Knowledge Graph stores opened.
10. AI Provider Layer initialized: provider health checks; local model servers started if T1+.
11. Workflow Engine initialized: scheduler started; pending deferred/event workflows registered.
12. Voice Pipeline initialized: wake word model loaded; microphone monitoring started.
13. Plugin Runtime initialized: installed plugins loaded and sandboxed.
14. Electron Shell launched (if GUI mode); HUD overlay rendered.
15. Write new PID lockfile at `/data/runtime/catlx.pid`.
17. Emit `system.ready` event on Event Bus.
18. Restore workspace snapshot → main window layout restored.
19. CATLX operational — voice monitoring active, ready for commands.

## 18.2 Voice Command Lifecycle (Detailed)
1. Wake word matched → Audio Capture begins recording.
2. VAD monitors for end-of-utterance silence (default 800 ms).
3. Audio segment closed and passed to STT Transcriber.
4. STT returns raw text transcript (latency: 200 ms–2 s depending on engine/hardware).
5. Context Manager assembles context window: last 10 turns + active workspace + knowledge graph neighborhood.
6. Context + transcript sent to NLU Intent Parser via Provider Abstraction Layer.
7. NLU returns `IntentObject` `{action_type, entities, confidence, ambiguity_flags, suggested_plan}`.
8. If confidence < 0.75 or ambiguity flags set: Disambiguation Engine generates a clarifying question; TTS speaks it; repeat from step 1 (of this lifecycle).
9. Confirmed intent passed to Workflow Planner.
10. Workflow Planner generates ExecutionPlan (DAG) from intent + available modules + CapabilityMap.
11. ExecutionPlan validated by Permission Router (capability check for each step).
12. DAG Executor begins execution; parallel steps dispatched to the thread pool.
13. Each completed step: checkpoint written; TTS announces progress (T1+); HUD updated.
14. All steps complete: TTS speaks final result; HUD shows completion banner.
15. Memory Broker writes EpisodicRecord with full provenance metadata.
16. Voice pipeline returns to wake-word monitoring state.

## 18.3 Workflow Lifecycle
1. Workflow definition loaded from YAML DSL or constructed dynamically by Workflow Planner.
2. DAG parsed and validated: no cycles, all dependencies present, all modules available.
3. Execution context created: unique run ID, input parameters snapshot, rollback log initialized.
4. Scheduler queues workflow for execution (immediate / deferred / event trigger).
5. At execution time: root nodes (no dependencies) dispatched first.
6. Each node: module invoked via Module Registry → Plugin Runtime / local worker / Docker container.
7. On node completion: output stored in execution context; dependent nodes unlocked.
8. On node failure: retry policy evaluated; if retries exhausted, workflow transitions to FAILED state.
9. If FAILED: rollback offered; compensating transactions executed in reverse order if accepted.
10. If all nodes complete successfully: workflow transitions to COMPLETED state.
11. Completion event emitted on Event Bus → TTS feedback → HUD notification → EpisodicRecord written.
12. Workflow run record archived in `workflows.db`.

## 18.4 Plugin Lifecycle
1. Plugin package received (marketplace install or local file).
2. Signature verification against developer public key.
3. Manifest parsed: declared capabilities, dependencies, API version target.
4. User presented with capability grant review dialog.
5. User approves/rejects each capability; grants stored in `plugins.db`.
6. Dependencies resolved and vendored into the plugin directory.
7. Plugin compiled/validated by Plugin Builder.
8. Plugin registered in Plugin Registry.
9. Plugin loaded into Plugin Runtime sandbox.
10. Plugin's `initialize()` lifecycle method called.
11. Plugin capabilities registered with Capability Router.
12. Plugin available for use in workflows and voice commands.
13. On update: new version downloaded; hot-swap if hot-reload enabled; else restart-required flag set.
14. On uninstall: plugin's `cleanup()` method called; capabilities deregistered; sandbox destroyed; files removed.

## 18.5 Recovery Lifecycle
1. Crash detected via stale PID lockfile on startup.
2. Recovery Mode flag set; Safe Mode UI shown.
3. WAL journals replayed for all SQLite databases.
4. Workspace snapshot loaded: last known window layout and task state.
5. Interrupted workflows identified in `workflows.db` (state = `RUNNING`).
6. For each interrupted workflow: checkpoint integrity verified (hash check).
7. User presented with recovery summary and options: **Resume / Rollback / Ignore**.
8. On Resume: workflow DAG Executor restarts from the last validated checkpoint.
9. On Rollback: compensating transactions applied in reverse order.
10. On Ignore: workflow marked CANCELLED in `workflows.db`.
11. Recovery complete; Recovery Mode flag cleared; normal boot sequence continues.

## Cross-references
- Consumed by: `skills/catlx-runtime-lifecycle/SKILL.md` and the per-subsystem skills.
- Delegates to: `catlx-recovery`, `catlx-voice-pipeline`, `catlx-workflow-engine`, `catlx-plugin-ecosystem`, `catlx-electron-shell`, `catlx-security`.
