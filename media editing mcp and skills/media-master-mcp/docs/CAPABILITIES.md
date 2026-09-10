# Capabilities
`get_media_capabilities` is authoritative at runtime.
- FFprobe: stream/container metadata.
- FFmpeg: transcode, trim, audio extraction, thumbnail generation.
- ImageMagick: image probe, conversion, resize, and metadata stripping.
- ExifTool: discovered and reported; mutation is intentionally not exposed in this release.
- yt-dlp: single authorized HTTPS item download; playlists, exec hooks and unrestricted templates are disabled.
Unsupported backends and operations fail explicitly rather than being simulated.
