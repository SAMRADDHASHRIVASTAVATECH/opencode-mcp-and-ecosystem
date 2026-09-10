# Security model
- Two unprivileged stdio MCP processes; no listening network ports.
- All visual operations are registered/allowlisted. No arbitrary shell or Python execution node.
- Artifact outputs stay in the configured store; input roots are explicit.
- External tools use fixed executables, argument arrays, timeout and captured output.
- GUI operations are typed requests for a separate, authorized Live Control Agent.
- `requires_approval` is metadata, not authority: the Live Agent must independently validate approval, bounds, foreground window, owner policy and emergency stop.
- Screens, files, model output, metadata and OCR text are untrusted data.
- Model/tool install is opt-in and should pin versions and verify hashes/licenses.

No software can promise zero possibility of OS failure. This design minimizes risk by excluding kernel components and unsupported injection, using documented user-mode boundaries, least privilege, timeouts and fail-closed delegation.
