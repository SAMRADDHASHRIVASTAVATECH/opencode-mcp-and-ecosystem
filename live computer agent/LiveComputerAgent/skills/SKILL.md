---
name: live-windows-computer-agent
description: Persistent, interruptible Windows perception and control through MCP; use only when GUI interaction is necessary.
---
# Live Windows Computer Agent

## Purpose and division of labor
OpenCode remains the high-level orchestrator: it researches, reads/writes workspace files, reasons, and chooses goals. This skill delegates only physical Windows GUI observation and interaction to the persistent Live Computer Agent. Do not replace file APIs, shell tools, browser APIs, or application-native automation with GUI clicks when a safer structured tool exists.

## Safety invariant
Before any action, know the target application, active window, and expected result. Never enter credentials, approve purchases, send messages, delete data, change security settings, or perform irreversible actions without explicit user confirmation at the consequential step. Never bypass access controls, anti-cheat, elevation boundaries, or OS security. The user can press Ctrl+Alt+Pause to stop independently of reasoning. STOP releases held inputs.

## Session protocol
1. Call `start_live_session` once. The capture/perception loops persist independently of MCP calls.
2. Call `get_active_window` and `get_screen_state`. Confirm the expected application and focus.
3. Prefer structured UIA elements. Use OCR elements next. Request `get_screen(include_image=true)` only when structure is insufficient.
4. Form one bounded action with a postcondition. Prefer `click_element` over coordinates and direct UIA semantics where available.
5. Execute once, inspect status/evidence, and re-observe if uncertain.
6. Continue from the new revision. Stop the live session when no further GUI work is needed.

## Certainty
Element confidence and source matter. UIA is usually stronger than OCR, but neither guarantees current state. A stale frame, mismatched title, missing element, or `uncertain` result requires re-observation—not repetition. Never describe an action as successful unless a postcondition or independent state change supports it.

## Modes
- Direct: exact bounded command such as Ctrl+L. Use individual action tools.
- Assisted: OpenCode decomposes a short goal and calls verified actions.
- Autonomous: call `computer_agent(..., autonomous=true)` only when a configured planner exists, the scope is bounded, and the user approved autonomous control. Monitor `get_agent_state`; cap timeout and steps.

## Goal formulation
Good goals identify application, desired observable end state, boundaries, and stop condition: “In Notepad, enter this text in the current blank document; do not save; stop when the text is visible.” Avoid open-ended “clean my computer.”

## Selection strategy
- Reuse an exact element ID from the newest revision.
- If searching by name, ensure the match is unique and its role fits.
- For coordinates, ensure they lie inside the current captured desktop/window and derive them from the latest frame.
- Focus the intended window before typing.
- Do not type secrets through logs or tool arguments.

## Verification strategy
Choose observable predicates: element appears/disappears, title contains text, window focus changes, or screen changes. Screen change alone is weak evidence; for consequential steps inspect the resulting elements/text. If failed: re-observe, classify focus/element/perception/application failure, modify the plan once, then ask the user rather than looping.

## Interruption and handoff
`pause_live_session` releases input and freezes active operation while preserving state. `resume_live_session` continues. `stop_autonomous_mode` cancels the goal but retains live perception. `stop_live_session` is the safe final state. If the user takes over, pause immediately and re-observe before resuming.

## OpenCode coordination
Use workspace/shell/research MCPs for data and reasoning. Use this MCP only for Windows state/action. Return structured action results to OpenCode, which decides the next subgoal. The Windows runtime may use an OpenAI-compatible local/remote planner only for autonomous mode; it must not recursively invoke arbitrary OpenCode tools. Cross-agent work is coordinated through goal/result MCP calls and the shared session state, not by merging both loops.

## Example workflow
For “Open the browser, find the file, and upload it”: use structured browser/file APIs if available. Otherwise start; identify/focus browser; inspect UI; navigate with bounded verified steps; invoke file picker; inspect its separate window; locate the exact file; select; verify filename; request confirmation if upload is consequential; click upload; verify completion indicator; stop. Never infer upload success from the click alone.
