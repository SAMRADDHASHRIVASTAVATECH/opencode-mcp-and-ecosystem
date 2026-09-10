# Operational reference

## Inspection
- Capabilities: `python scripts/yt_dlp_master.py discover`
- Formats: plan operation `formats`, equivalent to installed `--list-formats --simulate`.
- Metadata: operation `metadata` uses `--dump-single-json --skip-download`; output may contain private metadata and must be handled carefully.
- Subtitles/thumbnails: first inspect with installed `--list-subs` / `--list-thumbnails` when selection matters.
- Playlist estimate: use `--flat-playlist --dump-single-json` or print selected fields before bulk download.

## Format strategy
- Best quality: installed default or `bv*+ba/b`; FFmpeg may be needed.
- Up to 1080p: prefer `-S res:1080` for ranking or a filtered fallback expression when hard limits are required.
- MP4 preference: `bv*[ext=mp4]+ba[ext=m4a]/b[ext=mp4]/bv*+ba/b`, then `--merge-output-format mp4`; codec/container compatibility still determines result.
- Size limits are estimates when `filesize` is unavailable; `filesize_approx` may differ.
- Device compatibility: ask for device/container/codec limits; don't equate MP4 container with H.264.

## Playlists/channels
Inspect count and sample metadata first for large scopes. Use playlist-aware template, archive, range/items/date/match filters, retries, and failure summary. A channel URL may expose tabs/playlists differently by extractor; inspect before choosing scope.

## Authentication
Use `--cookies-from-browser BROWSER[:PROFILE...]` or `--cookies FILE` only after explicit approval. Never echo cookie contents. Avoid username/password unless the extractor officially supports it. OAuth/device flows are extractor-specific. Custom headers may carry secrets and must be redacted.

## Configuration
yt-dlp loads portable, home, user and system configs in documented precedence. Use `--ignore-config` for controlled diagnosis. Before creating/modifying config: show path, redacted diff, persistence and effect; approve; write atomically; verify with `--verbose` while redacting output. Never parse or display cookie/header/password values.

## Updates
Detect installation type first. Standalone official binaries can generally use `-U`/`--update-to`; pip installs should update with the same Python environment; package-manager installs should use that manager. Show current/target channel/version and executable, ask approval, update, then verify `--version`. Do not blindly self-update managed installations.

## Failure layers
Unsupported URL/extractor; stale version; authentication/availability/DRM; JavaScript challenge/runtime; HTTP/network/proxy/rate limit; selected format absent; FFmpeg/FFprobe; filesystem/path/space; archive/filter skip; live/upcoming state. Retry only transient network/extractor errors, not authentication, DRM, invalid paths or unsupported URLs.
