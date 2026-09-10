# Interoperation contract

Universal Artist creates `visual.request/1` envelopes with `visual_compute_request`. OpenCode routes them to Universal Graphics/Vision MCP. Resulting artifact IDs are added to project state or passed into critique/application steps.

For live desktop work, Artist creates `live-control.action/1` envelopes. A separate Windows Live Control Agent independently validates approval, foreground application, DPI/canvas transform, safe bounds and emergency stop, executes the action, then returns observations. Artist evaluates observations and plans corrections.

Neither peer imports the other's code or shares its database.
