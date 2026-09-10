# MCP usage
There are 78 discoverable semantic tools grouped by `audio_`, `voice_`, `soundboard_`, `sound_`, `dj_`, `preset_`, and `trigger_` prefixes.

Mutating tools return an exact plan containing action, arguments, current state and impact. Show it to the user, then call `audio_approve_change(plan_id,"approve")`; call `audio_execute_change` with the single-use token within 60 seconds. Execution returns actual readback and live engine verification.

Use `audio_get_capabilities` and `audio_list_devices` first. Use `audio_get_complete_state` and `audio_verify` after changes. Effect specifications use `{type, parameters, enabled}`. Implemented effects: gain, high/low/band-pass filter, peaking/notch/low-shelf/high-shelf parametric EQ, compressor, gate, limiter, distortion/saturation, delay/echo, tremolo and robot modulation.
