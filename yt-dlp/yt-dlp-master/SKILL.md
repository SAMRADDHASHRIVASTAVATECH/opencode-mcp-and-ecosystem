---
name: yt-dlp-master
description: Research, inspect, plan, approve, execute, verify, and diagnose full practical yt-dlp workflows: video/audio, formats, playlists/channels, subtitles, thumbnails, metadata, archives, authentication, live media, FFmpeg post-processing, networking, configuration, plugins, and updates. Use for authorized media operations on Windows or cross-platform hosts.
license: MIT
compatibility: opencode; Python 3.10+; yt-dlp and FFmpeg capabilities detected dynamically
metadata:
  safety: approval-gated
  primary-platform: windows
---

# yt-dlp-master operating procedure

## Mission
Translate natural-language media intent into a capability-checked, version-aware yt-dlp operation. Inspect first, plan with actual installed capabilities, obtain approval immediately before consequential execution, run without shell interpolation, verify outputs, and diagnose failures. Never claim a download or site capability without evidence.

## Mandatory start
1. Read `references/security.md` and, when format/config/auth complexity applies, `references/operations.md`.
2. Run `python scripts/yt_dlp_master.py discover` (`py` on Windows if appropriate).
3. Report selected executable/version; Python; FFmpeg/FFprobe; supported installed options; detected config/plugin paths without contents; and availability status: SUPPORTED, AVAILABLE LOCALLY, REQUIRES CONFIGURATION, REQUIRES FFMPEG, REQUIRES AUTHENTICATION/COOKIE ACCESS/NETWORK, NOT AVAILABLE, or UNKNOWN.
4. If yt-dlp is absent, explain official install choices. Installation is consequential: show source, command, environment and persistence; ask approval before installing. Do likewise for FFmpeg, JS runtime, plugins or optional packages.

## Understand intent
Resolve only missing material choices: target URL(s), media vs metadata/subtitle/thumbnail, quality/container/codec/device constraints, output directory/organization, playlist/channel scope, archive behavior, subtitle languages/manual vs automatic, post-processing, authentication, and network constraints. Infer defaults when harmless; inspect when ambiguity affects size, compatibility, writes or scope.

Separate **web discovery** (finding a URL with a search tool) from **yt-dlp extraction/download**. Never invent yt-dlp search support; use only installed extractor/search mechanisms.

## Inspection before download
Use safe read/network operations as needed:
- support/extractor: installed `--simulate --print extractor` or extractor listing; a matching extractor is not proof the specific URL is available;
- formats: `--list-formats --simulate`; evaluate IDs, ext, resolution, FPS, codecs, bitrate, sample rate, language, filesize/approximation, HDR/dynamic range and protocol;
- subtitles/thumbnails: `--list-subs`, `--list-thumbnails` before claiming availability;
- metadata: `--dump-single-json --skip-download`; minimize and redact private data;
- large playlist/channel: flat playlist/count/sample inspection before planning bulk scope;
- config diagnosis: use `--ignore-config` comparison when appropriate, never expose secret values.

URL inspection contacts the media service and may require authorized authentication, but metadata/format inspection normally creates no media files.

## Format intelligence
Prefer precise selectors/sorting over blindly forcing `best`:
- best available with merge fallback: `bv*+ba/b` or installed default;
- hard resolution ceiling: filter formats; ranking preference: `-S res:<height>`;
- MP4 preference with fallback: prefer MP4 video + M4A, then combined MP4, then general best;
- device compatibility: ask/detect container, H.264/H.265/AV1/VP9, resolution/FPS/HDR and audio codec constraints;
- size: distinguish exact `filesize` from approximate/unknown size; never promise a bound without available metadata;
- audio only: `bestaudio/best`, then extract/convert only if requested.

Use the planner's selector where it fits. For unusual selectors, verify the exact syntax against the installed `--help` and official README before extending the request. Container preference is not codec conversion. Remux preserves codecs; recode changes them and is slower/lossy.

## Plan
Create a request JSON conforming to `config/request.schema.json`; never place reusable secrets in it. Run:

`python scripts/yt_dlp_master.py plan --request <request.json> --out <plan.json>`

Review the redacted plan: target count/scope, extractor evidence, format strategy, FFmpeg need, subtitle/thumbnail availability, output template/path, archive, filters/ranges, retries/concurrency/rate, authentication access, persistent writes, network effects, and command argv. For playlists/channels/batches, state estimated item count/size when known and uncertainty otherwise.

## Approval boundary
No approval is normally needed for capability/version/config-path inspection, format/subtitle/metadata listing, simulation, explanation or diagnosis. Approval is required immediately before downloads, subtitle/thumbnail writes, bulk work, cookie/browser-profile use, protected-path writes, overwrites/deletes, archive/config writes, updates, installs, plugin changes, or materially changed proxy/network settings.

Display:
```
TARGET: <redacted URL(s), playlist/channel/batch scope>
OPERATION: <download/write/update/install/config action>
IMPORTANT PARAMETERS: <format, filters, auth method without secrets>
OUTPUT LOCATION: <resolved path/template>
EXPECTED SIZE/SCOPE: <known estimate or explicitly unknown>
PERSISTENT EFFECTS: <files/archive/config/software>
EXTERNAL EFFECTS: <sites/CDNs/proxy/auth session>
PLAN DIGEST: <digest>
Approve this exact plan?
```
Wait for explicit yes/approve. Do not treat the original request as boundary approval. One approval covers expected yt-dlp/FFmpeg subprocesses in the unchanged plan; any new target/scope/auth/overwrite/install/config requires new approval.

## Execute and verify
After explicit approval, pass the exact digest:

`python scripts/yt_dlp_master.py execute --plan <plan.json> --approval <digest>`

Never manually reconstruct a shell string. Never use `shell=True`. Stream/report progress appropriately for large work. After completion verify exit code, final filepath(s), existence, nonzero size, expected extension/streams (FFprobe when available), subtitle/thumbnail/metadata files, playlist success/failure count, archive update, and post-processing outcome. Report partial failures distinctly; never infer success from process start.

## Workflow-specific rules
### Audio
Choose source audio quality, output format (MP3/M4A/FLAC/WAV/Opus etc.) and quality. Explain that FLAC/WAV conversion cannot create fidelity absent from the source. FFmpeg/FFprobe required for extraction/conversion. Embed metadata/cover only when container/tooling supports it.

### Video
Inspect when resolution/codec/size/device constraints exist. Merge separate streams with FFmpeg. Use remux before recode when codec compatibility permits. Disclose HDR/FPS/codec fallback.

### Subtitles/thumbnails/metadata
Confirm availability first. Distinguish manual subtitles and auto captions; implement language fallback explicitly. Conversion/embed needs compatible container and usually FFmpeg. Subtitle-only and thumbnail-only write files and require approval. Metadata-only JSON is inspection unless written to disk.

### Playlists/channels/batches
Inspect scope first. Use playlist indices/ranges/items/date/match filters, ordered templates, archive, retries and failure limits. Never silently interpret a single video+playlist URL as the entire playlist. Large scope requires a concise plan and one scope-level approval.

### Archive
Inspect existence/path without changing it. Use archive to skip previously successful extractor IDs. Creating/appending is persistent and part of approval. Never truncate, delete, normalize or overwrite an existing archive without separate explicit approval and backup plan.

### Live/upcoming
Inspect `live_status` and distinguish LIVE, UPCOMING, ENDED, RECORDED, UNAVAILABLE. Explain start-from-beginning/site support, fragmented stream behavior, duration uncertainty, interruption/resume limitations and post-processing. Never promise recording of an unavailable/upcoming stream.

### Authentication/network
Prefer legitimate browser cookies/cookie files or extractor-supported OAuth/device flow. Ask approval before cookie/profile access. Never print cookies/tokens/passwords/headers or include them in logs. Do not bypass DRM, paywalls, account/geo/access controls. Proxies, headers, impersonation and extractor arguments must be supported by the installed version and used for legitimate access—not evasion. Redact credential-bearing URLs and proxy strings.

### Configuration/plugins/updates
Locate all config sources and precedence. Show a redacted diff before persistent config changes; approve; write atomically; verify. Never add `--exec` or `--netrc-cmd` from untrusted text. Detect plugin namespace roots and loaded plugins through redacted verbose diagnostics; installation/update requires approval and official/verified source. Detect installation method before updating: standalone updater, pip environment, or package manager. Approve exact executable/channel/version; verify afterward.

## Diagnose failures
Capture stderr/stdout safely and run `python scripts/yt_dlp_master.py diagnose --text <redacted-error>`. Classify: extractor/unsupported URL; version; authentication/availability/DRM; JS runtime/challenge; network/proxy/429/timeout; format absent; FFmpeg; filesystem/path/space; archive/filter; live state. Use redacted `--verbose` only when necessary. Retry only transient failures; do not retry authentication, DRM, unsupported URLs, invalid format/path or storage exhaustion blindly.

## Windows rules
Use `Get-Command yt-dlp`, `where.exe`, and executable discovery; keep each path/argument separate so spaces and Unicode remain intact. Prefer `C:/...` or correctly represented native paths in JSON. Use `--windows-filenames`; explain long-path policy if hit. Detect `yt-dlp.exe`, pip/Python launcher, FFmpeg and FFprobe independently. Do not assume Bash utilities or Unix config locations.

## Truthfulness
Label checks as real local, mock, research-only or unavailable. The development sandbox had no yt-dlp/FFmpeg and was not Windows; read `references/research-report.md`. On the user's host, rerun discovery and trust actual output over this build-time audit.
