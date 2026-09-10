# Runtime
Four live threads implement event dispatch, cognitive pulse/decay, task deadline monitoring, and reflection scheduling. Safety stop is synchronous, revokes all capabilities, checkpoints state and enters SAFE_IDLE. Event backpressure drops only low-priority events when full.
