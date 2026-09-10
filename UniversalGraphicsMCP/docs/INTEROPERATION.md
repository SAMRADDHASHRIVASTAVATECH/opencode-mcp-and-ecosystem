# Interoperation contract

This MCP accepts `visual.request/1` semantics: `operation`, artifact IDs in `inputs`, and `params`. Its results contain artifact metadata and node results. OpenCode—or another orchestrator—calls `execute_visual_graph` and returns resulting artifact IDs to Universal Artist. There is no Python import, shared process, shared database, or hidden direct dependency between the MCPs.

Screen capture is represented by `visual.capture-request/1` and delegated to an approved platform provider. The Graphics MCP analyzes imported frames; it does not inject input.
