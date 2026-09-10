# android_messaging

Agent <-> device messaging channel (§5). action="send": send plain `message` (and/or `structured`) agent->device(s). action="receive": poll device(s)->agent messages since last read. action="ingest": simulate an inbound (device->agent) message for testing.

- kind: `messaging`
- callable: ``android_control.skills.android_messaging``
- master orchestrates: ``android_control``
