# Skill: antigravity-last-resort

# Antigravity — Final Escalation Layer (Last-Resort Specialist)

**Antigravity is the FINAL escalation stage, not the primary worker.** It is a native background
fallback inside the CATLX/OpenCode system, invoked automatically only when the system has sufficient
evidence that its own complete capabilities are genuinely insufficient.

Router target aliases: antigravity, agy, last resort, escalation, external agent, fallback agent,
escalate this, advanced reasoning, final escalation layer.

Base directory: `C:\Users\HP\.config\opencode\catlx-skill-system\skills\antigravity-last-resort`
Wrapper: `scripts\ag.py` (availability check, headless run, result envelope). Run with `py`.

---

## 1. Non-negotiable priority order

CATLX's complete native capabilities **must always** be given the first opportunity to solve a task
independently. Do NOT delegate merely because a task is large, interesting, or somewhat difficult.

```
1. CATLX native capabilities (all skills, MCP, web research, search operators, crawling,
   document/PDF processing, browser, local models, verification, reasoning, etc.)
2. Deeper internal reasoning / research / intelligent skill+tool combinations
3. Retries / refinement of approach / investigation of missing information / verification
4. ONLY then, if genuinely necessary: Antigravity (agy) as the last resort
5. CATLX critically evaluates, verifies, and integrates the returned result
6. CATLX remains responsible for the final answer
```

Before escalating, CATLX must have: combined multiple skills/tools, retried or refined the approach
when appropriate, investigated missing information, and made a genuine effort to verify results.

## 2. When escalation is justified (sufficient evidence)

Escalate automatically (without the user requesting it) only when at least one of these is true:

- The task is genuinely beyond CATLX's effective capabilities after native attempts.
- The task requires substantially stronger reasoning than the available system provides
  (e.g., deep multi-file architectural reasoning the local stack has repeatedly failed on).
- Repeated, consistent failures remain despite reasonable approaches and retries.
- An external advanced agent would materially benefit the task AFTER internal capabilities
  have been exhausted.

## 3. What is sent to Antigravity

Send ONLY the specific unresolved problem or subtask, together with:

- necessary context (task, workspace, constraints, prior approaches tried)
- relevant findings already produced by CATLX (do not discard work)
- the specific deliverable/format requested

**Never blindly restart the entire task.** Antigravity receives a focused escalation, not a blank slate.

## 4. Invocation (via wrapper)

```powershell
# 1. Counterfactual/availability check (no side effects)
py "<skill>\scripts\ag.py" check

# 2. Escalate one focused subtask
py "<skill>\scripts\ag.py" escalate "<focused problem + context + constraints + findings>" `
    --timeout 300 [--model <slug>] [--effort high] [--agent <name>]
```

The wrapper returns a machine-readable JSON envelope:
`status`, `response`, `conversation_id`, `duration_s`, `error` (if any), `question`.
Exit code `0` = SUCCESS, `4` = run failure, `3` = unavailable.

Reference: `knowledge\antigravity-cli.md` documents the `agy` headless flags in detail.

## 5. Integration of the returned result

After Antigravity returns, CATLX MUST:

1. **Critically evaluate** the result (does it answer the subtask? is it consistent with prior findings?).
2. **Verify** where possible (run checks, re-run relevant portions of its own toolchain).
3. **Integrate** the validated result into the ongoing workflow.
4. **Remain responsible for the final answer.** Antigravity output is input to CATLX's decision-making,
   not the final word.

## 6. Graceful degradation

If Antigravity is unavailable, fails, times out, or returns an inadequate result:

- Continue gracefully using CATLX's own capabilities.
- Clearly report the remaining limitation in the final answer.
- Do NOT fabricate an Antigravity result. `status: UNAVAILABLE/FAILED/TIMEOUT` is an honest report.

## 7. Transparency

When an escalation happens, mention it briefly in the final response (one line, internal detail level),
e.g. "escalated the X subtask to Antigravity as last resort; validated and integrated the result."
Do not dump raw Antigravity logs into user-facing output by default.

## Source / provenance

- Derived integration skill for the CATLX/OpenCode system. Underlying tool: Google Antigravity CLI
  (`agy`), headless `-p/--print` mode with `--output-format json` and `--print-timeout`.
- The last-resort routing policy is native agent behavior defined in `AGENTS.md`.