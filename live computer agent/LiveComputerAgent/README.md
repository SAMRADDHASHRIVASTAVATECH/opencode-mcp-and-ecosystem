# LiveComputerAgent

A persistent Windows desktop-awareness and control runtime exposed to OpenCode through MCP. It continuously captures screen state on a background thread, fuses foreground-window metadata, Microsoft UI Automation and OCR, accepts bounded actions, verifies effects, tracks session state, and supports direct, assisted and autonomous modes.

## What was actually present before this build
Workspace inspection found one artifact only: `../universal-game-agent-feasibility-study.pdf`. There was no pre-existing agent source, MCP server, skill registry, configuration, or executable implementation to integrate. The PDF specifies a universal orchestration/control architecture; it remains unchanged and is treated as design input. “Existing workspace agent” therefore means OpenCode/Arena's external reasoning and workspace tools, not source code available for linking. This package integrates at the supported boundary: MCP over stdio and structured session state. It does not duplicate OpenCode research, shell, or file tools.

## Quick start (Windows 10/11)
Run `install.ps1`, review `config/default.json`, then `launch-mcp.ps1`. Add the OpenCode MCP entry from `opencode.json.example`. Start a session before actions. Ctrl+Alt+Pause is the independent emergency stop.

## Architecture
OpenCode owns reasoning, research and workspace operations. LiveComputerAgent owns real-time capture, UIA/OCR perception, Windows focus and input. The shared boundary is a typed MCP API and runtime session state. A capture thread operates at `capture_fps`; hybrid perception runs at `perception_fps`; autonomous planning is a separate bounded thread and is disabled unless a provider is configured.

Capture selection is DXcam (DXGI Desktop Duplication) on Windows, MSS fallback, synthetic only for non-Windows tests. Window metadata uses pywin32. UI structure uses pywinauto's UIA backend. OCR uses pytesseract when a separately installed Tesseract executable is available. Input uses PyAutoGUI, which uses native Windows input facilities and has corner failsafe protection. Accessibility-first element targeting avoids coordinate calculation where possible.

## MCP surface
Lifecycle: `start_live_session`, `pause_live_session`, `resume_live_session`, `stop_live_session`.
Observation: `get_screen`, `get_screen_state`, `observe_screen`, `analyze_screen`, `read_screen`, `get_active_window`, `list_windows`.
Input: `click`, `double_click`, `click_element`, `move_mouse`, `drag`, `scroll`, `press_key`, `release_key`, `hotkey`, `type_text`.
Windows: `focus_window`, `switch_window`, `open_application` (disabled by default).
State/goals: `get_agent_state`, `get_current_goal`, `set_goal`, `cancel_goal`, `execute_action`, `verify_action`, `start_autonomous_mode`, `stop_autonomous_mode`.
Master/operations: `computer_agent`, `health_check`.

## Planner configuration
Autonomous mode requires an OpenAI-compatible endpoint:
`LCA_LLM_URL`, `LCA_LLM_MODEL`, and optional `LCA_LLM_API_KEY`. Local endpoints are supported. Without these, direct and OpenCode-orchestrated assisted operation remain fully available; autonomous mode stops honestly instead of fabricating actions.

## Important limitations
This build was created and cross-platform-tested in a Linux sandbox; actual Windows desktop capture/input/UIA could not be physically exercised here. Windows acceptance tests are included and must be run on the target desktop. DXGI cannot capture the secure desktop or DRM-protected surfaces. UIA quality varies by app; elevated apps cannot be controlled by a non-elevated process. Tesseract installation is intentionally not silently downloaded. Verification based only on pixel change is evidence, not semantic proof. Native per-window Windows.Graphics.Capture is an extension point; current optimized path targets monitors via DXcam and crops/uses UIA window bounds.
