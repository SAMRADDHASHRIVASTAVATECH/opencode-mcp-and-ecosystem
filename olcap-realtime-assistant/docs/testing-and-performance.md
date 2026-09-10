# Testing & performance

## Automated tests (spec 35)

`python -m unittest discover -s tests` (25 tests). Offline/deterministic; they exercise
the control-plane logic and assert that absent hardware/model capabilities are honestly
reported (never faked).

Covered: default-OFF + no silent activation; mode switching + session creation;
sensor enablement rules; session lifecycle + **restart persistence** + delete; bounded
rolling context (no unbounded growth); screen context; events + interruption; emergency
stop (and that it blocks re-activation); health honesty; interview question
classification (behavioral/coding/technical); answer evaluation; honest "no model"
behaviour; meeting action/decision/question extraction; MCP manifest namespaces + no
unrestricted shell; mode flow; screen-unavailable honesty; audio device listing; practice
and session surfaces.

## End-to-end tests (spec 36–39)

* **36 Workspace E2E**: start workspace → mic/screen active → user speaks → STT → screen
  context → context combine → reason → response → (optional TTS) → tools when authorized
  → session updated. (Requires real mic/screen/model to run live; the plumbing is
  exercised offline via context/analyze/session tests.)
* **37 Interview practice**: question detected/classified → context → assistance →
  follow-up → session evaluated/report.
* **38 Coding practice**: analyze_code → generate_solution (structured fields) →
  explain_solution.
* **39 Workspace test**: combine permitted screen context + voice → guidance, with no
  repeated unnecessary captures.

Live runs of 36/37 need real hardware + a reachable LM Studio model; the assistant reports
exactly what's missing rather than faking them.

## Performance (spec 28, 29)

* Bounded queues and rolling transcripts (context window capped; transcript capped at 2000
  lines) prevent memory leaks and unbounded growth.
* Frame dedup + downscale before inference; capture only on meaningful change.
* Event-driven reasoning with debounce; cancellation on interrupt; response cancellation.
* Mode-specific resource policy: interview prioritises audio/transcript/reasoning;
  workspace prioritises audio/screen-changes/app context. Expensive vision runs only when
  the screen has meaningfully changed.
* Async/worker-friendly provider calls; no CPU/GPU saturation from repeated captures.
* Realtime uses the low-latency model; the stronger model is used only for deeper/complex
  events or explicit requests.
