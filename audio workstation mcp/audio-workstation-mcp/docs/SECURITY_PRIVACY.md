# Security, privacy and approval
Audio stays local. No cloud client or network upload exists. Logs must contain control metadata only, never raw audio or spoken content. Reference audio requires explicit rights confirmation. Model files are not downloaded or deserialized automatically; unsafe pickle checkpoints are a code-execution risk.

Starting capture, routing, playback, profile/reference changes and persistence require exact approval. Approval expires after 60 seconds and is single-use. The system never silently starts a microphone or auto-reconnects after a failure. Use only voices/audio you have rights and consent to process; do not impersonate people deceptively.
