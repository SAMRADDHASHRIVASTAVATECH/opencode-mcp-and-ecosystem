# Media Master MCP
A security-conscious local stdio MCP for media discovery, probing, image processing, video/audio workflows, and authorized HTTPS downloads. It exposes only operations supported by dynamically detected backends: FFmpeg/FFprobe, ImageMagick, ExifTool, and yt-dlp.

## Install
```bash
npm install
npm run build
node lib/index.js
```
The media root defaults to the server working directory. Set `MEDIA_MCP_ROOT` to a dedicated media directory. Inputs and outputs outside it are rejected.

OpenCode configuration:
```json
{"mcp":{"media-master":{"type":"local","command":["node","/absolute/path/media-master-mcp/lib/index.js"],"environment":{"MEDIA_MCP_ROOT":"/absolute/media/workspace"}}}}
```

Workflow: discover → probe → plan → inspect and approve → execute → poll job → independently probe output. All mutations require a short-lived exact-plan approval. No arbitrary shell command is exposed; subprocesses use argv with `shell:false`.

Downloading is available only when yt-dlp is installed, only for HTTPS, and only for content the user is authorized to retrieve. The MCP does not bypass DRM, authentication, paywalls, geographic controls, or site protections.
