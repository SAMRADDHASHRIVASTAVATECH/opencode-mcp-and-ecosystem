# Security model
- Files are confined to canonical `MEDIA_MCP_ROOT`; traversal and NULs are rejected.
- Read-only probing needs no approval. Every output mutation and network download needs exact approval.
- Approval tokens expire in 60 seconds, are single-use, and bind to a stable SHA-256 plan digest.
- No arbitrary executable, flags, shell, scripts, hooks, or yt-dlp post-process commands are accepted.
- Jobs have bounded output and timeout/cancellation. Output existence and size are verified; callers should probe semantics independently.
- Existing outputs are disclosed as overwrite/data-loss risk. Secrets must never be supplied as URLs or parameters.
- ImageMagick policies and codecs remain backend trust boundaries. Process-level resource limits should also be applied by the deployment host for untrusted media.
