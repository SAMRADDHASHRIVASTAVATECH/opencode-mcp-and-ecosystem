# OpenCode import
Run the platform installer. It creates `opencode.generated.json` with correct absolute paths. Either place that file at the root of the project where OpenCode is launched, or merge its `mcp` and `instructions` members into your existing OpenCode configuration. The person MCP is enabled. The physical computer-use MCP is deliberately disabled until separately installed, permission-reviewed, and explicitly enabled.

Normal sequence: `start_person` → `talk`/`set_goal` → `approve_goal` → use structured OpenCode tools → if GUI is essential, `propose_computer_action` → show approval → `decide_action` → call the separate computer-use MCP → verify → `record_experience`.
