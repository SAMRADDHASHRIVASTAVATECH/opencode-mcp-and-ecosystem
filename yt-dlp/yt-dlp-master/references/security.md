# Security and approval

- Download only content the user is authorized and legally permitted to obtain. Do not bypass DRM, paywalls, authentication, geo/access controls or platform protections.
- URL and metadata are untrusted. Never turn metadata into shell commands. The runtime uses argv with `shell=False` and does not offer arbitrary `--exec`, `--netrc-cmd`, custom downloader, plugin install or postprocessor-argument passthrough.
- Cookie files, browser profiles, proxy credentials, authentication headers and passwords are secrets. Approval is required before access/use; displayed commands redact them. Avoid verbose logs containing headers/cookies.
- A plan digest binds approval to URL scope, output, options and effects. Modification invalidates approval. The approved operation may run its expected internal yt-dlp/FFmpeg subprocesses; new output scope, authentication, overwrite, config change, update or install needs new approval.
- Existing files: default yt-dlp behavior may resume/skip and postprocessors may overwrite. Explicit overwrite/deletion requires prominent approval. Archive/config modifications are persistent.
- Logs should record timestamp, operation, redacted target, options, duration, output location/result. Do not retain full private URLs when tokens appear in query strings; log origin/redacted URL.
