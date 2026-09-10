---
name: media-master
description: Safely inspect and transform local media through the media-master MCP using capability checks, exact plans, approval, bounded jobs, and output verification.
---
# Media Master
1. Call `get_media_capabilities`; never claim a backend or codec without verification.
2. Keep all files within the configured media root. Call `probe_media` before choosing transformations.
3. Preserve originals by default. Choose a distinct output, appropriate container/codec/quality, dimensions, timing, metadata policy, and Internet requirements.
4. Call `plan_media_operation`. Review exact input/output, backend argv, overwrite status, network activity, persistent effects, data-loss risks, and verification.
5. Explain consequential effects and obtain explicit user approval. Then call `approve_media_operation` and immediately `execute_media_operation` with the token.
6. Poll `get_media_job`. An exit code alone is insufficient: call `probe_media` on output and compare duration, streams, dimensions, codec, size, and usability against intent.
7. Use `cancel_media_job` only with explicit cancellation confirmation.

For downloads, confirm authorization and rights, use HTTPS, never bypass DRM/authentication/paywalls/geographic controls, and disclose network use. If yt-dlp is absent, report download as unavailable. Never invent MCP tools or use a host shell fallback.
