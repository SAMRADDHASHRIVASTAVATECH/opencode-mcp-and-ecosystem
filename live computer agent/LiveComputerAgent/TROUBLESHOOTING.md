# Troubleshooting
- Black frame: switch `capture_backend` to `mss`; disable exclusive fullscreen; protected content cannot be captured.
- Empty UI tree: application may not expose UIA; enable accessibility flags where supported and use OCR/image state.
- OCR empty: verify `tesseract --version` in the same environment; enlarge UI scaling or add preprocessing provider.
- Click not accepted: confirm active window, same privilege/integrity level, and coordinates. Do not retry blindly.
- Focus denied: Windows foreground-stealing rules may block the request; activate manually once.
- Elevated target: run both at the same integrity only if appropriate; prefer not elevating the agent.
- Stuck input: Ctrl+Alt+Pause, move pointer to PyAutoGUI failsafe corner, or stop the process. Engine cleanup releases tracked keys.
- MCP does not appear: use an absolute launcher path and inspect OpenCode's MCP logs; run `launch-mcp.ps1` manually.
