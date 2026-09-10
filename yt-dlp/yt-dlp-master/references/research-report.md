# Research report — 2026-09-10

## Current upstream
The current official repository/release stream was reviewed, including releases through 2026.03.13. yt-dlp is a version-sensitive extractor/downloader with thousands of dynamically loaded extractors; the installed executable—not a copied site list—is authoritative. A February 2026 release fixed CVE-2026-26331 involving `--netrc-cmd`; this skill never generates that option.

The current CLI covers URL and batch input, playlists/channels/search prefixes where extractors support them, selection/filtering, output templates, archives, retries/fragments, proxies/headers/IP families, simulation/printing/JSON, format/subtitle/thumbnail listing, cookie/netrc authentication, external downloaders, FFmpeg post-processing, SponsorBlock, metadata parsing, chapters, plugins, extractor arguments, aliases/configuration, self-update/update channels and Python embedding.

## Environment audited here
- Host: Debian 13 x86_64 sandbox, **not the user's Windows machine**.
- `yt-dlp`: not installed; no executable or Python module.
- FFmpeg/FFprobe: not installed.
- Python: 3.13.14.
- Git: 2.47.3.
- PowerShell: unavailable.
- yt-dlp config/plugin locations checked safely: absent.
- Proxy variable names checked without values: none detected.

Consequently no media download, extractor, live-site, cookie, or FFmpeg integration was falsely claimed as executed. The runtime discovery script will re-audit the actual Windows host when installed there.

## Architecture
Natural-language intent is converted by the agent into a JSON request. `discover` dynamically selects the executable and parses installed `--help` to detect options. `plan` builds an argv array, dependency list, redacted review, expected writes/network effects, and SHA-256 digest. The user approves that exact digest. `execute` verifies the unchanged plan, approval digest and dependencies, then uses `subprocess.run(..., shell=False)`. Results are structured; secrets are removed from displayed command arguments.

## Key technical findings
- Current default behavior generally prefers separate best video/audio and needs FFmpeg to merge when applicable. Format selectors (`-f`) filter/compose streams; format sorting (`-S`) expresses preferences such as resolution, codec, filesize and protocol.
- `--list-formats`, `--list-subs`, JSON dumping, printing and simulation support inspection. A metadata request can still contact the site but does not write media.
- Audio extraction, merges, remux/recode, subtitle/thumbnail conversion and embedding, chapters, and many fixups require FFmpeg/FFprobe.
- Manual subtitles and automatic captions are distinct and site-dependent. Never assume a language exists before inspection.
- Archives record extractor IDs after successful download and prevent repeats. Archive creation/write is persistent; existing archives must not be deleted or overwritten.
- Browser cookies and cookie files enable legitimate authenticated sessions. They are sensitive; close/locking behavior differs by browser/OS. YouTube password login is not a substitute for cookies. Never bypass DRM/paywalls/authentication.
- Plugins load from `yt_dlp_plugins.extractor` and `.postprocessor` namespace packages across documented plugin locations. Extractor plugins can override built-ins; postprocessors require explicit use. Installation is consequential.
- Windows command safety requires argv execution rather than shell-string interpolation. Forward-slash paths are accepted by many examples, but native paths and Unicode/spaces must remain separate argv elements. `--windows-filenames` improves compatibility; long-path policy remains an OS concern.

## Primary sources
- Official repository/README: https://github.com/yt-dlp/yt-dlp
- Current releases: https://github.com/yt-dlp/yt-dlp/releases
- Installation: https://github.com/yt-dlp/yt-dlp/wiki/Installation
- FAQ/cookies: https://github.com/yt-dlp/yt-dlp/wiki/FAQ
- Extractors/auth notes: https://github.com/yt-dlp/yt-dlp/wiki/Extractors
- Plugins: https://github.com/yt-dlp/yt-dlp#plugins
- Embedding API: https://github.com/yt-dlp/yt-dlp#embedding-yt-dlp
- OpenCode skills: https://opencode.ai/v2/docs/skills
