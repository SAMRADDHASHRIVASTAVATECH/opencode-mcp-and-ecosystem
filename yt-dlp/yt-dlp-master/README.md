# yt-dlp-master

OpenCode skill plus a functional Python discovery/planning/approval/execution utility for yt-dlp.

## Install
Copy the complete directory to either:
- Project: `.opencode/skills/yt-dlp-master/`
- Global: `~/.config/opencode/skills/yt-dlp-master/`

OpenCode requires uppercase `SKILL.md`; the requested `skill.md` is also included. Python 3.10+ is required. Install yt-dlp and FFmpeg separately from official sources only after approval if absent.

## Validate environment
```powershell
py scripts\yt_dlp_master.py discover
```

## Plan and execute
```powershell
py scripts\yt_dlp_master.py plan --request examples\request-playlist.json --out plan.json
# Review the JSON summary and ask the user to approve the exact digest.
py scripts\yt_dlp_master.py execute --plan plan.json --approval <APPROVED_DIGEST>
```

No shell command string is evaluated. A changed plan or wrong digest is rejected. Authentication arguments are redacted in displayed output.

See `references/research-report.md`, `operations.md`, `capability-matrix.md`, and `security.md`.
