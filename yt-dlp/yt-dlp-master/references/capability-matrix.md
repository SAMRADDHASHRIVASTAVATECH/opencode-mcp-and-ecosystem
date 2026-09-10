# Capability matrix

“Implemented” means the planner can build the real CLI operation; availability remains dynamically dependent on installed yt-dlp/extractor/site/account.

| Capability | Supported | Dependency | Tested here |
|---|---|---|---|
| Single downloads | Implemented | yt-dlp, network | Planner/mock only |
| Playlist downloads | Implemented | extractor, network, storage | Planner/mock only |
| Channel downloads | Implemented | extractor, network, storage | Planner/mock only |
| Format selection | Implemented | installed yt-dlp options; URL inspection | Unit tested construction |
| Audio extraction | Implemented | yt-dlp + FFmpeg/FFprobe | Dependency gate tested |
| Video processing | Implemented | FFmpeg/FFprobe | Planner only |
| Subtitles | Implemented | extractor; FFmpeg for convert/embed | Planner only |
| Thumbnails | Implemented | extractor; FFmpeg/AtomicParsley may be needed to embed | Planner only |
| Metadata | Implemented | yt-dlp + network | Planner only |
| Authentication | Supported legitimately | extractor/account | Redaction tested; no login |
| Cookies | Supported legitimately | browser/file authorization | Redaction tested; no cookie access |
| FFmpeg integration | Planned/detected | FFmpeg + FFprobe | Absence detected |
| Archive | Implemented | writable archive path | Arg construction tested |
| Batch downloads | Implemented | batch file + yt-dlp | Planner only |
| Live streams | Delegated to installed extractor | network/site, often FFmpeg | Research only |
| Proxy/network controls | Implemented | supported installed options/proxy | Redaction tested; no proxy call |
| Configuration | Discovery and agent procedure | filesystem permission | Candidate detection tested |
| Updates | Agent procedure + native updater | installation type/network | Research only; no update run |
| Diagnostics | Implemented | none | Unit tested |
| Windows support | Windows-aware argv/paths/discovery | actual Windows host | Unit tests simulated; not physical |
