# Test report — 2026-09-10

Executed in the clean Debian sandbox:
- 12/12 unit and CLI mock tests passed.
- Python syntax compilation passed.
- Package/frontmatter/config JSON validation passed.
- Dynamic environment discovery executed and accurately reported yt-dlp/FFmpeg absence.
- Playlist plan generated with format, subtitles, metadata, archive, retries, dependencies and exact approval digest.

Tested: executable/dependency/config discovery structure; format construction; audio/metadata/playlist planning; archive/subtitle logic; secret redaction; exact approval and plan-tamper rejection; Windows path argument preservation; diagnostics; arbitrary `--exec` exclusion; CLI JSON output.

Not performed or claimed: real downloads, extractor/site calls, authentication/cookie access, FFmpeg processing, live recording, Windows execution, proxy use, updates, installs or configuration writes. These require the user's authorized physical environment.
