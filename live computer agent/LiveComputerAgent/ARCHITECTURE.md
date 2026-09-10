# Combined architecture

## Separation
**OpenCode/existing agent:** high-level reasoning, user dialogue, source/file operations, research, specialized MCPs and skill selection.
**LiveComputerAgent:** durable Windows session, frame acquisition, UIA/OCR, action arbitration, input cleanup, verification, metrics and interruption.
**Shared layer:** MCP contracts plus current `AgentState`, revisioned `ScreenState`, bounded `ActionResult`, goal and in-memory event history.

No giant recursive agent is created. OpenCode calls the Windows MCP when physical GUI work is required. Results return to OpenCode as structured evidence. Optional autonomous planning is contained inside the Windows runtime and can use only its bounded action vocabulary.

## Runtime paths
Fast loop: capture → pixel-change ratio → active window → revision/state publication.
Medium loop: UIA tree + OCR → element fusion → confidence/provenance.
Slow loop: goal → provider returns exactly one normalized action → guard → dispatch → wait → observe → verify → memory.
Reflex path: Ctrl+Alt+Pause → Win32 RegisterHotKey thread → release all held keys → cancel loops → STOPPED. No LLM dependency.

## Technology review/deviations
- Windows Graphics Capture is modern and supports HWND/HMONITOR through interop, but Python integration is complex. DXcam is a maintained MIT Python package using DXGI Desktop Duplication and now offers a WinRT path; it is used for practical low-latency monitor capture. MSS is fallback.
- UI Automation is the correct structured accessibility layer. pywinauto supports Win32/UIA but its public release cadence is conservative; it is isolated behind a provider.
- SendInput is subject to UIPI and never proves acceptance. PyAutoGUI is used as a mature wrapper, focus is checked, every hold is tracked, and verification follows.
- GameInput reads input and is not a universal virtual-controller injector; no virtual gamepad driver is installed.
- MCP is supervisory, never frame transport. Stdio is local by default; continuous frames stay inside the runtime.
- OCR is optional Tesseract; profile/provider replacement can add Windows.Media.Ocr or ONNX scene text.

## Security
Process launching and clipboard are off by default. Allow/deny lists apply to actions. Coordinates are bounded. Focus is required. Memory is volatile and screenshots are not retained by default. No arbitrary shell MCP tool is exposed. No elevation, credential access, anti-cheat bypass, memory inspection or protected-surface workaround exists.

## Extension contracts
Implement `CaptureProvider`, `WindowProvider`, `InputProvider`, `PerceptionProvider`, or `PlannerProvider` in `providers/base.py`, then inject it into `LiveComputerAgent`. Application adapters can add semantic elements/actions without changing the MCP transport.
